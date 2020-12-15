import unittest
import configparser
import pymysql.cursors
from session_service import rest_api


class SetUpTestDatabase:

    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        self.db_name = config['DataBase']['db_name']
        self.db_host = config['DataBase']['db_host']
        self.db_user = config['DataBase']['db_user']
        self.db_pass = config['DataBase']['db_pass']
        self.connection = pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass, db=self.db_name,
                                          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def truncate_database(self):
        with self.connection.cursor() as cursor:
            sql = """SET FOREIGN_KEY_CHECKS = 0;
                truncate table stable_identifier_record;
                truncate table session;
                truncate table assigning_application;
                truncate table session_identifier_action;
                truncate table production_database;
                SET FOREIGN_KEY_CHECKS = 1;"""
            for sql_line in sql.splitlines():
                cursor.execute(sql_line)
                self.connection.commit()


class RestTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config_file = '../session_service.conf'
        test_database = SetUpTestDatabase(config_file)
        test_database.truncate_database()
        cls.connection = rest_api.DataBaseConnection(config_file)

    def test_AssigningApplication(self):
        assigning_application = rest_api.AssigningApplication(self.connection)
        application_id = assigning_application.post(name='test_application_01', version=1, description='this is a test application')
        name, version, description = assigning_application.get(application_id=application_id)
        self.assertEqual(('test_application_01', 1, 'this is a test application'), (name, version, description))
        application_id_2 = assigning_application.get(name=name, version=version)
        self.assertEqual(application_id, application_id_2)
        result_4 = assigning_application.get(application_id=10000)
        self.assertEqual(False, result_4)
        result_1 = assigning_application.patch(application_id=application_id, description='update to description')
        self.assertEqual(True, result_1)
        result_2 = assigning_application.patch(application_id=10000, description='update to description')
        self.assertEqual(False, result_2)
        application_id_3 = assigning_application.post(name='test_application_01', version=1, description='this is a test application')
        self.assertEqual(False, application_id_3)
        result_3 = assigning_application.delete()
        self.assertEqual(False, result_3)

    def test_ProductionDatabase(self):
        production_database = rest_api.ProductionDatabase(self.connection)
        production_database_id = production_database.post(name='core_test_database')
        database_name = production_database.get(production_database_id=production_database_id)
        self.assertEqual('core_test_database', database_name)
        result = production_database.get(name='core_test_database')
        print(result)
        database_name_2 = production_database.get(production_database_id=100000)
        self.assertEqual(False, database_name_2)
        result_1 = production_database.patch(production_database_id=production_database_id, name='new_data_base_name')
        self.assertEqual(True, result_1)
        result_2 = production_database.patch(production_database_id=100000, name='new_data_base_name')
        self.assertEqual(False, result_2)
        result_3 = production_database.post(name='new_data_base_name')
        self.assertEqual(False, result_3)
        result_4 = production_database.delete()
        self.assertEqual(False, result_4)

    def test_Session(self):
        assigning_application = rest_api.AssigningApplication(self.connection)
        application_id = assigning_application.post(name='test_application_02', version=1, description='this is a test application')
        production_database = rest_api.ProductionDatabase(self.connection)
        production_database_id = production_database.post(name='core_test_database_02')
        session_table = rest_api.Session(self.connection)
        session_id = session_table.post(application_id=application_id, production_database_id=production_database_id, osid_idsetid=1, message="this is a session test")
        result, _, _, _, _, _ = session_table.get(session_id=session_id)
        self.assertEqual(application_id, result)
        result = session_table.get(osid_idsetid=1)
        print(result)
        self.assertEqual(session_id, result)
        _ = session_table.post(application_id=application_id, production_database_id=production_database_id, osid_idsetid=2, message="this is a second session test")
        #session_id_02 = session_table.post(application_id=application_id, production_database_id=production_database_id, osid_idsetid=1, message="this is a test")
        #self.assertEqual(False, session_id_02)
        result_1 = session_table.patch(session_id=session_id, data_check='pass')
        self.assertEqual(True, result_1)
        result_3 = session_table.delete()
        self.assertEqual(False, result_3)

    def test_StableIdentifierRecord(self):
        stable_identifier_record = rest_api.StableIdentifierRecord(self.connection)
        stable_identifier_record_id = stable_identifier_record.post(stable_identifier='AGAP000001', status='current',
                                                                    feature_type='gene')
        stable_identifier, status, feature_type = stable_identifier_record.get(stable_identifier_record_id=stable_identifier_record_id)
        self.assertEqual(('AGAP000001', 'current', 'gene'), (stable_identifier, status, feature_type))
        result_1 = stable_identifier_record.patch(stable_identifier_record_id=stable_identifier_record_id, status='obsolete')
        self.assertEqual(True, result_1)
        result_2 = stable_identifier_record.delete()
        self.assertEqual(False, result_2)

    def test_session_identifier_action(self):
        session_identifier_action = rest_api.SessionIdentifierAction(self.connection)
        stable_identifier_record = rest_api.StableIdentifierRecord(self.connection)
        stable_identifier_record_id = stable_identifier_record.post(stable_identifier='AGAP000002', status='current', feature_type='gene')
        assigning_application = rest_api.AssigningApplication(self.connection)
        application_id = assigning_application.post(name='test_application_05', version=1, description='this is a test application')
        production_database = rest_api.ProductionDatabase(self.connection)
        production_database_id = production_database.post(name='core_test_database_05')
        session_table = rest_api.Session(self.connection)
        session_id = session_table.post(application_id=application_id, production_database_id=production_database_id, osid_idsetid=10, message="this is a action test")
        session_identifier_action_id = session_identifier_action.post(stable_identifier_record_id=stable_identifier_record_id, session_id=session_id,
                                                                      action='create')
        record_id, ses_id, action = session_identifier_action.get(session_identifier_action_id=session_identifier_action_id)
        self.assertEqual((stable_identifier_record_id, session_id, 'create'), (record_id, ses_id, action))
        result_1 = session_identifier_action.patch(session_identifier_action_id=session_identifier_action_id, action='delete')
        self.assertEqual(True, result_1)
        result_2 = session_identifier_action.delete()
        self.assertEqual(False, result_2)


if __name__ == '__main__':
    unittest.main()
