import unittest
from annotation_events import AnnotationEvent


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




if __name__ == '__main__':
    unittest.main()
