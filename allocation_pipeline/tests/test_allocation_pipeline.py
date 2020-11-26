import unittest
from allocation_pipeline.annotation_events import EventCollection, AnnotationEvent
from allocation_pipeline.event_output import AnnotationEventFile
from allocation_pipeline.genomic_features import ProteinCodingGene, Feature
from allocation_pipeline.event_output import GFFAnnotations


class OSIDService:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def get_organism_id(organism_name):
        _ = organism_name
        return 1

    @staticmethod
    def get_gene_id(organism_id, generate_genes):
        _ = organism_id

        if generate_genes == 2:
            return 1,  [{"geneId": "ABC00015", "transcripts": [], "proteins": []},
                                      {"geneId": "ABC00016", "transcripts": [], "proteins": []}]
        elif generate_genes == 1:
            return 1, [{"geneId": "ABC00015", "transcripts": [], "proteins": []}]

    @staticmethod
    def get_transcripts(id_set_id, transcript_patch):
        _ = id_set_id
        if len(transcript_patch) == 2:
            return [{"geneId": "ABC00015", "transcripts": ['ABC00015_R001'], "proteins": ['ABC00015_P001']},
                                  {"geneId": "ABC00016", "transcripts": ['ABC00016_R001'], "proteins": ['ABC00016_P001']}]
        elif len(transcript_patch) == 1:
            return [{"geneId": "ABC00015", "transcripts": ['ABC00015_R001'], "proteins": ['ABC00015_P001']}]


class AnnotationEventDB:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    @staticmethod
    def get_annotations_events(event_type):

        if event_type == 'merge_gene':
            events = list()
            ref_model1 = {"source": "reference", "id": "ABCD00001", "children": [{"id": "ABCD00001_R0001", "version": 2,
                                                                              "children": [{"id": "ABCD00001_P0001", "version": 2}]}]}
            ref_model2 = {"source": "reference", "id": "ABCD00002", "children": [{"id": "ABCD00002_R0001", "version": 2,
                                                                              "children": [{"id": "ABCD00002_P0001", "version": 2}]}]}
            merge_model1 = {"source": "apollo", "id": "DFGVE-DHETE", "children": [{"id": "DHEYODH-DHYERS", "version": 2,
                                                                               "children": [{"id": "SGETFKCBW-IUDHET", "version": 2}]}]}
            merge_1 = [ref_model1, ref_model2, merge_model1]
            events.append(merge_1)

            return events
        else:
            return False


class CollectionTestCase(unittest.TestCase):
    def test_create_event_collection(self):
        event_connection = AnnotationEventDB(None)
        stable_id_service = OSIDService(None)
        event_collection = EventCollection('test', event_connection, stable_id_service)
        event_collection.event_types = {'merge_gene'}
        event_collection.create()

        self.assertEqual('ABC00015', event_collection.get_allocated_id('DFGVE-DHETE'))


class EventFileTestCase(unittest.TestCase):

    def test_write_event_file(self):
        event_connection = AnnotationEventDB(None)
        stable_id_service = OSIDService(None)
        event_collection = EventCollection('test', event_connection, stable_id_service)
        event_collection.event_types = {'merge_gene'}
        event_collection.create()

        event_file = AnnotationEventFile(event_collection, 'test_file')
        event_file.write_event_file()
        file_handle = open('./test_file', 'r')
        lines = file_handle.readlines()
        self.assertEqual("ABC00015\tmerge_gene\tABCD00001\n", lines[0])
        self.assertEqual("ABC00015\tmerge_gene\tABCD00002\n", lines[1])
        file_handle.close()


class AnnotationTestCase(unittest.TestCase):
    def test_create_genes(self):
        annotation_event = AnnotationEvent('merge', 'test_organism', None, None)
        index = dict()
        events = list()
        ref_model1 = {"source": "reference", "id": "ABCD00001", "children": [{"id": "ABCD00001_R0001", "version": 2,
                                                                              "children": [{"id": "ABCD00001_P0001", "version": 2}]}]}
        ref_model2 = {"source": "reference", "id": "ABCD00002", "children": [{"id": "ABCD00002_R0001", "version": 2,
                                                                              "children": [{"id": "ABCD00002_P0001", "version": 2}]}]}
        merge_model1 = {"source": "apollo", "id": "DFGVE-DHETE", "children": [{"id": "DHEYODH-DHYERS", "version": 2,
                                                                               "children": [{"id": "SGETFKCBW-IUDHET", "version": 2}]}]}
        merge_1 = [ref_model1, ref_model2, merge_model1]
        events.append(merge_1)
        ref_model3 = {"source": "reference", "id": "ABCD00007", "children": [{"id": "ABCD00007_R0001", "version": 2,
                                                                              "children": [{"id": "ABCD00007_P0001", "version": 2}]}]}
        ref_model4 = {"source": "apollo", "id": "ABCD00008", "children": [{"id": "ABCD00008_R0001", "version": 2,
                                                                           "children": [{"id": "ABCD00008_P0001", "version": 2}]}]}
        merge_model2 = {"source": "apollo", "id": "ABCD00009", "children": [{"id": "ABCD00009_R0001", "version": 2,
                                                                             "children": [{"id": "ABCD00009_P0001", "version": 2}]}]}
        merge_2 = [ref_model3, ref_model4, merge_model2]
        events.append(merge_2)

        genes = annotation_event._create_genes(merge_1, index)

        self.assertEqual(1, annotation_event.new_gene_count, 'new genes created')
        self.assertEqual(3, len(genes), 'object created')
        self.assertEqual(9, len(index), 'features register')
        self.assertEqual('reference', index['ABCD00001'].source)


class FeatureTestCase(unittest.TestCase):
    def test_feature(self):
        index = dict()
        model = {"id": "ABCD00001", "version": 1, "children": [{"id": "ABCD00001_R0001",
                                                                "children": [{"id": "ABCD00001_P0001", "version": 2}]}]}
        feature = Feature(model, index)
        self.assertEqual("ABCD00001", feature.source_id)

    def test_gene(self):
        index = dict()
        model = {"source": "apollo", "id": "ABCD00001", "children": [{"id": "ABCD00001_R0001", "version": 2,
                                                                      "children": [{"id": "ABCD00001_P0001", "version": 2}]}]}
        gene = ProteinCodingGene(model, index)
        self.assertEqual("ABCD00001", gene.source_id)
        self.assertEqual(1, len(gene.mrnas))
        mrna = gene.mrnas[0]
        self.assertEqual("ABCD00001_R0001", mrna.source_id)
        cds = mrna.cds
        self.assertEqual("ABCD00001_P0001", cds.source_id)


class GFFTestCase(unittest.TestCase):
    def test_extract_ids(self):
        ga = GFFAnnotations('', '', '')
        ga._current_gff_line = 'KB704696    VectorBase  mRNA    767281  778992  .   +   .   owner=none;Parent=ABC001_R001;ID=ABC001;date_last_modified=2020-01-09;'
        self.assertEqual(('ABC001', 'ABC001_R001'), ga._extract_ids())

        ga._current_gff_line = 'KB704696        VectorBase      gene    757672  778992  .       +       .       owner=none;ID=ABC001;date_last_modified=2020-01-09;'
        self.assertEqual(('ABC001', None), ga._extract_ids())

        ga._current_gff_line = 'KB704696        VectorBase      CDS     770336  770396  .       +       0       Parent=ABC001_R001;ID=ABC001_R001-CDS;Name='
        self.assertEqual(('ABC001_R001-CDS', 'ABC001_R001'), ga._extract_ids())

    def test_is_feature_line(self):
        ga = GFFAnnotations('', '', '')
        ga._current_gff_line = "KB704696\tVectorBase\tmRNA\t767281\t778992\t.\t+\t.\towner=none;Parent=ABC001_R001;ID=ABC001;date_last_modified=2020-01-09;"
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(True, ga._is_feature_line())

        ga._current_gff_line = 'KB704696\tVectorBase\tgene\t757672\t778992\t.\t+\t.\towner=none;ID=ABC001;date_last_modified=2020-01-09;'
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(True, ga._is_feature_line())

        ga._current_gff_line = 'KB704696\tVectorBase\tCDS\t770336\t770396\t.\t+\t.\tParent=ABC001_R001;ID=ABC001_R001-CDS;Name='
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(True, ga._is_feature_line())

        ga._current_gff_line = 'KB704696\tVectorBase\tXXX\t770336\t770396\t.\t+\t.\tParent=ABC001_R001;ID=ABC001_R001-CDS;Name='
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(False, ga._is_feature_line())


if __name__ == '__main__':
    unittest.main()
