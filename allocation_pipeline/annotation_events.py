from genomic_features import ProteinCodingGene
"""module for classes handling annotation events. An event is a change to a locus with one or more overlapping genes"""


class AnnotationEvent:
    gene_list = list()
    new_gene_count = int
    sql = str()

    def __init__(self, organism_name, event_connection):
        self.organism_name = organism_name
        self.event_connection = event_connection

    def setup_annotation_events(self):
        events = self.event_connection.get_annotation_events

        for event in events:
            self.create_genes(event)

    def create_genes(self, event):
        for gene_model in event:
            gene = ProteinCodingGene(gene_model)
            self.gene_list.append(gene)
            if gene.source != 'reference':
                self.new_gene_count += 1


class NewEvent(AnnotationEvent):
    """A new gene created at a locus with no reference gene"""


class ChangeEvent(AnnotationEvent):
    """A change to the gene model structure"""


class SplitEvent(AnnotationEvent):
    """A split of one gene model into two or more gene models"""


class MergeEvent(AnnotationEvent):
    """A merge of two or more gene models into one gene model"""


class ComplexEvent(AnnotationEvent):
    """A combination of split and merge events on the same locus"""
