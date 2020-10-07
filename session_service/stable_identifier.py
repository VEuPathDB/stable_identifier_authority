class StableIdentifierRecord:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def insert_identifier(self, stable_identifier, feature_type, session_id, status='current'):
        self.database_connection.commit('stable_identifier_record', {'stable_identifier': stable_identifier,
                                                                     'feature_type': feature_type,
                                                                     'sie_session_id': session_id, 'status': status})

    def make_identifier_obsolete(self, stable_identifier):
        self.database_connection.update('stable_identifier_record', {'status': 'obsolete'},
                                        {'stable_identifier': stable_identifier,
                                         'status': 'current'})

    def get_stable_identifier(self, stable_identifier):
        database_values = self.database_connection.load('stable_identifier_record',
                                                        {'stable_identifier': stable_identifier, 'status': 'current'},
                                                        ['stable_identifier_record_id',
                                                         'feature_type'])
        if database_values:
            return database_values['stable_identifier_record_id'], database_values['feature_type']
        else:
            return None, None
