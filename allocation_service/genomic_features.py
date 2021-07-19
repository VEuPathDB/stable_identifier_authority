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

"""module for all genomic feature classes"""


class GenomicFeatureModel:
    """Base class for building feature models i.e gene models in JSON."""

    def __init__(self, allowed_feature=None):
        self.allowed_feature = allowed_feature
        self.features = {"top": {}, "middle": {}, "bottom": {}}

    def add_feature(self, model_layer, gff_id, parent_id=None):

        if model_layer == 'top':
            self.features["top"][gff_id] = {"json": {"source": "community_GFF", "id": gff_id, "children": []}}
        elif model_layer == 'middle':
            self.features["middle"][gff_id] = {"parent": parent_id, "json": {"id": gff_id, "children": []}}
        elif model_layer == 'bottom':
            self.features["bottom"][gff_id] = {"parent": parent_id, "json": {"id": gff_id}}


class Gene(GenomicFeatureModel):
    """Class for the biotype Gene"""
    allowed_feature_type = {'gene': 'top', 'mRNA': 'middle', 'CDS': 'bottom'}

    def __init__(self, allowed_feature=None):
        super().__init__(allowed_feature)

    def add_allowed_feature(self, feature_type, gff_id, parent_id=None):
        if feature_type in Gene.allowed_feature_type:
            super().add_feature(Gene.allowed_feature_type[feature_type], gff_id, parent_id)

    def build_model(self):
        finished_models = list()
        for gff_id, model in self.features["bottom"].items():
            parent_middle_id = model["parent"]
            if parent_middle_id in self.features['middle']:
                self.features["middle"][parent_middle_id]["json"]["children"].append(model["json"])
            else:
                raise KeyError("mRNA id: {} is not found and the CDS {} is orphan".format(parent_middle_id, gff_id))
        for gff_id, model in self.features["middle"].items():
            parent_top_id = model["parent"]
            if parent_top_id in self.features["top"]:
                self.features["top"][parent_top_id]["json"]["children"].append(model["json"])
            else:
                raise KeyError("Gene id: {} is not found and the mRNA {} is orphan".format(parent_top_id, gff_id))
        for gff_id, model in self.features["top"].items():
            if self.allowed_feature is None:
                finished_models.append(model["json"])
            elif gff_id in self.allowed_feature:
                finished_models.append(model["json"])
        return finished_models


class PseudoGene(GenomicFeatureModel):
    """Class for the biotype pseudogene"""
    allowed_feature_type = {'pseudogene': 'top', 'pseudogenic_transcript': 'bottom'}

    def __init__(self, allowed_feature=None):
        super().__init__(allowed_feature)

    def add_allowed_feature(self, feature_type, gff_id, parent_id=None):
        if feature_type in PseudoGene.allowed_feature_type:
            super().add_feature(PseudoGene.allowed_feature_type[feature_type], gff_id, parent_id)

    def build_model(self):
        finished_models = list()
        for gff_id, model in self.features["bottom"].items():
            parent_top_id = model["parent"]
            if parent_top_id in self.features['top']:
                self.features["top"][parent_top_id]["json"]["children"].append(model["json"])
            else:
                raise KeyError("pseudogene id: {} is not found and the pseudogenic_transcript {} is orphan"
                               .format(parent_top_id, gff_id))
        for gff_id, model in self.features["top"].items():
            if self.allowed_feature is None:
                finished_models.append(model["json"])
            elif gff_id in self.allowed_feature:
                finished_models.append(model["json"])
        return finished_models


class NcRnaGene(GenomicFeatureModel):
    """Class for the biotype ncRNA_gene"""
    allowed_feature_type = {'ncRNA_gene': 'top', 'tRNA': 'bottom'}

    def __init__(self, allowed_feature=None):
        super().__init__(allowed_feature)

    def add_allowed_feature(self, feature_type, gff_id, parent_id=None):
        if feature_type in NcRnaGene.allowed_feature_type:
            super().add_feature(NcRnaGene.allowed_feature_type[feature_type], gff_id, parent_id)

    def build_model(self):
        finished_models = list()

        for gff_id, model in self.features["bottom"].items():
            parent_top_id = model["parent"]
            if parent_top_id in self.features['top']:
                self.features["top"][parent_top_id]["json"]["children"].append(model["json"])
            else:
                raise KeyError("ncRNA_gene id: {} is not found and the tRNA {} is orphan".format(parent_top_id, gff_id))
        for gff_id, model in self.features["top"].items():
            if self.allowed_feature is None:
                finished_models.append(model["json"])
            elif gff_id in self.allowed_feature:
                finished_models.append(model["json"])
        return finished_models


class Feature:
    """Base class for genomic features holding stable identifier"""

    def __init__(self, model, index):
        self.source_id = str()
        self.allocated_id = str()
        self.osid_id = int
        self.ancestors = set()
        self.status_flags = set()
        self.known_events = set()
        self.setup_model(model)
        self._register_my_self(index)

    def setup_model(self, model):
        self.source_id = model['id']

    def set_allocated_id(self, identifier):
        self.allocated_id = identifier

    def _register_my_self(self, index):
        index[self.source_id] = self


class ProteinCodingGene(Feature):
        """A gene is a collection of transcripts (mRNAs) and each transcript can have only one coding sequence (CDS)."""

        def __init__(self, model, index):
            super().__init__(model, index)
            self.mrnas = list()
            self.source = model['source']
            self._create_mrna(model['children'], index)

        def _create_mrna(self, model, index):
            for mrna_model in model:
                mrna = MRNA(mrna_model, index)
                mrna.setup_model(mrna_model)
                self.mrnas.append(mrna)

        def update_transcripts(self, transcripts, translations):

            if len(transcripts) != len(self.mrnas):
                return False
            for index, mrna in enumerate(self.mrnas):
                mrna.osid_id = self.osid_id
                mrna.set_allocated_id((transcripts[index], translations[index]))


class MRNA(Feature):
        """A mRNA belongs to one gene, and can have 1 CDS"""

        def __init__(self, model, index):
            super().__init__(model, index)
            self.cds = CDS(model, index)

        def set_allocated_id(self, identifier):
            mrna_id, cds_id = identifier
            self.allocated_id = mrna_id
            self.cds.set_allocated_id(cds_id)


class CDS(Feature):
    """coding sequence"""
    def setup_model(self, model):
        self.source_id = model['id'] + '-CDS'
