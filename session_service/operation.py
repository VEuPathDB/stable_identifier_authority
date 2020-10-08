from session import Session
from stable_identifier import StableIdentifierRecord


class StableIdentifierTransaction:
    """
    The main user interface, all stable identifier events should be recorded using this class.
    """

    def __init__(self, database_connection, application_name, application_version,
                 database_name, message):
        self.database_connection = database_connection
        self.application_name = application_name
        self.application_version = application_version

        self.database_name = database_name
        self.message = message

        self.session = Session(self.database_connection, self.application_name, self.application_version,
                               self.database_name, self.message)
        self.stable_identifier_record = StableIdentifierRecord(self.database_connection)

    def insert_new_identifier(self, new_stable_identifier, feature_type):

        last_insert_id = self.stable_identifier_record.insert_identifier(new_stable_identifier,
                                                                         feature_type, self.session.session_id)
        return last_insert_id

    def insert_batch_identifiers(self, stable_identifiers, feature_type):
        identifiers = list()
        for stable_identifier in stable_identifiers:
            new_stable_identifier = self.insert_new_identifier(stable_identifier, feature_type)
            identifiers.append(new_stable_identifier)
        return identifiers

    def delete_identifier(self, stable_identifier):
        stable_identifier_record_id, _ = self.stable_identifier_record.get_stable_identifier(
            stable_identifier)
        if stable_identifier_record_id is not None:
            self.stable_identifier_record.make_identifier_obsolete(stable_identifier)

        return stable_identifier_record_id
