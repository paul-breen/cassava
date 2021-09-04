__version__ = '0.1.0'

import csv
import datetime
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
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

    def _raise(self, e):
        """
        Enable an exception to be raised in a lambda expression

        :param e: The exception to raise
        :type e: Exception
        :raises: e
        """

        raise e

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

    def get_column_data(self, col, exc_value=np.nan):
        """
        Get the data for the given column, taking into account forgive mode

        :param col: The column index
        :type col: int
        :param exc_value: The value to use in place of values that throw an
        exception, when running in forgive mode
        :type exc_value: any
        :returns: The column data
        :rtype: list
        """

        if self.conf['forgive']:
            data = [self._catch(lambda: float(row[col]), handle=lambda e: exc_value) for row in self.rows[self.conf['first_data_row']:len(self.rows)]]
        else:
            data = [float(row[col]) for row in self.rows[self.conf['first_data_row']:len(self.rows)]]

        return data

    def get_x_axis_data(self, exc_value=np.nan):
        """
        Get the x-axis data from the rows, transforming as required

        :param exc_value: The value to use in place of values that throw an
        exception, when running in forgive mode
        :type exc_value: any
        :returns: The x-axis data
        :rtype: list
        """

        # The x-column can be datetime, numeric, or default to list of indices
        if self.conf['xcol'] is not None:
            if self.conf['x_as_datetime']:
                x = [self._catch(lambda: datetime.datetime.strptime(row[self.conf['xcol']], self.conf['datetime_format']), handle=lambda e: self._raise(ValueError(f'Failed to convert x-column at row {i} to datetime: {row}'))) for i, row in enumerate(self.rows[self.conf['first_data_row']:len(self.rows)], start=self.conf['first_data_row'])]
            else:
                x = self.get_column_data(self.conf['xcol'], exc_value=exc_value)
        else:
            x = [i for i, n in enumerate(range(self.conf['first_data_row'], len(self.rows)))]

        return x

    def get_y_axis_data(self, col, exc_value=np.nan):
        """
        Get the y-axis data from the rows, transforming as required

        :param col: The column index
        :type col: int
        :param exc_value: The value to use in place of values that throw an
        exception, when running in forgive mode
        :type exc_value: any
        :returns: The y-axis data
        :rtype: list
        """

        return self.get_column_data(col, exc_value=exc_value)

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

    def check_empty_columns(self):
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

    def check_empty_rows(self):
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

    def compute_stats(self, data):
        """
        Compute statistics for the given data

        :returns: A stats dict
        :rtype: dict
        """

        q = np.nanquantile(data, [0.25, 0.5, 0.75])
        stats = {'min': np.nanmin(data), 'max': np.nanmax(data), 'mean': np.nanmean(data), 'q1': q[0], 'median': q[1], 'q3': q[2], 'std': np.nanstd(data)}

        return stats

    def compute_column_stats(self):
        """
        Compute column statistics for the configured columns

        :yields: A message dict
        """

        for ycol in self.conf['ycol']:
            Y = self.get_y_axis_data(ycol)
            stats = self.compute_stats(Y)
            msg = {'x': ycol, 'y': None, 'data': stats, 'status': CassavaStatus.ok}
            yield msg

    def check_column_outliers_iqr(self, k=1.5):
        """
        Check for any outliers for the configured columns (IQR)

        :param k: The factor to multiply the IQR by
        :type k: float
        :yields: A message dict
        """

        y0 = self.conf['first_data_row']

        for ycol in self.conf['ycol']:
            Y = self.get_y_axis_data(ycol)
            stats = self.compute_stats(Y)
            iqr = stats['q3'] - stats['q1']

            # High outliers
            for y in np.where(Y > stats['q3'] + k * iqr)[0]:
                msg = {'x': ycol, 'y': y + y0, 'data': {'value': Y[y]}, 'status': CassavaStatus.error}
                yield msg

            # Low outliers
            for y in np.where(Y < stats['q1'] - k * iqr)[0]:
                msg = {'x': ycol, 'y': y + y0, 'data': {'value': Y[y]}, 'status': CassavaStatus.error}
                yield msg

    def print_status(self, text, status, end='\n'):
        """
        Print the given text, colour-coded according to the given status

        :param text: The text to print
        :type text: str
        :param status: The status of the message for colour-coding
        :type status: CassavaStatus
        :param end: An arbitrary end to append to the text (as with print())
        :type end: str
        """

        if status is CassavaStatus.ok:
            print(_term.green(text), end=end)
        elif status is CassavaStatus.warn:
            print(_term.yellow(text), end=end)
        elif status is CassavaStatus.error:
            print(_term.red(text), end=end)
        elif status is CassavaStatus.neutral:
            print(_term.blue(text), end=end)
        else:
            print(text, end=end)

    def print_msg_table(self, table, indent=0, fmt='.2f'):
        """
        Print the given list of message dicts as a table

        :param table: The list of message dicts to be tabulated
        :type table: list
        :param indent: An indent to prepend to each row of the table
        :type indent: int
        :param fmt: A format specifier to apply to each data value
        :type fmt: str
        """

        prefix = ' ' * indent

        # Dynamically calculate column lengths and data coords label lengths
        if len(table) > 0:
            coords = []
            if table[0]['x'] is not None:
                coords.append('column')
            if table[0]['y'] is not None:
                coords.append('row')
            label_header = ','.join(coords)

            col_lens = [0] * len(table[0]['data'])
            label_len = len(label_header) + 1
            labels = []

        for row in table:
            for x, (k, v) in enumerate(row['data'].items()):
                col_lens[x] = np.max([col_lens[x], len(str(k)) + 1, len(f'{v:{fmt}}') + 1])

            coords = []
            if row['x'] is not None:
                coords.append(str(row['x']))
            if row['y'] is not None:
                coords.append(str(row['y']))
            label = ','.join(coords)
            labels.append(label)
            label_len = np.max([label_len, len(label) + 1])

        for i, row in enumerate(table):
            if i == 0:
                text = ''.join([f'{k}'.ljust(col_lens[x]) for x,k in enumerate(row['data'])])
                self.print_status(prefix + label_header.ljust(label_len) + text, row['status'])

            text = ''.join([f'{v:{fmt}}'.ljust(col_lens[x]) for x,v in enumerate(row['data'].values())])
            self.print_status(prefix + labels[i].ljust(label_len) + text, row['status'])

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

    def print_row_counts(self):
        """
        Print information about the total rows and data rows
        """

        print('Row counts:')
        indent = ' ' * INDENT

        status = CassavaStatus.ok
        total_nrows = len(self.rows)

        try:
            data_nrows = total_nrows - self.conf['first_data_row']
        except KeyError:
            data_nrows = total_nrows

        text = '{}total rows = {}, data rows = {}'.format(indent, total_nrows, data_nrows)
        self.print_status(text, status)

    def print_empty_columns(self):
        """
        Print any columns that are wholly empty
        """

        print('Empty columns:')
        indent = ' ' * INDENT

        for msg in self.check_empty_columns():
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

        for msg in self.check_empty_rows():
            text = '{}row {} is {}empty'.format(indent, msg['y'], '' if msg['data']['is_empty'] else 'not ')

            if msg['data']['is_empty']:
                self.print_status(text, msg['status'])
            else:
                if(self.conf['verbose']):
                    self.print_status(text, msg['status'])

    def print_column_stats(self):
        """
        Print column statistics for the configured columns
        """

        print('Column stats:')
        table = [msg for msg in self.compute_column_stats()]
        self.print_msg_table(table, indent=INDENT)

    def print_column_outliers_iqr(self):
        """
        Print any outliers for the configured columns
        """

        print('Column outliers (IQR):')
        table = [msg for msg in self.check_column_outliers_iqr()]
        self.print_msg_table(table, indent=INDENT)

