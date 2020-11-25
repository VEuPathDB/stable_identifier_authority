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

"""Module for classes getting annotation event from different sources"""


class AnnotationEventDB:

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_annotations_events(self, event_type):
        event_sql = "select vb_gene_id, cap_gene_id from gene_events where events = %s;"
        event_db = self.execute_sql(event_sql, event_type)
        return self.setup_gene_model(event_db, event_type)

    def setup_gene_model(self, event_db, event_type):
        events = list()
        for event in event_db:
            genes = list()
            if event_type == 'new_gene':
                genes.append({"source": "apollo", "id": event['cap_gene_id'], "version": 1,
                              "children": self.add_transcripts(event['cap_gene_id'])})
                events.append(genes)
            elif event_type == 'change_gene':
                genes.append({"source": "reference", "id": event['vb_gene_id'], "version": None,
                              "children": self.add_transcripts(event['vb_gene_id'])})
                genes.append({"source": "apollo", "id": event['cap_gene_id'], "version": None,
                              "children": self.add_transcripts(event['cap_gene_id'])})
                events.append(genes)
            elif event_type == 'split_gene':
                genes.append({"source": "reference", "id": event['vb_gene_id'], "version": None,
                              "children": self.add_transcripts(event['vb_gene_id'])})
                for gene_id in event['cap_gene_id'].split(":"):
                    genes.append({"source": "apollo", "id": gene_id, "version": 1,
                                  "children": self.add_transcripts(gene_id)})
                events.append(genes)
            elif event_type == 'merge_gene':
                genes.append({"source": "apollo", "id": event['cap_gene_id'], "version": 1,
                              "children": self.add_transcripts(event['cap_gene_id'])})
                for gene_id in event['vb_gene_id'].split(":"):
                    genes.append({"source": "reference", "id": gene_id, "version": None,
                                  "children": self.add_transcripts(gene_id)})
                events.append(genes)
        return events

    def add_transcripts(self, gene_id):
        sql = "select distinct(transcript_id) from gene_model where gene_id = %s;"
        transcript_db = self.execute_sql(sql, gene_id)
        transcript_list = list()
        for transcript in transcript_db:
            transcript_list.append({'id': transcript['transcript_id'], "children": [{'id': None}]})
        return transcript_list

    def execute_sql(self, sql, values):

        with self.db_connection.cursor() as cursor:
            cursor.execute(sql, values)
        return cursor.fetchall()
