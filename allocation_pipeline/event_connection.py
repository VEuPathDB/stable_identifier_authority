"""Module for classes getting annotation event from different sources"""

class AnnotationEventDB:

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_annotations_events(self):
        pass