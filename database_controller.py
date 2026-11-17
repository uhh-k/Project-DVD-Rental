"""Controller as an intermediary between data model and view."""

from abc import ABC, abstractmethod
from dataclasses import fields

from database_postgresql import DatabasePostgreSQL
from database_view import DatabaseView


class DatabaseController(ABC):
    """
    Abstract base class for all database controllers.
    It provides methods to load, manipulate, and present query results from the database.
    """
    def __init__(self, db_name: str, db_classes: list):
        # A protected database manager (model) that connects to the database in PostgreSQL
        self._pg = DatabasePostgreSQL(db_name)
        # A protected view manager that presents data
        self._view = DatabaseView()

        # Database name and its tables represented by classes defined in a model module
        self._dbname = db_name
        self._classes = db_classes

        # Two (unused) data structures that maintain loaded data, saved in dataframes and objects respectively
        self._dataframes = dict()
        self._objects = dict()

    def close(self):
        """
        Close the database connection.
        """
        self._pg.close()

    def query_database(self, sql: str, columns: list):
        """
        Delegate a SQL query to the database and return the results in a dataframe.
        :param sql: the SQL query
        :param columns: the columns to select and present in the result dataframe
        :return: query results in a dataframe
        """
        datasets = self._pg.query(sql) # query results in a list of tuples
        res_df = self._view.query2dataframe(datasets, columns) # query results in a dataframe
        return res_df

    def view_scatter(self, *, x:list, y:list, **kwargs):
        """
        Delegate data to the view manager for displaying them in a scatter plot.
        :param x: a list data for the x axis
        :param y: a list data for the y axis
        :param kwargs: additional info such as labels of the axes and the title of the plot.
        """
        self._view.query2scatter(x, y, **kwargs)

    def get_dataframes(self):
        """
        Get the dataframes that contain all data of the database loaded from PostgreSQL
        :return: a dictionary with table names as keys and dataframes of the loaded data as values
        """
        return self._dataframes

    def get_objects(self):
        """
        Get the objects that represent all data of the database loaded from PostgreSQL
        :return: a dictionary with table/class names as keys and object representations of the loaded data as values
        """
        return self._objects

    def load_data(self):
        """
        Load all data of the database from PostgreSQL
        """
        # SQL query to get all table names of the database
        tables_sql = """
                     SELECT table_name
                     FROM information_schema.tables
                     WHERE table_schema = 'public'
                     AND table_type = 'BASE TABLE'; \
                     """
        column_label = "Table_Name" # column label for the query result in a dataframe
        # Use the class own query_database() function to get the query result in a dataframe (otherwise a list of tuples)
        tables_df = self.query_database(tables_sql, [column_label])
        # Convert the query result (all table names of the database) in a Python list
        table_names = tables_df[column_label].tolist()
        # Call the function to load all tables of the database from PostgreSQL
        self._load_tables(table_names, self._classes)

    def _load_tables(self, table_names: list, classes: list):
        """
        Load all tables of the database from PostgreSQL
        :param table_names: all tables names of the database
        :param classes: class names representing the tables; classes defined in a data model module
        """
        classes_left = list() # classes that do not find a corresponding table in the database
        for clazz in classes: # for each class
            table_name = clazz.__name__.lower() # get the class name in the lower case -> the corresponding table name

            if table_name in table_names: # if table name exists in the database

                # Load the table content in a dataframe and output them in a csv-file (for convenient data viewing)
                table_df = self._output_csv(table_name, clazz)
                self._dataframes[table_name] = table_df # add the dataframe to the dictionary of all data of the database

                # Create a list of objects representing the loaded table contents
                table_obj = self._output_obj(table_name, clazz)
                self._objects[table_name] = table_obj # add the list of objects to the dictionary of all data of the db

            else: # register if a class name does not find a corresponding table in the database
                classes_left.append(clazz)
        else:
            if classes_left: # display a message if there are classes without corresponding tables in the database
                print(f"Not found in the PostgreSQL database {self._dbname}: {classes_left}")

    def _output_csv(self, table_name, clazz):
        """
        Load the data of a table from the PostgreSQL database in a dataframe and additionally output it to a csv file.
        :param table_name: the table name for a SQL query to load its data from the PostgreSQL database
        :param clazz: the class (defined in a data model module) representing the table of the database
        :return:
        """
        # Get all column names of a table by extracting them from the attributes of a class
        column_names = [field.name for field in fields(clazz)]
        # Handle possible deviations between attribute names of a class and column names of a table (depending on the db)
        column_names = self._set_columns(column_names, clazz)

        # Query the PostgreSQL database to load the data of a table
        columns = ", ".join(column_names) # combine column names to a string for the SQL query
        table_sql = f"SELECT {columns} from {table_name}" # construct the SQL query
        # Get the query result in a dataframe (df); set the first column (id) for the df index; sort the df by index
        table_df = (self.query_database(table_sql, column_names)
                    .set_index(column_names[0]).sort_values(column_names[0]))

        # Output the loaded data of a table to a csv-file (for convenient viewing)
        table_df.to_csv(f"table_{table_name}.csv")
        return table_df

    @abstractmethod
    def _set_columns(self, columns, clazz):
        """
        Handle possible deviations between attribute names of a class and column names of a table.
        An abstract method because the deviations depend on the database.
        A specialized database controller (inheriting the current base controller) implements the method.
        The implementation is to reconcile the attribute names of the class with the column names of the table.
        :param columns: attribute names of a class
        :param clazz: the class representing the table of the database
        :return: a list of column names for the SELECT clause in a SQL query
        """
        pass

    def _output_obj(self, table_name, clazz):
        """
        Create a list of objects representing the loaded table contents.
        :param table_name: the table name
        :param clazz: the class representing the table
        :return: a list of objects representing the loaded data of the table
        """
        objects = list() # list of all objects of a class (that represents a corresponding table of the database)
        # Get the dataframe that contains the loaded data of the table and iterate over its rows
        for index, row in self._dataframes[table_name].iterrows(): # index -> id; row -> other instance attributes
            # Handle possible deviations between the dataframe columns and the instance attributes (depending on the db)
            arguments = self._set_arguments(table_name, index, row)
            # Pass the arguments in the right order to the dataclass constructor and add the constructed object to the list
            objects.append(clazz(**arguments)) # a dictionary for keyword arguments
        return objects

    @abstractmethod
    def _set_arguments(self, table_name, index, row):
        """
        Handle possible deviations between the dataframe columns (data of a table) and the instance attributes (of a class).
        An abstract method because the deviations depend on the database.
        A specialized database controller (inheriting the current base controller) implements the method.
        The implementation is to create a dictionary of keyword arguments to be passed to the constructor of the class.
        :param table_name: also the class name
        :param index: the index of the dataframe
        :param row: the row of the dataframe, which contains the instance attributes of the class
        :return: a dictionary of keyword arguments to be passed to the constructor of the class
        """
        pass
