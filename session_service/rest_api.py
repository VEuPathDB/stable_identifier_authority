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
from sqlalchemy.orm import Session as SqlSession
from sqlalchemy.exc import SQLAlchemyError


class AssigningApplication:

    def __init__(self, sql_alchemy_base, sql_alchemy_engine):
        self.assigning_application = sql_alchemy_base.classes.assigning_application
        self.sql_session = SqlSession(sql_alchemy_engine)

    def __del__(self):
            self.sql_session.close()

    def get(self, **kwargs):

        if 'application_id' in kwargs:
            result = self.sql_session.query(self.assigning_application).get(kwargs['application_id'])
            if result is not None:
                return result.name, int(result.version), result.description
            else:
                return False
        elif 'name' in kwargs and 'version' in kwargs:
            result = self.sql_session.query(self.assigning_application).filter(
                self.assigning_application.name == kwargs['name'],
                self.assigning_application.version == kwargs['version'])
            return result[0].application_id
        else:
            return False  # 400 Bad Request

    def post(self, **kwargs):
        if 'name' in kwargs and 'version' in kwargs and 'description' in kwargs:
            new_application = self.assigning_application(name=kwargs['name'], version=kwargs['version'],
                                                         description=kwargs['description'])
            self.sql_session.add(new_application)
            try:
                self.sql_session.commit()
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
            return new_application.application_id
        else:
            return False  # 400 Bad Request

    def patch(self, **kwargs):
        if 'application_id' in kwargs and 'description' in kwargs:
            row = self.sql_session.query(self.assigning_application).get(kwargs['application_id'])
            if row is not None:
                row.description = kwargs['description']
            else:
                return False
            try:
                self.sql_session.commit()
                return True
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
        else:
            return False  # 400 Bad Request

    @staticmethod
    def delete():
        return False  # 405 METHOD NOT ALLOWED


class ProductionDatabase:

    def __init__(self, sql_alchemy_base, sql_alchemy_engine):
        self.production_database = sql_alchemy_base.classes.production_database
        self.sql_session = SqlSession(sql_alchemy_engine)

    def __del__(self):
        self.sql_session.close()

    def get(self, **kwargs):
        if 'production_database_id' in kwargs:
            result = self.sql_session.query(self.production_database).get(kwargs['production_database_id'])
            if result is not None:
                return result.name
            else:
                return False
        else:
            return False  # 400 Bad Request

    def post(self, **kwargs):
        if 'name' in kwargs:
            new_database = self.production_database(name=kwargs['name'])
            self.sql_session.add(new_database)
            try:
                self.sql_session.commit()
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
            return new_database.production_database_id
        else:
            return False  # 400 Bad Request

    def patch(self, **kwargs):
        if 'production_database_id' in kwargs and 'name' in kwargs:

            row = self.sql_session.query(self.production_database).get(kwargs['production_database_id'])
            if row is not None:
                row.name = kwargs['name']
            else:
                return False
            try:
                self.sql_session.commit()
                return True
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
        else:
            return False  # 400 Bad Request

    @staticmethod
    def delete():
        return False  # 405 METHOD NOT ALLOWED


class Session:

    def __init__(self, sql_alchemy_base, sql_alchemy_engine):
        self.session_table = sql_alchemy_base.classes.session
        self.sql_session = SqlSession(sql_alchemy_engine)

    def __del__(self):
        self.sql_session.close()

    def get(self, **kwargs):
        if 'session_id' in kwargs:
            result = self.sql_session.query(self.session_table).get(kwargs['session_id'])
            return result.ses_application_id, result.ses_production_database_id, result.osid_idsetid,\
                result.data_check, result.message, result.creation_date
        else:
            return False  # 400 Bad Request

    def post(self, **kwargs):
        if 'application_id' in kwargs and 'production_database_id' in kwargs and 'osid_idsetid' in kwargs\
                and 'message' in kwargs:
            new_session = self.session_table(ses_application_id=kwargs['application_id'],
                                             ses_production_database_id=kwargs['production_database_id'],
                                             osid_idsetid=kwargs['osid_idsetid'], message=kwargs['message'])
            self.sql_session.add(new_session)
            try:
                self.sql_session.commit()
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
            return new_session.session_id
        else:
            return False  # '400 Bad Request'

    def patch(self, **kwargs):
        if kwargs['session_id'] and kwargs['data_check']:
            row = self.sql_session.query(self.session_table).get(kwargs['session_id'])
            row.data_check = kwargs['data_check']
            try:
                self.sql_session.commit()
                return True
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
        else:
            return False  # 400 Bad Request

    @staticmethod
    def delete():
            return False  # 400 Bad Request


class SessionIdentifierAction:

    def __init__(self, sql_alchemy_base, sql_alchemy_engine):
        self.session_identifier_action = sql_alchemy_base.classes.session_identifier_action
        self.sql_session = SqlSession(sql_alchemy_engine)

    def __del__(self):
        self.sql_session.close()

    def get(self, **kwargs):
        if 'session_identifier_action_id' in kwargs:
            result = self.sql_session.query(self.session_identifier_action).get(kwargs['session_identifier_action_id'])
            return result.sia_stable_identifier_record_id, result.sia_session_id, result.action
        else:
            return False  # 400 Bad Request

    def post(self, **kwargs):
        if 'stable_identifier_record_id' in kwargs and 'session_id' in kwargs and 'action' in kwargs:
            new_session_identifier_action = self.session_identifier_action(
                sia_stable_identifier_record_id=kwargs['stable_identifier_record_id'],
                sia_session_id=kwargs['session_id'],
                action=kwargs['action'])
            self.sql_session.add(new_session_identifier_action)
            try:
                self.sql_session.commit()
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
            return new_session_identifier_action.session_identifier_action_id
        else:
            return False  # 400 Bad Request

    def patch(self, **kwargs):
        if 'session_identifier_action_id' in kwargs and 'action' in kwargs:
            row = self.sql_session.query(self.session_identifier_action).get(kwargs['session_identifier_action_id'])
            row.action = kwargs['action']
            try:
                self.sql_session.commit()
                return True
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
        else:
            return False  # 400 Bad Request

    @staticmethod
    def delete():
        return False  # 400 Bad Request


class StableIdentifierRecord:

    def __init__(self, sql_alchemy_base, sql_alchemy_engine):
        self.stable_identifier_record = sql_alchemy_base.classes.stable_identifier_record
        self.sql_session = SqlSession(sql_alchemy_engine)

    def __del__(self):
        self.sql_session.close()

    def get(self, **kwargs):
        if 'stable_identifier_record_id' in kwargs:
            result = self.sql_session.query(self.stable_identifier_record).get(kwargs['stable_identifier_record_id'])
            return result.stable_identifier, result.status, result.feature_type
        else:
            return False  # 400 Bad Request

    def post(self, **kwargs):
        if 'stable_identifier' in kwargs and 'status' in kwargs and 'feature_type' in kwargs:
            new_stable_identifier_record = self.stable_identifier_record(stable_identifier=kwargs['stable_identifier'],
                                                                         status=kwargs['status'],
                                                                         feature_type=kwargs['feature_type'])
            self.sql_session.add(new_stable_identifier_record)
            try:
                self.sql_session.commit()
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
            return new_stable_identifier_record.stable_identifier_record_id
        else:
            return False  # 400 Bad Request

    def patch(self, **kwargs):
        if 'stable_identifier_record_id' in kwargs and 'status' in kwargs:
            row = self.sql_session.query(self.stable_identifier_record).get(kwargs['stable_identifier_record_id'])
            row.action = kwargs['status']
            try:
                self.sql_session.commit()
                return True
            except SQLAlchemyError as mysql_error:
                print(mysql_error.__str__())
                return False
        else:
            return False  # 400 Bad Request

    @staticmethod
    def delete():
        return False  # 400 Bad Request
