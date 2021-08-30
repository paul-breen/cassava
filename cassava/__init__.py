__version__ = '0.1.0'

import csv
import datetime
from enum import Enum

import matplotlib.pyplot as plt
from blessed import Terminal

INDENT = 4
_term = Terminal()

class CassavaStatus(Enum):
    """
    Cassava Status enum
    """

    undefined = -1
    ok = 1
    warn = 2
    error = 3
    neutral = 4

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

        :yields: A message dict
        """

        first_line_ncols = 0

        for y, row in enumerate(self.rows):
            if y < self.conf['first_data_row']:
                continue
            else:
                if y == self.conf['first_data_row']:
                    first_line_ncols = len(row)
                    msg = {'x': None, 'y': y, 'data': {'is_first_row': True, 'ncols': len(row)}, 'status': CassavaStatus.ok}
                else:
                    msg = {'x': None, 'y': y, 'data': {'is_first_row': False, 'ncols': len(row)}, 'status': CassavaStatus.undefined}
                    if len(row) != first_line_ncols:
                        msg['status'] = CassavaStatus.error
                    else:
                        msg['status'] = CassavaStatus.ok

                yield msg

    def check_for_empty_columns(self):
        """
        Check for any columns that are wholly empty

        :yields: A message dict
        """

        ncols = len(self.rows[self.conf['first_data_row']])

        for x in range(ncols):
            is_empty = True
            status = CassavaStatus.error

            for row in self.rows:
                try:
                    if row[x] != '':
                        is_empty = False
                        status = CassavaStatus.ok
                        break
                except IndexError:
                    # Some rows may (incorrectly) have different column counts
                    # but that's not our concern here
                    pass

            msg = {'x': x, 'y': None, 'data': {'is_empty': is_empty}, 'status': status}
            yield msg

    def check_for_empty_rows(self):
        """
        Check for any rows that are wholly empty

        :yields: A message dict
        """

        for y, row in enumerate(self.rows):
            is_empty = True
            status = CassavaStatus.error
            ncols = len(row)

            for x in range(ncols):
                if row[x] != '':
                    is_empty = False
                    status = CassavaStatus.ok
                    break

            msg = {'x': None, 'y': y, 'data': {'is_empty': is_empty}, 'status': status}
            yield msg

    def print_status(self, text, status):
        """
        Print the given text, colour-coded according to the given status
        """

        if status is CassavaStatus.ok:
            print(_term.green(text))
        elif status is CassavaStatus.warn:
            print(_term.yellow(text))
        elif status is CassavaStatus.error:
            print(_term.red(text))
        elif status is CassavaStatus.neutral:
            print(_term.blue(text))
        else:
            print(text)

    def print_column_counts(self):
        """
        Print whether the number of columns is consistent for all rows
        """

        print('Column counts:')
        indent = ' ' * INDENT

        for msg in self.check_column_counts():
            row_text = 'first row' if msg['data']['is_first_row'] else 'row'
            text = '{}{} {}: ncols = {}'.format(indent, row_text, msg['y'], msg['data']['ncols'])

            if(self.conf['verbose']):
                self.print_status(text, msg['status'])
            else:
                if msg['data']['is_first_row']:
                    self.print_status(text, msg['status'])
                elif msg['status'] in [CassavaStatus.warn, CassavaStatus.error]:
                    self.print_status(text, msg['status'])

    def print_empty_columns(self):
        """
        Print any columns that are wholly empty
        """

        print('Empty columns:')
        indent = ' ' * INDENT

        for msg in self.check_for_empty_columns():
            text = '{}column {} is {}empty'.format(indent, msg['x'], '' if msg['data']['is_empty'] else 'not ')

            if msg['data']['is_empty']:
                self.print_status(text, msg['status'])
            else:
                if(self.conf['verbose']):
                    self.print_status(text, msg['status'])

    def print_empty_rows(self):
        """
        Print any rows that are wholly empty
        """

        print('Empty rows:')
        indent = ' ' * INDENT

        for msg in self.check_for_empty_rows():
            text = '{}row {} is {}empty'.format(indent, msg['y'], '' if msg['data']['is_empty'] else 'not ')

            if msg['data']['is_empty']:
                self.print_status(text, msg['status'])
            else:
                if(self.conf['verbose']):
                    self.print_status(text, msg['status'])

