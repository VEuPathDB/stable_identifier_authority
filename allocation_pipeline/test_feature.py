import unittest
import genomic_features


class MyTestCase(unittest.TestCase):
    def test_feature(self):
        model = {"id": "ABCD00001", "version": 1, "children": [{"id": "ABCD00001_R0001", "version": 2,
                                                                "children": [{"id": "ABCD00001_P0001", "version": 2}]}]}
        feature = genomic_features.Feature(model)
        self.assertEqual("ABCD00001", feature.source_id)
        self.assertEqual(1, feature.version)

    def test_gene(self):
        model = {"id": "ABCD00001", "version": 1, "children": [{"id": "ABCD00001_R0001", "version": 2,
                                                                "children": [{"id": "ABCD00001_P0001", "version": 2}]}]}
        gene = genomic_features.ProteinCodingGene(model)
        self.assertEqual("ABCD00001", gene.source_id)
        self.assertEqual(1, gene.version)
        self.assertEqual(1, len(gene.mrnas))
        mrna = gene.mrnas[0]
        self.assertEqual("ABCD00001_R0001", mrna.source_id)
        self.assertEqual(2, mrna.version)
        cds = mrna.cds
        self.assertEqual("ABCD00001_P0001", cds.source_id)
        self.assertEqual(2, cds.version)


if __name__ == '__main__':
    unittest.main()
