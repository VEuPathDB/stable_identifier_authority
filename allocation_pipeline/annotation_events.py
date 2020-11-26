"""
Copyright [2019-2020] EMBL-European Bioinformatics Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from allocation_pipeline.genomic_features import ProteinCodingGene
"""module for classes handling annotation events. An event is a change to a locus with one or more overlapping genes"""


class EventCollection:
    event_types = {'new_gene', 'change_gene', 'split_gene', 'merge_gene'}

    def __init__(self, organism_name, event_connection, stable_id_service):
        self.organism_name = organism_name
        self.event_connection = event_connection
        self.stable_id_service = stable_id_service
        self.annotation_event_list = list()
        self.feature_index = dict()

    def create(self):
        for event_type in self.event_types:
            if event_type == 'change_gene':
                annotation_event = EditOnlyEvent(event_type, self.organism_name,
                                                 self.event_connection, self.stable_id_service)
            else:
                annotation_event = CreateGeneModelEvent(event_type, self.organism_name,
                                                        self.event_connection, self.stable_id_service)

            annotation_event.setup(self.feature_index)
            annotation_event.get_new_stable_ids()
            annotation_event.update_ancestors()
            self.annotation_event_list.append(annotation_event)

    def get_allocated_id(self, source_id):
        try:
            gene = self.feature_index[source_id]
            return gene.allocated_id
        except KeyError:
            return None


class AnnotationEvent:
    def __init__(self, event_type, organism_name, event_connection, stable_id_service):
        self.event_list = list()
        self.created_genes = list()
        self.gene_event_index = dict()
        self.allocated_index = dict()
        self.new_gene_count = int()
        self.event_type = event_type
        self.organism_name = organism_name
        self.event_connection = event_connection
        self.stable_id_service = stable_id_service

    def setup(self, index):
        events = self.event_connection.get_annotations_events(self.event_type)

        for event in events:
            genes_in_event = self._create_genes(event, index)
            self.event_list.append(genes_in_event)

    def _create_genes(self, event, index):
        genes = list()
        for gene_model in event:
            gene = ProteinCodingGene(gene_model, index)
            genes.append(gene)
            self.gene_event_index[gene.source_id] = genes

            if gene.source != 'reference':
                self.new_gene_count += 1
                self.created_genes.append(gene)
        return genes

    def _allocate_to_gene(self, osid_id, gene_id):
        for gene in self.created_genes:
            if not gene.allocated_id:
                gene.osid_id = osid_id
                gene.allocated_id = gene_id
                self.allocated_index[gene_id] = gene
                return len(gene.mrnas)

    def _allocate_to_transcript(self, gene_model):
        for gene_info in gene_model:
            allocated_id = gene_info['geneId']
            gene = self.allocated_index[allocated_id]
            gene.update_transcripts(gene_info['transcripts'], gene_info['proteins'])

    def update_ancestors(self):
        for event in self.event_list:
            ancestors = list()
            for gene in event:
                if gene.source == 'reference':
                    ancestors.append(gene)
            for gene in event:
                if gene.source != 'reference':
                    gene.ancestors = ancestors


class CreateGeneModelEvent(AnnotationEvent):
    """A new gene model created at a locus with no reference gene"""
    """A split of one gene model into two or more gene models"""
    """A merge of two or more gene models into one gene model"""

    def get_new_stable_ids(self):
        organism_id = self.stable_id_service.get_organism_id(self.organism_name)
        id_set_id, generated_genes = self.stable_id_service.get_gene_id(organism_id, self.new_gene_count)
        transcript_patch = list()
        for gene in generated_genes:
            gene_id = gene['geneId']
            transcript_number = self._allocate_to_gene(id_set_id, gene_id)
            transcript_patch.append({'geneId': gene_id, 'transcripts': transcript_number})
        requested_id = self.stable_id_service.get_transcripts(id_set_id, transcript_patch)
        self._allocate_to_transcript(requested_id)


class EditOnlyEvent(AnnotationEvent):
    """A change to the gene model structure"""
    def get_new_stable_ids(self):
        organism_id = self.stable_id_service.get_organism_id(self.organism_name)
        id_set_id, _ = self.stable_id_service.get_gene_id(organism_id, 0)
        reference_gene = None
        for created_gene in self.created_genes:
            event = self.gene_event_index[created_gene.source_id]
            for gene in event:
                if gene.source == 'reference':
                    reference_gene = gene
            created_gene.osid_id = id_set_id
            created_gene.allocated_id = reference_gene.source_id
            transcript_number = len(created_gene.mrnas)
            transcript_patch = list()
            transcript_patch.append({'geneId': created_gene.allocated_id, 'transcripts': transcript_number})
            gene_model = self.stable_id_service.get_transcripts(id_set_id, transcript_patch)
            created_gene.update_transcripts(gene_model[0]['transcripts'], gene_model[0]['proteins'])
