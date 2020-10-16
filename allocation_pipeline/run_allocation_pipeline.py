import pymysql.cursors
import configparser
import sys
from event_connection import AnnotationEventDB
from annotation_events import EventCollection
from osid_service import OSIDService
import event_output


def get_database_connection(config,
                            charset='utf8mb4', cursor_class=pymysql.cursors.DictCursor):

    database_name = config['DataBase']['db_name']
    host = config['DataBase']['db_host']
    port = config['DataBase']['db_port']
    user = config['DataBase']['db_user']
    password = config['DataBase']['db_pass']

    return pymysql.connect(host=host, port=port, user=user, password=password, db=database_name,
                           charset=charset, cursorclass=cursor_class)


if __name__ == '__main__':
    allocation_config_file = sys.argv[0]
    allocation_config = configparser.ConfigParser()
    allocation_config.read(allocation_config_file)

    db_connection = get_database_connection(allocation_config)
    event_connection = AnnotationEventDB(db_connection)
    osid_service = OSIDService(allocation_config)
    event_collection = EventCollection('test_species', event_connection, osid_service)
    event_collection.create()
    gff_annotation = event_output.GFFAnnotations('input_gff', 'out_put_gff', event_collection)
    gff_annotation.annotate_gff()
    event_file = event_output.AnnotationEventFile(event_collection, 'event_file')
    event_file.write_event_file()
