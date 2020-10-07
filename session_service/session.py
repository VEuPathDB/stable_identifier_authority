import datetime


class Session:
    def __init__(self, database_connection, application_name, application_version, database_name, message):

        session_date = datetime.datetime.now()
        mysql_date = "{}-{}-{} {}:{}:{}".format(session_date.year, session_date.month,
                                                session_date.day, session_date.hour,
                                                session_date.minute, session_date.second)
        self.assigning_application = AssigningApplication(database_connection, application_name, application_version)
        self.application_id = self.assigning_application.application_id
        self.session_id = database_connection.commit('session', {'database_name': database_name, 'message': message,
                                                                 'creation_date': mysql_date,
                                                                 'ses_application_id': self.application_id})

    def check_resent_session(self):
        pass


class AssigningApplication:
    def __init__(self, database_connection, application_name, application_version):
        self.database_values = database_connection.load('assigning_application',
                                                        {'application_name': application_name,
                                                         'version': application_version},
                                                        ['application_id'])
        self.application_id = self.database_values['application_id']
