"""Presentation of a database query result, e.g., in a table or plot."""

import pandas as pd
import matplotlib.pyplot as plt

class DatabaseView:
    """The class provides methods to display a database query result in different ways."""

    @staticmethod
    def query2dataframe(datasets: list, columns: list) -> pd.DataFrame:
        """
        Convert a database query result (a list of tuples) to a pandas dataframe.
        :param datasets: the database query result to be converted.
        :param columns: the column names of the dataframe.
        :return: a pandas dataframe.
        """
        transposed = [list(col) for col in zip(*datasets)]
        dictionary = dict(zip(columns, transposed))
        df = pd.DataFrame(dictionary)
        df.index += 1 # index to start from 1 instead of 0
        return df

    @staticmethod
    def query2scatter(x: list, y: list, /, **kwargs):
        """
        Convert a database query result to a scatter plot.
        :param x: a list of data for the x-axis.
        :param y: a list of data for the y-axis.
        :param kwargs: additional info such as labels of the axes and the title of the plot.
        """
        magnitudes = [round(i) for i in y]
        plt.scatter(x, y, c=magnitudes, s=magnitudes, cmap=plt.cm.get_cmap('jet'))
        plt.colorbar()
        if "xlabel" in kwargs: plt.xlabel(kwargs["xlabel"])
        if "ylabel" in kwargs: plt.ylabel(kwargs["ylabel"])
        if "title" in kwargs: plt.title(kwargs["title"])
        plt.show()
