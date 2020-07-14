class StableIdentifierEvent:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def insert_identifier(self, stable_identifier, feature_type_id, session_id, version=0, status='current'):
        self.database_connection.commit('stable_identifier_event', {'stable_identifier': stable_identifier,
                                                                    'sie_feature_type_id': feature_type_id,
                                                                    'sie_session_id': session_id,
                                                                    'version': version,
                                                                    'status': status})

    def make_identifier_obsolete(self, stable_identifier):
        self.database_connection.update('stable_identifier_event', {'status': 'obsolete'},
                                        {'stable_identifier': stable_identifier,
                                         'status': 'current'})

    def get_stable_identifier(self, stable_identifier):
        database_values = self.database_connection.load('stable_identifier_event',
                                                        {'stable_identifier': stable_identifier, 'status': 'current'},
                                                        ['stable_identifier_event_id', 'version',
                                                         'sie_feature_type_id'])
        if database_values:
            return database_values['stable_identifier_event_id'], database_values['version'],\
                   database_values['sie_feature_type_id']
        else:
            return None, None, None


class StableIdentifierLog:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def insert_organism_log(self, organism_id, feature_type_id, allocated_identifier):
        self.database_connection.commit('stable_identifier_log', {'sil_organism_id': organism_id,
                                                                  'sil_feature_type_id': feature_type_id,
                                                                  'last_allocated_identifier': allocated_identifier})

    def get_last_log(self, organism_id, feature_type_id):
        database_values = self.database_connection.load('stable_identifier_log',
                                                        {'sil_organism_id': organism_id,
                                                         'sil_feature_type_id': feature_type_id},
                                                        ['last_allocated_identifier'])
        if database_values:
            return database_values['last_allocated_identifier']
        else:
            return None

    def set_last_log(self, organism_id, feature_type_id, new_log):
        self.database_connection.update('stable_identifier_log', {'last_allocated_identifier': new_log},
                                        {'sil_organism_id': organism_id,
                                         'sil_feature_type_id': feature_type_id})


class StableIdentifierTracking:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def get_tracking_by_successor(self, successor_event_id):
        database_rows = self.database_connection.load_all('stable_identifier_tracking',
                                                          {'successor_event_id': successor_event_id},
                                                          ['predecessor_event_id'])
        results = list()
        for row in database_rows:
            results.append(row['predecessor_event_id'])
        return results

    def get_tracking_by_predecessor(self, predecessor_event_id):
        database_rows = self.database_connection.load_all('stable_identifier_tracking',
                                                          {'predecessor_event_id': predecessor_event_id},
                                                          ['successor_event_id'])
        results = list()
        for row in database_rows:
            results.append(row['successor_event_id'])
        return results

    def insert_event_tracking(self, successor_event_id, predecessor_event_id, sit_session):
        self.database_connection.commit('stable_identifier_tracking', {'successor_event_id': successor_event_id,
                                                                       'predecessor_event_id': predecessor_event_id,
                                                                       'sit_session_id': sit_session})
