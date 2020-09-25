import unittest
from event_output import GFFAnnotations


class MyTestCase(unittest.TestCase):
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
        ga._current_gff_line = "KB704696\tVectorBase\tmRNA\t767281  778992  .       +       .       owner=none;Parent=ABC001_R001;ID=ABC001;date_last_modified=2020-01-09;"
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(True, ga._is_feature_line())

        ga._current_gff_line = 'KB704696\tVectorBase\tgene\t757672  778992  .       +       .       owner=none;ID=ABC001;date_last_modified=2020-01-09;'
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(True, ga._is_feature_line())

        ga._current_gff_line = 'KB704696\tVectorBase\tCDS\t770336  770396  .       +       0       Parent=ABC001_R001;ID=ABC001_R001-CDS;Name='
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(True, ga._is_feature_line())

        ga._current_gff_line = 'KB704696\tVectorBase\tXXX\t770336  770396  .       +       0       Parent=ABC001_R001;ID=ABC001_R001-CDS;Name='
        ga._current_fields = ga._current_gff_line.rstrip().split("\t")
        self.assertEqual(False, ga._is_feature_line())



if __name__ == '__main__':
    unittest.main()
