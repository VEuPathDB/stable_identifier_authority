import unittest
from annotation_events import EventCollection
from event_output import AnnotationEventFile


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
            return {"generatedIds": [{"geneId": "ABC00015", "transcripts": [], "proteins": []},
                                      {"geneId": "ABC00016", "transcripts": [], "proteins": []}]}
        elif generate_genes == 1:
            return {"generatedIds": [{"geneId": "ABC00015", "transcripts": [], "proteins": []}]}

    @staticmethod
    def get_transcripts(transcript_patch):

        if len(transcript_patch) == 2:
            return {"generatedIds": [{"geneId": "ABC00015", "transcripts": ['ABC00015_R001'], "proteins": ['ABC00015_P001']},
                                  {"geneId": "ABC00016", "transcripts": ['ABC00016_R001'], "proteins": ['ABC00016_P001']}]}
        elif len(transcript_patch) == 1:
            return {"generatedIds": [{"geneId": "ABC00015", "transcripts": ['ABC00015_R001'], "proteins": ['ABC00015_P001']}]}


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
        event_collection.create_event_collection()

        self.assertEqual('ABC00015', event_collection.get_allocated_id('DFGVE-DHETE'))


class EventFileTestCase(unittest.TestCase):

    def test_write_event_file(self):
        event_connection = AnnotationEventDB(None)
        stable_id_service = OSIDService(None)
        event_collection = EventCollection('test', event_connection, stable_id_service)
        event_collection.event_types = {'merge_gene'}
        event_collection.create_event_collection()

        event_file = AnnotationEventFile(event_collection, 'test_file')
        event_file.write_event_file()
        file_handle = open('./test_file', 'r')
        lines = file_handle.readlines()
        self.assertEqual("ABC00015\tmerge_gene\tABCD00001\n", lines[0])
        self.assertEqual("ABC00015\tmerge_gene\tABCD00002\n", lines[1])
        file_handle.close()

if __name__ == '__main__':
    unittest.main()
