import pymysql.cursors


class DatabaseConnection:
    def __init__(self, host, user, password, database_name, port=3306, charset='utf8mb4',
                 cursor_class=pymysql.cursors.DictCursor):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database_name = database_name
        self.charset = charset
        self.cursor_class = cursor_class

        self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.database_name,
                                          charset=self.charset, cursorclass=self.cursor_class)

    def load(self, table_name, search_terms, columns):
        column_str = self._get_columns(columns)
        where_statement, where_values = self._get_where_statement(search_terms)
        with self.connection.cursor() as cursor:
            sql = "select {} from {} where {};".format(column_str, table_name, where_statement)
            cursor.execute(sql, where_values)
            return cursor.fetchone()

    def load_all(self, table_name, search_terms, columns):
        column_str = self._get_columns(columns)
        where_statement, where_values = self._get_where_statement(search_terms)
        with self.connection.cursor() as cursor:
            sql = "select {} from {} where {};".format(column_str, table_name, where_statement)
            cursor.execute(sql, where_values)
            return cursor.fetchall()

    def commit(self, table_name, sql_parameters):
        columns_str, select_str, _, value_str = self._get_columns_and_values(sql_parameters)
        with self.connection.cursor() as cursor:
            sql = "insert  {}({}) select {} ;".format(table_name, columns_str, select_str)
            cursor.execute(sql, value_str)
            self.connection.commit()
            return cursor.lastrowid

    def update(self, table_name, sql_parameters, search_terms):
        columns_str, _, set_str, value_str = self._get_columns_and_values(sql_parameters)
        where_statement, where_values = self._get_where_statement(search_terms)
        with self.connection.cursor() as cursor:
            sql = "update {} set {} where {};".format(table_name, set_str, where_statement)
            cursor.execute(sql, value_str + where_values)
            self.connection.commit()

    @staticmethod
    def _get_columns(columns):
        sql_str = None
        for column_name in columns:
            if sql_str:
                sql_str = sql_str + ',' + column_name
            else:
                sql_str = column_name

        return sql_str

    @staticmethod
    def _get_columns_and_values(sql_parameters):
        column_str = None
        select_str = None
        set_str = None
        value_list = list()
        for column, value in sql_parameters.items():
            if column_str:
                column_str = column_str + ',' + column
                select_str = select_str + ',%s'
                set_str = set_str + column + '=%s'
                value_list.append(str(value))
            else:
                column_str = column
                select_str = '%s'
                set_str = column + '=%s'
                value_list.append(str(value))
        return column_str, select_str, set_str, value_list

    @staticmethod
    def _get_where_statement(search_terms):
        where_statement = None
        where_values = list()
        for key, value in search_terms.items():
            if where_statement:
                where_statement = where_statement + ' and ' + key + '=%s'
                where_values.append(str(value))
            else:
                where_statement = key + '=%s'
                where_values.append(str(value))
        return where_statement, where_values
