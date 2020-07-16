import unittest
from database_connection import DatabaseConnection
from organism import Organism
from session import Session
from feature import FeatureType
from stable_identifier import StableIdentifierEvent, StableIdentifierLog, StableIdentifierTracking
from operation import StableIdentifierOperation, StableIdentifierTransaction
import pymysql.cursors

password = 'xxxxxxx'


class SetUpTestDatabase:
    def __init__(self):
        self.connection = pymysql.connect(host='localhost', user='test_user', password=password,
                                          db='test_stable_identifier_authority',
                                          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def load_test_species(self):
        with self.connection.cursor() as cursor:
            sql = """SET FOREIGN_KEY_CHECKS = 0;
                truncate table stable_identifier_tracking;
                truncate table feature_archive;
                truncate table stable_identifier_event;
                truncate table session;
                truncate table stable_identifier_log;
                truncate table feature_type;
                truncate table assigning_application;
                truncate table organism_build;
                truncate table organism;
                SET FOREIGN_KEY_CHECKS = 1;
                insert organism(production_name, genus, species, strain, ncbi_taxonomy_id, prefix) select 'aedes_aegypti_lvpagwg', 'aedes', 'aegypti', 'LVP_AGWG', '7159', 'AAEL' ;
                select @organismID := organism_id from organism where production_name = 'aedes_aegypti_lvpagwg';
                insert organism_build(ob_organism_id, INSDC_number, gene_build) select  @organismID, 'GCA_002204515.1', 'AaegL5.2';
                insert assigning_application(application_name, version, description) select 'test_app', 1, 'running test';
                insert feature_type(feature_name, abbreviation) select 'gene', 'g';
                insert feature_type(feature_name, abbreviation) select 'transcript', 't';
                insert feature_type(feature_name, abbreviation) select 'translation', 'p';"""
            for sql_line in sql.splitlines():
                cursor.execute(sql_line)
                self.connection.commit()

    def load_test_session(self):
        with self.connection.cursor() as cursor:
            sql = """insert session(ses_application_id, database_name, ses_build_id, message, creation_date) select 1, 'my_test_database', 1, 'test_session', '2013-01-15 13:47:30';"""
            for sql_line in sql.splitlines():
                cursor.execute(sql_line)
                self.connection.commit()

    def load_test_log(self):
        with self.connection.cursor() as cursor:
            sql = """insert stable_identifier_log(sil_organism_id, sil_feature_type_id, last_allocated_identifier) select 1, 1, 1;"""
            for sql_line in sql.splitlines():
                cursor.execute(sql_line)
                self.connection.commit()


class TransactionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_database = DatabaseConnection('localhost', 'test_user', password, 'test_stable_identifier_authority')

    def setUp(self):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()

    def test_create_new_identifier(self):
        event_transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1, 'aedes_aegypti_lvpagwg',
                                                        'my_test_database', 'test_run', 'gene')
        new_identifier, version = event_transaction.create_new_identifier()
        self.assertEqual('AAEL_g000001', new_identifier)
        new_identifier_2, _ = event_transaction.create_new_identifier()
        self.assertEqual('AAEL_g000002', new_identifier_2)

    def test_update_version(self):
        event_transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1, 'aedes_aegypti_lvpagwg',
                                                        'my_test_database', 'test_run', 'gene')

        new_identifier, version = event_transaction.create_new_identifier()
        event_transaction.update_version(new_identifier)
        events = StableIdentifierEvent(self.test_database)
        _, updated_version, _ = events.get_stable_identifier(new_identifier)
        self.assertEqual(2, updated_version)

    def test_delete_identifier(self):
        event_transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1, 'aedes_aegypti_lvpagwg',
                                                        'my_test_database', 'test_run', 'gene')

        new_identifier, version = event_transaction.create_new_identifier()
        event_transaction.delete_identifier(new_identifier, 'AATTGCAAAATTTTGCCC')
        events = StableIdentifierEvent(self.test_database)
        _, version, _ = events.get_stable_identifier(new_identifier)
        self.assertIsNone(version)

    def test_replace_identifier(self):
        event_transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1, 'aedes_aegypti_lvpagwg',
                                                        'my_test_database', 'test_run', 'gene')
        identifier_1, _ = event_transaction.create_new_identifier()
        identifier_2, _ = event_transaction.replace_identifier(identifier_1, 'AATTGCAAAATTTTGCCC')
        self.assertEqual('AAEL_g000002', identifier_2)
        events = StableIdentifierEvent(self.test_database)
        event_id, version, _, = events.get_stable_identifier('AAEL_g000002')
        self.assertEqual(1, version)

        tracking = StableIdentifierTracking(self.test_database)
        predecessor_list = tracking.get_tracking_by_successor(event_id)
        self.assertEqual(1, predecessor_list[0])

    def test_calculate_md5_checksum(self):
        event_transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1, 'aedes_aegypti_lvpagwg',
                                                        'my_test_database', 'test_run', 'gene')
        seq_checksum = event_transaction.calculate_md5_checksum('ATCGATCG')
        self.assertEqual('719476596e0da2ff50f227a00cbe87a7', seq_checksum)


class OperationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        test_setup_database.load_test_session()
        test_setup_database.load_test_log()
        cls.test_database = DatabaseConnection('localhost', 'test_user', password, 'test_stable_identifier_authority')

    def test_generate_stable_identifier(self):
        test_organism = Organism(self.test_database, 'aedes_aegypti_lvpagwg')
        test_feature = FeatureType(self.test_database, 'gene')
        test_operation = StableIdentifierOperation(self.test_database)
        first_identifier = test_operation.generate_stable_identifier(test_organism, test_feature)
        self.assertEqual('AAEL_g000001', first_identifier)
        second_identifier = test_operation.generate_stable_identifier(test_organism, test_feature)
        self.assertEqual('AAEL_g000002', second_identifier)


class IdentifierTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        test_setup_database.load_test_session()
        cls.test_database = DatabaseConnection('localhost', 'test_user', password, 'test_stable_identifier_authority')

    def test_insert_identifier(self):
        test_event = StableIdentifierEvent(self.test_database)
        test_event.insert_identifier('AAEL_g000001', 1, 1)

        event_id, version, future_id = test_event.get_stable_identifier('AAEL_g000001')

        self.assertEqual(0, version)
        self.assertEqual(1, future_id)

    def test_make_obsolete(self):
        test_event = StableIdentifierEvent(self.test_database)
        test_event.make_identifier_obsolete('AAEL_g000001')

        event_id, version, future_id = test_event.get_stable_identifier('AAEL_g000001')
        print(version)
        self.assertIsNone(version)

    def test_identifier_log(self):

        test_log = StableIdentifierLog(self.test_database)
        self.assertIsNone(test_log.get_last_log(1, 1))

        test_log.insert_organism_log(1, 1, 1)
        self.assertEqual(1, test_log.get_last_log(1, 1))


class FeatureTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        cls.test_database = DatabaseConnection('localhost', 'test_user', password, 'test_stable_identifier_authority')

    def test_feature_type(self):
        test_feature = FeatureType(self.test_database, 'gene')
        self.assertEqual('g', test_feature.abbreviation)


class SessionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        cls.test_database = DatabaseConnection('localhost', 'test_user', password, 'test_stable_identifier_authority')

    def test_session(self):
        test_session = Session(self.test_database, 'test_app', '1', 'aedes_aegypti_lvpagwg',
                               'my_test_database', 'test case')

        self.assertEqual(1, test_session.assigning_application.application_id)
        self.database_values = self.test_database.load('session', {'ses_application_id': 1},
                                                       ['database_name'])

        self.assertEqual('my_test_database', self.database_values['database_name'])


class OrganismTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        cls.test_database = DatabaseConnection('localhost', 'test_user', password, 'test_stable_identifier_authority')

    def test_organism(self):
        species = Organism(self.test_database, 'aedes_aegypti_lvpagwg')
        self.assertEqual(1, species.organism_id)
        self.assertEqual('AAEL', species.prefix)

    def test_organism_build(self):
        species = Organism(self.test_database, 'aedes_aegypti_lvpagwg')
        self.assertEqual(1, species.build.build_id)




if __name__ == '__main__':
    unittest.main()
