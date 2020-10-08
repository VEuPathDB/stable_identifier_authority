import unittest
import configparser

from database_connection import DatabaseConnection
from session import Session
from stable_identifier import StableIdentifierRecord
from operation import StableIdentifierTransaction
import pymysql.cursors

config_file = './session_service.conf'
config = configparser.ConfigParser()
config.read(config_file)
db_name = config['DataBase']['db_name']
db_host = config['DataBase']['db_host']
db_user = config['DataBase']['db_user']
db_pass = config['DataBase']['db_pass']


class SetUpTestDatabase:
    def __init__(self):
        self.connection = pymysql.connect(host=db_host, user=db_user, password=db_pass,
                                          db=db_name,
                                          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def load_test_species(self):
        with self.connection.cursor() as cursor:
            sql = """SET FOREIGN_KEY_CHECKS = 0;
                truncate table stable_identifier_record;
                truncate table session;
                truncate table assigning_application;
                SET FOREIGN_KEY_CHECKS = 1;
                insert assigning_application(application_name, version, description) select 'test_app', 1, 'running test';"""
            for sql_line in sql.splitlines():
                cursor.execute(sql_line)
                self.connection.commit()

    def load_test_session(self):
        with self.connection.cursor() as cursor:
            sql = """insert session(ses_application_id, database_name, message, creation_date) select 1, 'my_test_database', 'test_session', '2013-01-15 13:47:30';"""
            for sql_line in sql.splitlines():
                cursor.execute(sql_line)
                self.connection.commit()


class TransactionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_database = DatabaseConnection(db_host, db_user, db_pass, db_name, './test_mysql_error')

    def setUp(self):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()

    def test_insert_new_identifier(self):
        transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1,
                                                        'my_test_database', 'test_run')
        new_identifier = transaction.insert_new_identifier('AAEL_g000001', 'gene')
        self.assertEqual(1, new_identifier)
        new_identifier_2 = transaction.insert_new_identifier('AAEL_g000002', 'gene')
        self.assertEqual(2, new_identifier_2)
        new_identifier_3 = transaction.insert_new_identifier('AAEL_g000002', 'gene')
        self.assertEqual(False, new_identifier_3)

    def test_delete_identifier(self):
        transaction = StableIdentifierTransaction(self.test_database, 'test_app', 1,
                                                        'my_test_database', 'test_run')

        new_identifier = transaction.insert_new_identifier('AAEL_g000005', 'gene')
        transaction.delete_identifier('AAEL_g000005')
        record = StableIdentifierRecord(self.test_database)
        record_id, _ = record.get_stable_identifier(new_identifier)
        self.assertIsNone(record_id)


class IdentifierTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        test_setup_database.load_test_session()
        cls.test_database = DatabaseConnection(db_host, db_user, db_pass, db_name, './test_mysql_error')

    def test_insert_identifier(self):
        test_event = StableIdentifierRecord(self.test_database)
        test_event.insert_identifier('AAEL_g000001', 'gene', 1)

        record_id, future_name = test_event.get_stable_identifier('AAEL_g000001')

        self.assertEqual('gene', future_name)

    def test_make_obsolete(self):
        test_event = StableIdentifierRecord(self.test_database)
        test_event.insert_identifier('AAEL_g000001', 'gene', 1)
        test_event.make_identifier_obsolete('AAEL_g000001')

        record_id, _ = test_event.get_stable_identifier('AAEL_g000001')

        self.assertIsNone(record_id)


class SessionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_setup_database = SetUpTestDatabase()
        test_setup_database.load_test_species()
        cls.test_database = DatabaseConnection(db_host, db_user, db_pass, db_name, './test_mysql_error')

    def test_session(self):
        test_session = Session(self.test_database, 'test_app', '1', 'my_test_database', 'test case')

        self.assertEqual(1, test_session.assigning_application.application_id)
        self.database_values = self.test_database.load('session', {'ses_application_id': 1},
                                                       ['database_name'])

        self.assertEqual('my_test_database', self.database_values['database_name'])


if __name__ == '__main__':
    unittest.main()
