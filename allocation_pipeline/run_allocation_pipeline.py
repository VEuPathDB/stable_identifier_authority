import pymysql.cursors
import configparser
import event_connection
import annotation_events
import osid_service
import event_output


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
    event_connection = event_connection.AnnotationEventDB(db_connection)
    osid_service = osid_service.OSIDService(allocation_config)
    event_collection = annotation_events.EventCollection(organism_production_name, event_connection, osid_service)
    event_collection.create_event_collection()
    gff_annotation = event_output.GFFAnnotations(input_gff_path, output_gff_path, event_collection)
    gff_annotation.annotate_gff()
    event_file = event_output.AnnotationEventFile(event_collection, event_file_path)
    event_file.write_event_file()
