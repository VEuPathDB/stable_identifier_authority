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
from allocation_service import genomic_features

"""Module for classes getting annotation event from different sources"""


class AnnotationEventDB:

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_annotations_events(self, event_type):
        event_sql = "select vb_gene_id, cap_gene_id from gene_events where events = %s;"
        event_db = self.execute_sql(event_sql, event_type)
        return self.setup_gene_model(event_db, event_type)

    def setup_gene_model(self, event_db, event_type):
        events = list()
        for event in event_db:
            genes = list()
            if event_type == 'new_gene':
                genes.append({"source": "apollo", "id": event['cap_gene_id'], "version": 1,
                              "children": self.add_transcripts(event['cap_gene_id'])})
                events.append(genes)
            elif event_type == 'change_gene' or event_type == 'gain_iso_form' or event_type == 'lost_iso_form':
                genes.append({"source": "reference", "id": event['vb_gene_id'], "version": None,
                              "children": self.add_transcripts(event['vb_gene_id'])})
                genes.append({"source": "apollo", "id": event['cap_gene_id'], "version": None,
                              "children": self.add_transcripts(event['cap_gene_id'])})
                events.append(genes)
            elif event_type == 'split_gene':
                genes.append({"source": "reference", "id": event['vb_gene_id'], "version": None,
                              "children": self.add_transcripts(event['vb_gene_id'])})
                for gene_id in event['cap_gene_id'].split(":"):
                    genes.append({"source": "apollo", "id": gene_id, "version": 1,
                                  "children": self.add_transcripts(gene_id)})
                events.append(genes)
            elif event_type == 'merge_gene':
                genes.append({"source": "apollo", "id": event['cap_gene_id'], "version": 1,
                              "children": self.add_transcripts(event['cap_gene_id'])})
                for gene_id in event['vb_gene_id'].split(":"):
                    genes.append({"source": "reference", "id": gene_id, "version": None,
                                  "children": self.add_transcripts(gene_id)})
                events.append(genes)
        return events

    def add_transcripts(self, gene_id):
        sql = "select distinct(transcript_id) from gene_model where gene_id = %s;"
        transcript_db = self.execute_sql(sql, gene_id)
        transcript_list = list()
        for transcript in transcript_db:
            transcript_list.append({'id': transcript['transcript_id'], "children": [{'id': None}]})
        return transcript_list

    def execute_sql(self, sql, values):

        with self.db_connection.cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.fetchall()


class GffFilePasser:
    """Class for parsing GFF files"""

    def __init__(self, gff_file_path, feature_filter, allowed_biotype):
        self._current_gff_line = None
        self._current_fields = list()
        self._current_feature = None
        self._current_gff_id = None
        self._current_parent_id = None
        self.observers = list()
        self.genes = list()
        self.events = list()
        self.allowed_feature = set()
        self._load_feature_filter(feature_filter)
        self._instantiate_observers(allowed_biotype)
        self._load_events_from_gff(gff_file_path)

    def _instantiate_observers(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                allowed_object = line.rstrip()
                if allowed_object == 'gene':
                    self.observers.append(genomic_features.Gene(allowed_feature=self.allowed_feature))
                elif allowed_object == 'ncRNA_gene':
                    self.observers.append(genomic_features.NcRnaGene(allowed_feature=self.allowed_feature))
                elif allowed_object == 'pseudogene':
                    self.observers.append(genomic_features.PseudoGene(allowed_feature=self.allowed_feature))

    def get_annotations_events(self, event_type):
        if event_type == 'new_gene':
            return self.events
        else:
            return list()  # return empty list

    def _load_feature_filter(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                feature_id = line.rstrip()
                self.allowed_feature.add(feature_id)

    def _load_events_from_gff(self, gff_file_path):
        with open(gff_file_path, 'r') as file:
            for line in file:
                self._current_gff_line = line.rstrip()
                self._current_fields = self._current_gff_line.split("\t")

                if self._is_feature_line():
                    self._current_feature = self._current_fields[2]
                    self._current_gff_id, self._current_parent_id = self._extract_ids()
                    for observer in self.observers:
                        observer.add_allowed_feature(self._current_feature,
                                                     self._current_gff_id, self._current_parent_id)
        for observer in self.observers:
            finished_models = observer.build_model()
            if len(finished_models) > 0:
                self.events.append(finished_models)

    def _is_feature_line(self):
        if len(self._current_fields) == 9:
            return True
        else:
            return False

    def _extract_ids(self):
        """
        Extract the ID and Parent of the current gff feature
        """

        gff_id = None
        parent = None
        try:
            attribs = self._extract_attribs()
            if "ID" in attribs:
                gff_id = attribs["ID"]
            if "Parent" in attribs:
                parent = attribs["Parent"]
        except:
            pass

        return gff_id, parent

    def _extract_attribs(self):
        """
        Extract the attribs from the gff feature line
        Returns a dict of attribs with their key
        """
        attrib_col = self._current_fields[8]
        
        attribs = {}
        for field in attrib_col.split(";"):
            if field:
                (key, value) = field.split("=")
                attribs[key] = value
        
        return attribs
    
