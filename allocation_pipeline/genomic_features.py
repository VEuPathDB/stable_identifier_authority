"""module for all genomic feature classes"""


class Feature:
    """Base class for genomic features holding stable identifier and version information"""
    source_id = str()
    version = int
    allocated_id = str()
    ancestors = list()

    def __init__(self, model):
        self.setup_model(model)

    def setup_model(self, model):
        self.source_id = model['id']
        self.version = model['version']


class ProteinCodingGene(Feature):
        """A gene is a collection of transcripts (mRNAs) and each transcript can have only one coding sequence (CDS)."""
        mrnas = list()

        def __init__(self, model):
            super().__init__(model)
            self.source = model['source']
            self._create_mrna(model['children'])

        def _create_mrna(self, model):
            for mrna_model in model:
                mrna = MRNA(mrna_model)
                mrna.setup_model(mrna_model)
                self.mrnas.append(mrna)


class MRNA(Feature):
        """A mRNA belongs to one gene, and can have 1 CDS"""
        cds = object()

        def __init__(self, model):
            super().__init__(model)
            self.cds = CDS(model['children'][0])


class CDS(Feature):
        """coding sequence"""
