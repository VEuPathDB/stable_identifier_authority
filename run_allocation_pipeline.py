"""
Copyright [2017-2020] EMBL-European Bioinformatics Institute

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

import pymysql.cursors
import configparser
import sys
from allocation_service.event_input import AnnotationEventDB
from allocation_service.annotation_events import EventCollection
from allocation_service.osid_service import OSIDService
from allocation_service.event_output import GFFAnnotations, AnnotationEventFile, SessionService
from session_service.rest_api import DataBaseConnection, AssigningApplication, ProductionDatabase


def get_database_connection(config,
                            charset='utf8mb4', cursor_class=pymysql.cursors.DictCursor):

    database_name = config['DataBase']['db_name']
    host = config['DataBase']['db_host']
    port = int(config['DataBase']['db_port'])
    user = config['DataBase']['db_user']
    password = config['DataBase']['db_pass']

    return pymysql.connect(host=host, port=port, user=user, password=password, db=database_name,
                           charset=charset, cursorclass=cursor_class)


if __name__ == '__main__':
    allocation_config_file = './allocation_service/allocation_pipeline.conf'
    session_config_file = './session_service/session_service.conf'
    allocation_config = configparser.ConfigParser()
    allocation_config.read(allocation_config_file)

    pipeline_name = allocation_config['PIPELINE']['name']
    pipeline_version = allocation_config['PIPELINE']['version']
    commit_message = allocation_config['PIPELINE']['message']
    input_gff_path = allocation_config['FILE']['input_gff']
    output_gff_path = allocation_config['FILE']['output_gff']
    event_file_path = allocation_config['FILE']['event']
    organism_production_name = allocation_config['ProductionOrganism']['name']
    production_database_name = allocation_config['ProductionOrganism']['database']

    db_connection = get_database_connection(allocation_config)

    event_input = AnnotationEventDB(db_connection)
    osid_service = OSIDService(allocation_config)
    event_collection = EventCollection(organism_production_name, event_input, osid_service)
    event_collection.create()

    session_database = DataBaseConnection(session_config_file)
    assigning_application = AssigningApplication(session_database)
    application_id = assigning_application.get(name=pipeline_name, version=pipeline_version)
    if not application_id:
        sys.exit('Please add the assigning pipeline to the assigning_application table in the session database')
    production_database = ProductionDatabase(session_database)
    production_database_id = production_database.get(name=production_database_name)

    if not production_database_id:
        production_database_id = production_database.post(name=production_database_name)

    session_service = SessionService(session_database, application_id, production_database_id,
                                     commit_message, event_collection)

    gff_annotation = GFFAnnotations(input_gff_path, output_gff_path, event_collection)
    gff_annotation.annotate_gff()
    event_file = AnnotationEventFile(event_collection, event_file_path)
    event_file.write_event_file()
