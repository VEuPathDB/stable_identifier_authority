from session import Session
from stable_identifier import StableIdentifierEvent, StableIdentifierLog, StableIdentifierTracking
from feature import FeatureType, FeatureArchive
import hashlib


class StableIdentifierOperation:
    def __init__(self, database_connection):
        self.database_connection = database_connection

    def generate_stable_identifier(self, organism, feature):
        numerical_identifier = self._get_next_incrementation(organism.organism_id, feature.feature_id)
        numerical_identifier_length = len(str(numerical_identifier))
        prefix_zero = "0" * (6 - numerical_identifier_length)
        numerical_identifier_string = prefix_zero + str(numerical_identifier)
        prefix = organism.prefix
        feature_abbreviation = feature.abbreviation
        return prefix + '_' + feature_abbreviation + numerical_identifier_string

    def _get_next_incrementation(self, organism_id, feature_id):
        stable_identifier_log = StableIdentifierLog(self.database_connection)
        last_log = stable_identifier_log.get_last_log(organism_id, feature_id)
        if last_log:
            stable_identifier_log.set_last_log(organism_id, feature_id, (last_log + 1))
            return last_log
        else:
            stable_identifier_log.insert_organism_log(organism_id, feature_id, 1)
            last_log = stable_identifier_log.get_last_log(organism_id, feature_id)
            stable_identifier_log.set_last_log(organism_id, feature_id, (last_log + 1))
            return last_log


class StableIdentifierTransaction(StableIdentifierOperation):
    """
    The main user interface, all stable identifier events should be recorded using this class.


    """

    def __init__(self, database_connection, application_name, application_version, organism_production_name,
                 database_name, message, feature_name):
        self.database_connection = database_connection
        self.application_name = application_name
        self.application_version = application_version
        self.organism_production_name = organism_production_name
        self.database_name = database_name
        self.message = message
        self.feature_name = feature_name

        super().__init__(self.database_connection)

        self.feature_type = FeatureType(self.database_connection, self.feature_name)

        self.session = Session(self.database_connection, self.application_name, self.application_version,
                               self.organism_production_name,
                               self.database_name, self.message)

        self.stable_identifier_event = StableIdentifierEvent(database_connection)
        self.stable_identifier_tracking = StableIdentifierTracking(database_connection)

    def create_new_identifier(self):
        version = 1
        new_stable_identifier = self.generate_stable_identifier(self.session.organism,
                                                                self.feature_type)
        self.stable_identifier_event.insert_identifier(new_stable_identifier,
                                                       self.feature_type.feature_id,
                                                       self.session.session_id, version)
        return new_stable_identifier, version

    def create_batch_identifiers(self, batch_size):
        identifiers = list()
        for i in range(batch_size):
            new_stable_identifier, version = self.create_new_identifier()
            identifiers.append((new_stable_identifier, version))
        return identifiers

    def update_version(self, stable_identifier):
        stable_identifier_event_id, version, feature_type_id = self.stable_identifier_event.get_stable_identifier(
            stable_identifier)

        new_version = version + 1

        self.stable_identifier_event.make_identifier_obsolete(stable_identifier)
        self.stable_identifier_event.insert_identifier(stable_identifier, feature_type_id,
                                                       self.session.session_id, new_version)
        return new_version

    def delete_identifier(self, stable_identifier, sequence=None):
        stable_identifier_event_id, _, _ = self.stable_identifier_event.get_stable_identifier(
            stable_identifier)
        if stable_identifier_event_id is not None:
            self.stable_identifier_event.make_identifier_obsolete(stable_identifier)
        if sequence is not None:
            feature_archive = FeatureArchive(self.database_connection, stable_identifier_event_id)
            feature_archive.archive_feature(sequence, self.calculate_md5_checksum(sequence))

        return stable_identifier_event_id

    def replace_identifier(self, stable_identifier, sequence=None):
        predecessor_event_id = self.delete_identifier(stable_identifier, sequence)
        new_stable_identifier, version = self.create_new_identifier()
        successor_event_id, _, _ = self.stable_identifier_event.get_stable_identifier(
            new_stable_identifier)
        self.stable_identifier_tracking.insert_event_tracking(successor_event_id, predecessor_event_id,
                                                              self.session.session_id)

        return new_stable_identifier, version

    def replace_multiplex_identifiers(self, replace_identifiers: "list of tuple", create_identifiers: int,
                                      annotation_event_type):
        if annotation_event_type not in ['merge', 'split']:
            return 'Can not handle this annotation_event_type'

        predecessor_events = list()
        successor_events = list()
        results = list()
        for identifier in replace_identifiers:
            stable_identifier, sequence = identifier
            predecessor_event_id = self.delete_identifier(stable_identifier, sequence)
            predecessor_events.append((predecessor_event_id, stable_identifier))

        new_stable_identifiers = self.create_batch_identifiers(create_identifiers)
        for new_identifier in new_stable_identifiers:
            new_stable_identifier, version = new_identifier
            successor_event_id, _, _ = self.stable_identifier_event.get_stable_identifier(
                new_stable_identifier)
            successor_events.append((successor_event_id, new_stable_identifier, version))

        if annotation_event_type == 'split':
            for successor_event in successor_events:
                successor_event_id, new_stable_identifier, version = successor_event
                for predecessor_event in predecessor_events:
                    predecessor_event_id, old_stable_identifier = predecessor_event
                    self.stable_identifier_tracking.insert_event_tracking(successor_event_id, predecessor_event_id,
                                                                          self.session.session_id)
                    results.append((old_stable_identifier, new_stable_identifier, version))

        if annotation_event_type == 'merge':
            for predecessor_event in predecessor_events:
                predecessor_event_id, old_stable_identifier = predecessor_event
                for successor_event in successor_events:
                    successor_event_id, new_stable_identifier, version = successor_event
                    self.stable_identifier_tracking.insert_event_tracking(successor_event_id, predecessor_event_id,
                                                                          self.session.session_id)
                    results.append((old_stable_identifier, new_stable_identifier, version))

        return results

    @staticmethod
    def calculate_md5_checksum(sequence):
        return hashlib.md5(sequence.encode()).hexdigest()
