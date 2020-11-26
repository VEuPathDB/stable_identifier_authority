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
from allocation_pipeline.event_connection import AnnotationEventDB
from allocation_pipeline.annotation_events import EventCollection
from allocation_pipeline.osid_service import OSIDService
from allocation_pipeline.event_output import GFFAnnotations, AnnotationEventFile
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from session_service import rest_api


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
    allocation_config_file = './allocation_pipeline.conf'
    allocation_config = configparser.ConfigParser()
    allocation_config.read(allocation_config_file)

    input_gff_path = allocation_config['FILE']['input_gff']
    output_gff_path = allocation_config['FILE']['output_gff']
    event_file_path = allocation_config['FILE']['event']
    organism_production_name = allocation_config['ProductionOrganism']['name']

    db_connection = get_database_connection(allocation_config)

    event_connection = AnnotationEventDB(db_connection)
    osid_service = OSIDService(allocation_config)
    event_collection = EventCollection(organism_production_name, event_connection, osid_service)
    event_collection.create()

    base = automap_base()
    engine = create_engine(session_database.database_url)
    base.prepare(engine, reflect=True)
    session = Session(engine)


    assigning_application = rest_api.AssigningApplication(self.base, self.engine)
    application_id = rest_api.assigning_application.get(name=name, version=version)

    production_database = rest_api.ProductionDatabase(self.base, self.engine)
    production_database_id = production_database.post(name='core_test_database_02')




    gff_annotation = GFFAnnotations(input_gff_path, output_gff_path, event_collection)
    gff_annotation.annotate_gff()
    event_file = AnnotationEventFile(event_collection, event_file_path)
    event_file.write_event_file()
