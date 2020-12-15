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

import re
from session_service import rest_api
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


class SessionService:

    def __init__(self, session_database, application_id, production_database_id, commit_message, event_collection):
        self.database = session_database
        self.application_id = application_id
        self.production_database_id = production_database_id
        self.commit_message = commit_message
        self.event_collection = event_collection
        self.session_table = rest_api.Session(self.database)
        for annotation_event_type in self.event_collection.annotation_event_list:

            for event in annotation_event_type.event_list:
                for gene in event:
                    if gene.source_id != 'reference' and gene.allocated_id:
                        self.add_feature(gene, 'gene')
                        for mrna in gene.mrnas:
                            self.add_feature(mrna, 'transcript')

    def add_feature(self, feature, feature_type):
        session_id = self.session_table.get(osid_idsetid=feature.osid_id)

        if not session_id:
            session_id = self.session_table.post(
                application_id=self.application_id, production_database_id=self.production_database_id,
                osid_idsetid=feature.osid_id, message=self.commit_message)

        stable_identifier_record = rest_api.StableIdentifierRecord(self.database)
        stable_identifier_record_id = stable_identifier_record.post(
                stable_identifier=feature.allocated_id, status='current', feature_type=feature_type)
        if stable_identifier_record_id:
            session_identifier_action = rest_api.SessionIdentifierAction(self.database)
            _ = session_identifier_action.post(
                    stable_identifier_record_id=stable_identifier_record_id, session_id=session_id, action='create')
        else:
            print('NOT loaded: ', feature.allocated_id)
