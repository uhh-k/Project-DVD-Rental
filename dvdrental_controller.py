"""Controller as an intermediary between data model and view, specialized for the database "dvdrental"."""

import re
import json

from database_controller import DatabaseController


class DVDrentalController(DatabaseController):
    """The class inherits the abstract base class DatabaseController, implementing the abstract methods."""

    def _set_columns(self, column_names, clazz):
        """
        Handle possible deviations between attribute names of a class and column names of a table.
        Implementation of an abstract method because the deviations depend on the database.
        The implementation is to reconcile the attribute names of the class with the column names of the table.
        Name modification -> an attribute name modified to be the same as the corresponding column name.
        Order modification -> id to be the first column so that later the dataframe is ordered by id.
        :param columns: attribute names of a class
        :param clazz: the class representing the table of the database
        :return: a list of column names for the SELECT clause in a SQL query
        """
        if self._dbname == "dvdrental": # maybe unnecessary if the specialized controller is used only for "dvdrental"
            # Shift the first attribute (always 'last_update') to the last so that id becomes the first column
            column_names.append(column_names.pop(0))

            class_name = clazz.__name__.lower() # get class name
            if class_name == "payment":           # attribute of the class "Payment" -> 'last_update'
                column_names[-1] = "payment_date" # column name of the table "payment" -> 'payment_date'

            # Change the now first attribute name 'id' to the primary key according to the table
            if class_name not in ["film_category", "film_actor"]: # both tables with composite primary keys
                column_names[0] = class_name + "_id" # the primary key of other tables -> table name + '_id'
        return column_names

    def _set_arguments(self, table_name, index, row):
        """
        Handle possible deviations between the dataframe columns (data of a table) and the instance attributes (of a class).
        Implementation of an abstract method because the deviations depend on the database.
        The implementation is to create a dictionary of keyword arguments to be passed to the constructor of the class.
        Name modification -> an dataframe column name modified to be the same as the corresponding instance attribute name.
        Argument modification -> argument modified to a more proper data type and/or content
        :param table_name: also the class name
        :param index: the index of the dataframe, which is the attribute 'id' of a class (except for composite primary keys)
        :param row: the row of the dataframe, which contains the remaining attributes of the class
        :return: a dictionary of keyword arguments to be passed to the constructor of the class
        """
        arguments = dict() # a dictionary of keyword arguments to be passed to the constructor of the class

        if self._dbname == "dvdrental": # maybe unnecessary if the specialized controller is used only for "dvdrental"

            # Modify the attribute 'fulltext' of the class "Film" to a dictionary of key-value pairs
            # (When loaded from the database, the attribute was converted to a string and saved as such in the dataframe.)
            if table_name == "film":
                # film.fulltext consists of key-value pairs.
                # Some values in film.fulltext are a series of numbers separated by comma (without space),
                # e.g. 'key':2,18,37 -> to be replaced by a [list of numbers]
                replace = lambda x: f'[{x.group()}]' # function for replacement
                if "," in row["fulltext"]: # re.sub() from module re
                    row["fulltext"] = re.sub(r"[0-9]+,[0-9]+(,[0-9]+)*", replace, row["fulltext"])

                # film.fulltext with key-value pairs as a string -> to be converted to a Python dictionary by json.loads()
                # So far in the string: not surrounded by {curly brackets}; keys in 'single quotes'; key-value pairs separated by space
                # The string input S for json.loards() must begin and end with {curly brackets}.
                # The keys in S must be in "double quotes". The separator in S must be comma.
                row["fulltext"] = "{" + row["fulltext"].replace("\'", "\"").replace(" ", ", ") + "}"
                # json.loads() from module json converts a string to a Python dictionary.
                row["fulltext"] = json.loads(row["fulltext"])

            # Classes representing a table with composite primary keys do not have their own 'id' attribute.
            # The content of the dataframe index represents the first attribute of those classes (one of the composite primary keys).
            # Assign the dataframe index (as value) to the argument keyword (as key) that corresponds to the first attribute.
            if   table_name == "film_category": arguments["film_id"]  = index
            elif table_name == "film_actor"   : arguments["actor_id"] = index
            # Other classes ->
            # Assign the dataframe index (as value) to the argument keyword (as key) that corresponds to their 'id' attribute
            else: arguments['id'] = index

            # Append the dataframe row (with remaining attributes) to the dictionary
            arguments.update(row.to_dict())

            if table_name == "payment": # dataframe column 'last_update' -> keyword argument (instance attribute) 'payment_date'
                arguments["last_update"] = arguments.pop("payment_date")
        return arguments
