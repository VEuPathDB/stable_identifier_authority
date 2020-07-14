class FeatureType:
    def __init__(self, database_connection, feature_name):
        self.database_values = database_connection.load('feature_type', {'feature_name': feature_name},
                                                        ['feature_type_id', 'abbreviation'])
        self.feature_id = self.database_values['feature_type_id']
        self.abbreviation = self.database_values['abbreviation']


class FeatureArchive:
    def __init__(self, database_connection, stable_identifier_event_id):
        self.database_connection = database_connection
        self.stable_identifier_event_id = stable_identifier_event_id

    def archive_feature(self, sequence, md5_checksum):
        pass
