"""Interface between the Python program and PostgreSQL."""

import psycopg # psycopg3

class DatabasePostgreSQL:
    """The class provide methods for interacting with a PostgreSQL database."""

    def __init__(self, database: str):
        """
        Connect to a database and open a cursor to perform database operations.
        :param database: the name of the database
        """
        self.__database = database
        self.__conn = psycopg.connect(dbname = self.__database, user = "postgres", password = "12345678")
        self.__cursor = self.__conn.cursor()

        self.__cursor.execute("SELECT current_database();") # current database name -> the same as self.__database
        dataset = self.__cursor.fetchone()[0]
        print(f'You are connecting to the PostgreSQL database "{dataset}".')

    # The with statement does not allow instance attribute and constrains the resource (connection) within its scope.
        # with psycopg.connect(dbname = "dvdrental", user = "postgres", password = "12345678") as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute("select current_database();")
        #         res = cursor.fetchone()[0]
        #         print(f'You are connecting to the PostgreSQL database "{res}".')

    def close(self):
        """
        Close the database connection.
        """
        self.__cursor.close()
        self.__conn.close()

    def query(self, sql: str) -> list:
        """
        Query the database and return a list of the results.
        :param sql: the SQL query
        :return: a list of the query results
        """
        self.__cursor.execute(sql)
        datasets = self.__cursor.fetchall()
        return datasets
