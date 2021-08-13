__version__ = '0.1.0'

import argparse
import csv
import datetime

import matplotlib.pyplot as plt

class Cassava(object):
    """
    Context manager for processing CSV files
    """

    DEFAULTS = {
        'header_row': None,
        'first_data_row': 0,
        'xcol': None,
        'ycol': [0],
        'x_as_datetime': False,
        'datetime_format': '%Y-%m-%dT%H:%M:%S',
        'delimiter': ',',
        'skip_initial_space': False,
        'forgive': False,
        'verbose': False
    }
 
    def __init__(self, path=None, conf={}):
        """
        Constructor

        :param path: File path
        :type path: str
        :param conf: Optional configuration
        :type conf: dict
        """

        self.path = path
        self.conf = conf or self.DEFAULTS
        self.fp = None
        self.header_row = []
        self.rows = []
 
    def __enter__(self):
        """
        Enter the runtime context for this object

        The path is opened

        :returns: This object
        :rtype: Cassava
        """

        return self.open(path=self.path)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit the runtime context for this object

        The path is closed

        :returns: False
        :rtype: bool
        """

        self.close()

        return False         # This ensures any exception is re-raised

    def open(self, path=None, mode='r', encoding='utf-8'):
        """
        Open the given path

        :param path: File path
        :type path: str
        :param mode: Mode in which to open the file
        :type mode: str
        :param encoding: Encoding of the file
        :type encoding: str
        :returns: This object
        :rtype: Cassava
        """

        if path:
            self.path = path

        self.fp = open(self.path, mode, encoding=encoding)

        return self

    def close(self):
        """
        Close the path

        :returns: This object
        :rtype: Cassava
        """

        self.fp.close()
        self.fp = None

        return self

    def read(self):
        """
        Read the input file

        The input is parsed into a list of rows and accessible via self.rows

        If an index has been set in the header_row config item, then after
        parsing the rows, the header row is stored in self.header_row

        :returns: The rows
        :rtype: list
        """

        reader = csv.reader(self.fp, delimiter=self.conf['delimiter'], skipinitialspace=self.conf['skip_initial_space'])
        self.rows = [row for row in reader]
        self.store_header()

        return self.rows

    def store_header(self):
        """
        Store the header row, if one is present in the file

        :returns: The parsed header row
        :rtype: list
        """

        if self.conf['header_row'] is not None:
            self.header_row = self.rows[self.conf['header_row']]

        return self.header_row

    def get_column_labels_from_header(self, cols):
        """
        Get the corresponding labels from the header row, for the given colums

        :param cols: The column indices
        :type cols: list
        :returns: The column labels
        :rtype: list
        """

        labels = []

        if self.header_row:
            labels = [self.header_row[col] for col in cols]

        return labels

    def _catch(self, func, handle=lambda e: e, *args, **kwargs):
        """
        Enable a function to be exception handled, inline in comprehensions

        :param func: The processing function
        :type func: Function
        :param handle: Exception handling function
        :type handle: Function
        :param args: Arbitrary arguments for the processing function
        :type args: args
        :param kwargs: Arbitrary keyword arguments for the processing function
        :type kwargs: kwargs
        :returns: The output of the processing function, or if an exception
        occurs, the output of the exception handling function
        """

        try:
            return func(*args, **kwargs)
        except Exception as e:
            return handle(e)

    def get_x_axis_data(self):
        """
        Get the x-axis data from the rows, transforming as required

        :returns: The x-axis data
        :rtype: list
        """

        # The x-column can be datetime, numeric, or default to list of indices
        if self.conf['xcol'] is not None:
            if self.conf['x_as_datetime']:
                x = [datetime.datetime.strptime(i[self.conf['xcol']] or 'NaN', self.conf['datetime_format']) for i in self.rows[self.conf['first_data_row']:len(self.rows)]]
            else:
                x = [float(i[self.conf['xcol']] or 'NaN') for i in self.rows[self.conf['first_data_row']:len(self.rows)]]
        else:
            x = [i for i, n in enumerate(range(self.conf['first_data_row'], len(self.rows)))]

        return x

    def get_y_axis_data(self, col):
        """
        Get the y-axis data from the rows, transforming as required

        :param col: The column index
        :type col: int
        :returns: The y-axis data
        :rtype: list
        """

        if self.conf['forgive']:
            y = [self._catch(lambda: float(i[col]), handle=lambda e: None) for i in self.rows[self.conf['first_data_row']:len(self.rows)]]
        else:
            y = [float(i[col] or 'NaN') for i in self.rows[self.conf['first_data_row']:len(self.rows)]]

        return y

    def plot(self):
        """
        Plot the data
        """

        x = self.get_x_axis_data()
        labels = self.get_column_labels_from_header(self.conf['ycol'])

        for i, ycol in enumerate(self.conf['ycol']):
            y = self.get_y_axis_data(ycol)
            opt_kwargs = {}

            if len(labels) > i and labels[i]:
                opt_kwargs['label'] = labels[i]

            plt.plot(x, y, **opt_kwargs)

        plt.legend()
        plt.show()

    def check_column_counts(self):
        """
        Check that the number of columns is consistent for all rows
        """

        first_line_ncols = 0

        for i, row in enumerate(self.rows):
            if(i < self.conf['first_data_row']):
                continue
            if(self.conf['verbose']):
                print('row {}: ncols = {}'.format(i, len(row)))
            else:
                if(i == self.conf['first_data_row']):
                    first_line_ncols = len(row)
                    print('first row {}: ncols = {}'.format(i, len(row)))
                else:
                    if(len(row) != first_line_ncols):
                        print('row {}: ncols = {}'.format(i, len(row)))

