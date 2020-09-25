"""module for all genomic feature classes"""


class Feature:
    """Base class for genomic features holding stable identifier"""

    def __init__(self, model, index):
        self.source_id = str()
        self.allocated_id = str()
        self.ancestors = list()
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
                'error'
            for index, mrna in enumerate(self.mrnas):
                mrna.set_allocated_id((transcripts[index], translations[index]))


class MRNA(Feature):
        """A mRNA belongs to one gene, and can have 1 CDS"""

        def __init__(self, model, index):
            super().__init__(model, index)
            self.cds = CDS(model['children'][0], index)

        def set_allocated_id(self, identifier):
            mrna_id, cds_id = identifier
            self.allocated_id = mrna_id
            self.cds.set_allocated_id(cds_id)


class CDS(Feature):
        """coding sequence"""
