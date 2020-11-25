import re
"""module of classes that format the event into different outputs """


class GFFAnnotations:
    allowed_feature = {'gene', 'mRNA', 'CDS', 'exon'}

    def __init__(self, input_gff_file, output_gff_file, event_collection):
        self.in_gff_file = input_gff_file
        self.out_gff_file = output_gff_file
        self.event_collection = event_collection
        self._current_gff_line = None
        self._current_fields = None
        self._output_gff_handle = None

    def annotate_gff(self):
        """open gff file """
        input_gff_handle = open(self.in_gff_file, 'r')
        self._output_gff_handle = open(self.out_gff_file, 'w')

        for line in input_gff_handle:
            self._current_gff_line = line.rstrip()
            self._current_fields = self._current_gff_line.rstrip().split("\t")
            if self._is_feature_line():
                source_id, source_parent_id = self._extract_ids()
                allocated_id, allocated_parent = self._get_feature_info(source_id, source_parent_id)
                self._update_gff_feature(allocated_id, allocated_parent)
            else:
                """write to GFF"""
                self._output_gff_handle.write(self._current_gff_line + '\n')

    def _is_feature_line(self):
        if len(self._current_fields) == 9 and self._current_fields[2] in self.allowed_feature:
            return True
        else:
            return False

    def _get_feature_info(self, source_id, source_parent_id):
        allocated_id = self.event_collection.get_allocated_id(source_id)
        allocated_parent = self.event_collection.get_allocated_id(source_parent_id)

        return allocated_id, allocated_parent

    def _update_gff_feature(self, allocated_id, allocated_parent):

        if allocated_id is not None:
            new_id = 'ID={};'.format(allocated_id)
            self._current_gff_line = re.sub(r'ID=.*?;', new_id, self._current_gff_line)

        if allocated_parent is not None:
            new_parent_id = 'Parent={};'.format(allocated_parent)
            self._current_gff_line = re.sub(r'Parent=.*?;', new_parent_id, self._current_gff_line)

        self._output_gff_handle.write(self._current_gff_line + '\n')

    def _extract_ids(self):
        id_obj = re.match(r'.*ID=(.+?);', self._current_gff_line, flags=0)
        parent_obj = re.match(r'.*Parent=(.+?);', self._current_gff_line, flags=0)

        gff_id = None
        parent = None
        if id_obj:
            gff_id = id_obj.group(1)
        if parent_obj:
            parent = parent_obj.group(1)

        return gff_id, parent


class AnnotationEventFile:
    def __init__(self, event_collection, out_file):
        self.file_handle = open(out_file, 'w')
        self.event_collection = event_collection

    def write_event_file(self):
        for annotation_event_type in self.event_collection.annotation_event_list:
            event_type = annotation_event_type.event_type
            for event in annotation_event_type.event_list:
                for gene in event:
                    if gene.source_id != 'reference':
                        if len(gene.ancestors) == 0 and gene.allocated_id:
                            self.file_handle.write(gene.allocated_id
                                                   + "\t" + event_type + "\t" + '' + "\n")
                        else:
                            for ancestor in gene.ancestors:
                                self.file_handle.write(gene.allocated_id
                                                       + "\t" + event_type + "\t" + ancestor.source_id + "\n")

        self.file_handle.close()
