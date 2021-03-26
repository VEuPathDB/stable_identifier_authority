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