# cassava

Cassava is a package for reading, plotting and quality-checking CSV files.  It's primary purpose is for giving a quick, first assessment of a CSV file, highlighting common quality issues such as wholly empty columns or rows, differing column counts and basic outlier detection.  The package can be integrated as part of a larger workflow, or used directly from the command line with a simple but functional command line interface (CLI).

## Install

The package can be installed from PyPI (note the package distribution name):

```bash
$ pip install cassava-csv
```

## From the command line

The cassava CLI runs in a number of modes.  The main commands are `plot`, to visually inspect a file, and `print`, to print its findings to `stdout`.  For each of these commands, there are two subcommands; `qc` for producing a QC plot or report, and `stats` for producing a summary statistics plot or report.  There are then many options to specify how to read and process the CSV file, e.g., whether it has a header row, which column to use for the x-axis in the plot, which columns to use for the y-axis in the plot etc.

### Synopsis

The general usage is to call the cassava package main, followed by any options, then the command (one of `plot`, `print`), a subcommand (one of `qc`, `stats`) and finally the input CSV file.  Note that the subcommand is optional and if not supplied, will default to `qc`.

```bash
$ python -m cassava [opts] command [subcommand] input.csv
```

Specifying the `--help` option, will print the CLI usage and quit.  To get help on a given command, specify the `--help` option after that command.  For example:

```bash
$ python -m cassava plot --help 
```

Note that the options are global to all modes (commands and subcommands), even when some only really make sense for a given mode.  This is by design, and to make for an uncomplicated CLI, which lends itself well to just pressing "up arrow" in the shell and using the same options but in a different mode.

### Options

```
  -h, --help            show this help message and exit
  -H HEADER_ROW, --header-row HEADER_ROW
                        row containing the header
  -i FIRST_DATA_ROW, --first-data-row FIRST_DATA_ROW
                        first row containing data to plot
  -x XCOL, --x-column XCOL
                        column containing values for the x-axis
  -y YCOL, --y-column YCOL
                        column containing values for the y-axis (specify
                        multiple columns separated by commas to plot multiple
                        curves on y-axis)
  -d, --x-as-datetime   treat the x-axis values as datetimes
  -f DATETIME_FORMAT, --datetime-format DATETIME_FORMAT
                        datetime format specification
  -l DELIMITER, --delimiter DELIMITER
                        alternative delimiter
  -s, --skip-initial-space
                        ignore whitespace immediately following the delimiter
  -F, --forgive         be forgiving when parsing numeric data
  -N NCOLS, --plot-in-n-columns NCOLS
                        number of columns for a multi-plot grid
  -k K, --tukey-fence-factor K
                        factor to multiply IQR by in Tukey's rule
  -O, --hide-outliers   don't show outliers on stats plots
  -v, --verbose         emit verbose messages
```

### Examples

Given the following CSV file:

```
Datetime,Temperature,Relative_Humidity,Sea_Level_Pressure,Wind_Speed,,,
1999-12-20T00:00:00,-10,40,990,,,,
1999-12-21T00:00:00,-11,51,971,,,,
1999-12-22T00:00:00,-10,62,952,17,,,
1999-12-23T00:00:00,-10,56,956,,,,
1999-12-24T00:00:00,-12,78,,,,,
1999-12-25T00:00:00,-11,77,995,,,,
1999-12-26T00:00:00,-11,70,986,,,,
1999-12-27T00:00:00,-12,47,966,22,,,
1999-12-28T00:00:00,-11,48,990,230,,,
1999-12-29T00:00:00,-11,57,967,25,,,
,,,,,,,
,,,,,,,
,,,,,,,
,,,,,
,,,,,,,,,,,
```

we can see a number of issues.  It's likely that this was exported from a spreadsheet, as it has a number of trailing empty columns, and trailing empty rows.  In addition, there's been some subsequent "finger trouble", as the last two empty rows have differing column counts.  There are wholly empty columns, as well as some sparse, but not wholly empty columns, and at least one highly probable outlier.

Often a quick plot will tell us a lot about our data, so let's try that.  If our CSV file contained only numeric columns, with no header, then we could simply do:

```bash
$ python -m cassava plot data.csv

...

ValueError: could not convert string to float: 'Datetime'
```

however in this case, the default y-axis column (0) contains ISO datetime strings, and the first row is a header row, so cassava will raise the above exception.

At this point, we could replace the `plot` command with `print`, and get some useful QC information about the file, as the `print` command doesn't need to interpret the data as much as the `plot` command does.

A key feature of cassava is that you can run it in "forgive" mode (`-F`), where it will simply replace any invalid numeric values with a placeholder value (the default is NaN).  By default the forgive mode is `False`, otherwise it would mask quality issues with the data, and so defeat the central point of cassava!  However, in cases where we just want to get a first look at the data, the forgive mode is invaluable.  So let's do that:

```bash
$ python -m cassava -F plot data.csv
```

This produces a plot, but it's empty!  This is because the default y-axis column contains datetime strings, and so the forgive mode has skipped over all of them.  Let's specify the y-axis data (`-y`) as column 1:

```bash
$ python -m cassava -F -y 1 plot data.csv
No handles with labels found to put in legend.
```

That works, and produces a line plot of the `Temperature` data.  This is a minimal working command line for plotting this file, but we can do better!

Let's provide a few more options for processing.  First we can address the notification that `matplotlib` emitted about no labels for the legend.  We can tell cassava that the first row (row 0 - all cassava coordinates have origin zero) is a header row (`-H 0`) and the first data row is the next row (`-i 1`).  Having these as two separate options gives us flexibility for cases where the CSV file may have a complex structured header section.  Furthermore, we note that this is a timeseries, so we can provide options to cassava so that it can treat it as such.  We specify the x-axis data as column 0 (`-x 0`), and tell cassava to treat the x-axis as a datetime column (`-d`).  The datetime format is ISO 8601, which is the cassava default, so we don't need to specify the datetime format.  Trying this also raises an exception:

```bash
$ python -m cassava -H 0 -i 1 -x 0 -d -y 1 plot qc data.csv

...

ValueError: Failed to convert x-column at row 11 to datetime: ['', '', '', '', '', '', '', '']
```

This is valuable QC information, as it tells us exactly the row that failed to parse as a datetime.  Particularly useful if the file is large.  At this point we could address the issue directly, by editing the CSV file accordingly (in this example, by removing the empty trailing rows), or just run cassava without specifying the x-axis data (cassava then defaults to integer indices).  Let's do the latter:

```bash
$ python -m cassava -H 0 -i 1 -y 1 plot qc data.csv

...

ValueError: could not convert string to float: '' 
```

More valuable QC information!  The empty rows at the bottom of the file cause this exception.  Let's reintroduce the forgive option.  This allows us to get on with evaluating the data, but of course eventually, we will remove those empty rows.

```bash
$ python -m cassava -H 0 -i 1 -y 1 -F plot qc data.csv
```

This gives us a nice working command line.  Now let's plot all the numeric columns.  We can specify multiple columns for the y-axis by giving a comma-separated list:

```bash
$ python -m cassava -H 0 -i 1 -y 1,2,3,4 -F plot qc data.csv
```

This works, but as the `Sea_Level_Pressure` values are far greater than the other columns, it's not easy to pick out the detail.  We could drop the `Sea_Level_Pressure` column from the y-axis list (`-y 1,2,4`).  This is an improvement, but the outlier in `Wind_Speed` is now causing problems.  In cases where your data are of greatly differing scales, it's better to plot multiple curves on separate plots.  This can be achieved using the `-N NCOLS` option, which tells cassava to plot a grid of NCOLS-wide plots:

```bash
$ python -m cassava -H 0 -i 1 -y 1,2,3,4 -F -N 2 plot qc data.csv
```

This plots a 2x2 grid of plots, with each variable in its own plot, with a suitably-scaled y-axis.

For any of the working command lines above, we could replace the `qc` subcommand with the `stats` subcommand, to get summary statistics plots for the specified y-columns.  Let's do that for the last command line.  The first thing to note, is that the `-N 2` option is not required for stats plots.  However, as noted above, it doesn't hurt to leave it there and thus allows for rapid tweak/repeat cycles:

```bash
$ python -m cassava -H 0 -i 1 -y 1,2,3,4 -F -N 2 plot stats data.csv
```

This produces three plots for each specified y-column: a density plot of the distribution of the data, a line plot of the data including bounds to highlight potential outliers, and a boxplot of the data.  In this example, the outlier in the `Wind_Speed` is clearly identified.  If an outlier is so large that it dominates the remaining data, then we can instruct cassava to not show outliers (`-O`), thereby revealing the detail:

```bash
$ python -m cassava -H 0 -i 1 -y 1,2,3,4 -F -N 2 -O plot stats data.csv
```

Similarly, we can replace the `plot` command with the `print` command.  Let's do that (again, no need to remove extraneous options):

```bash
$ python -m cassava -H 0 -i 1 -y 1,2,3,4 -F -N 2 -O print qc data.csv 
Column counts:
    first row 1: ncols = 8
    row 14: ncols = 6
    row 15: ncols = 12
Row counts:
    total rows = 16, data rows = 15
Empty columns:
    column 5 is empty
    column 6 is empty
    column 7 is empty
Empty rows:
    row 11 is empty
    row 12 is empty
    row 13 is empty
    row 14 is empty
    row 15 is empty
```

which produces the above QC report.  The output is colour-coded using a traffic light system, thereby highlighting quality issues.  For the `Column counts` section, only those rows which have differing column counts to the first data row are listed, so ideally in good data, you would only see the column count of the first data row.  Running the above in verbose mode (`-v`) would list all column counts, irrespective of whether they agree with the first data row or not.

We can also print summary statistics for the specified columns, and list any cells that contain suspected outlier values:

```bash
$ python -m cassava -H 0 -i 1 -y 1,2,3,4 -F -N 2 -O print stats data.csv 
Column stats:
    column min     mean    max     q1      median  q3      std 
    1      -12     -11     -10     -11     -11     -10     0.7 
    2      40      59      78      49      56      68      12  
    3      9.5e+02 9.7e+02 1e+03   9.7e+02 9.7e+02 9.9e+02 15  
    4      17      74      2.3e+02 21      24      76      90  
Column outliers (1.5 * IQR):
    column,row value   
    4,9        2.3e+02 
```

## Using the package

To use cassava in your own code, setup a configuration `dict`, and then call the required methods from within the `Cassava` context manager:

```python
from cassava import Cassava

filename = 'data.csv'
conf = Cassava.DEFAULTS.copy()
opts = {
    'header_row': 0,
    'first_data_row': 1,
    'ycol': [1,2,3,4],
    'forgive': True
}
conf.update(opts)

with Cassava(path=filename, conf=conf) as f:
    f.read()
    f.plot()
```

### Configuration dict

As can be seen above, cassava requires a fully-specified configuration `dict`, so the easiest way to ensure this is to take a copy of the `Cassava` class `DEFAULTS dict`, and then override any specific configuration items.  The default configuration `dict` is:

```python
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
```

* header_row: Integer row index of the input file's header
* first_data_row: Integer row index of the input file's first data row
* xcol: Integer column index from the input file for the plot x-axis
* ycol: Integer column index `list` from the input file for the plot y-axis
* x_as_datetime: Consider the x-axis data as datetime strings
* datetime_format: `datetime.datetime.strptime()` format specification
* delimiter: Column delimiter character
* skip_initial_space: Skip any spaces following the delimiter character
* forgive: Forgive mode. Replace invalid numeric values with placeholder (NaN)
* verbose: Print extra messages in `print` mode methods

Note that all cassava column/row coordinates have origin zero.

#### Persist custom default configuration for a session

A feature of the `DEFAULTS dict` is that, because it's a class variable (rather than an instance variable), you can set per `import` session defaults for all instances by directly updating `DEFAULTS`:

```python
from cassava import Cassava

filenames = ['data1.csv','data2.csv']
opts = {
    'header_row': 0,
    'first_data_row': 1
}
Cassava.DEFAULTS.update(opts)

for filename in filenames:
    with Cassava(path=filename) as f:
        f.read()
        f.plot()
```

Note that if no configuration `dict` is passed via the `conf` kwarg, then cassava uses `DEFAULTS` instead.

### The cassava object

The `Cassava` object has the following instance variables:

```python
        self.path = path
        self.conf = conf or self.DEFAULTS
        self.fp = None
        self.header_row = []
        self.rows = []
```

`path` and `conf` are the input file path `str` and the configuration `dict` that are (optionally) passed to the constructor, as shown in the above examples.  `fp` is the file pointer for the input file.  `header_row` (a `list`) holds the (optional) header row, parsed from the input data, and `rows` (a `list` of `list`s) contains the data rows parsed from the input data.

### Reading input data

The easiest way to get data into cassava, is by using it as a context manager:

```python
with Cassava(path=filename, conf=conf) as f:
    f.read()
    f.plot_stats()
```

however, you can use the `open/close` methods directly, should you wish:

```python
c = Cassava(conf=conf)
c.open(path=filename)
c.read()
c.print_qc()
c.close()
```

As noted in the previous section, the `header_row` and `rows` attributes hold the header row and data rows parsed from the input data.  Hence you could also directly set `rows` (and optionally `header_row`), rather than reading them from a file using the `read` method, and still be able to make use of the methods that cassava provides.

#### Reading input data with different delimiters

Although by default, cassava is setup to read CSV data, it can actually read any similarly-delimited tabular data.  This is controlled by the `delimiter` configuration item.  For instance a space (`conf['delimiter'] = ' '`) or a tab (`conf['delimiter'] = '\t'`).  Note that if the columns are separated by multiple spaces (e.g. a fixed width format), then setting `conf['skip_initial_space'] = True` will consume all spaces between the columns.

### Analysing the data

Once we have the data in cassava, we can produce quick-look plots, generate QC reports and compute summary statistics.

#### Plot the data

To give an initial exploratory look at the data and assess any QC issues, we can simply plot our dependent variables (our `ycol` columns) by calling `plot()`:

```python
    f.conf['ycol'] = [1,2,3,4]
    f.plot()
```

Our input file may contain an independent variable (e.g. datetime) which we can use for our `xcol` column:

```python
    f.conf['xcol'] = 0
    f.conf['ycol'] = [1,2,3,4]
    f.plot()
```

If our dependent variables contain data with differing scales, we can choose to plot them as separate subplots, rather than all on a single plot with a shared y-axis.  We do this by providing a `layout` tuple specifying an `m` rows by `n` columns plot grid (where `m * n > 1`):

```python
    f.conf['ycol'] = [1,2,3,4]
    f.plot(layout=(2,2))
```

Often we don't care how many rows the plot grid requires, rather just how many columns wide the grid should be, so we can use the `compute_multi_plot_layout` method to compute our `layout` for us, given our desired number of columns:

```python
    f.conf['ycol'] = [1,2,3,4]
    f.plot(layout=f.compute_multi_plot_layout(2))
```

which will produce a 2x2 plot grid.

To allow some customisation of the plot, we can use the `opts` kwarg.  This takes a `dict`, and can contain any plot kwargs accepted by `matplotlib`:

```python
    f.plot(opts={'lw': 4, 'c': 'green', 'ls': '--'})
```

In addition, we can defer the showing of the plot via the `show` kwarg.  This allows us to do further customisation of the plot before showing it.  Note that to do this, we have to `import matplotlib` and call `show()` ourselves:

```python
import matplotlib.pyplot as plt

    fig, axs = f.plot(show=False)
    fig.suptitle(f'Meteorological Data - {filename}')
    plt.show()
```

#### Plot summary statistics for the data

Plotting summary statistics is straightforward:

```python
    f.conf['ycol'] = [1,2,3,4]
    f.plot_stats()
```

This produces three plots for each specified y-column: a density plot of the distribution of the data, a line plot of the data including bounds to highlight potential outliers, and a boxplot of the data.

Note that the bounds in the line plot, and the whiskers in the boxplot, are scaled according to Tukey's rule and are 1.5 * IQR above/below the IQR.  We can change this scale factor via the `k` kwarg:

```python
    f.plot_stats(k=2.5)
```

If we have outliers that are so large that they dominate the remaining data, then we can choose to omit them, thereby revealing the detail:

```python
    f.plot_stats(showfliers=False)
```

By default, the number of bins to use for the density plot is automatically calculated by `matplotlib`.  We can specify these explicitly via the `bins` kwarg, which takes any form supported by `matplotlib.pyplot.hist`:

```python
    f.plot_stats(bins=10)
```

#### Print a QC report of the data

To print a QC report of the data to `stdout`, we can do:

```python
filename = 'data.csv'

with Cassava(path=filename) as f:
    f.read()
    f.print_qc()
```

which outputs the following (using our example data from above):

```bash
Column counts:
    first row 0: ncols = 8
    row 14: ncols = 6
    row 15: ncols = 12
Row counts:
    total rows = 16, data rows = 16
Empty columns:
    column 5 is empty
    column 6 is empty
    column 7 is empty
Empty rows:
    row 11 is empty
    row 12 is empty
    row 13 is empty
    row 14 is empty
    row 15 is empty
```

Note that this really requires no configuration, but assumes that our input file has no header row (and so `total rows` == `data rows`), or more generally, that the data begin on the first row (row 0).  If the file does contain a header row, or an extended header section, then we should specify the first data row index for completeness, and so generate a more accurate report:

```python
    f.conf['first_data_row'] = 1
    f.print_qc()
```

The `print_qc` method is a wrapper around the methods that produce the different output sections in the above output.  Of course, we can call these directly to produce a custom report.  For example:

```python
    f.print_column_counts()
    f.print_empty_columns()
```

#### Print a summary statistics report of the data

Here we require a little more configuration than for a QC report.  We need to specify those columns that we wish to compute summary statistics for, and, taking our example data above, we'd need to run cassava in forgive mode to skip over our trailing empty rows:


```python
    f.conf['first_data_row'] = 1
    f.conf['ycol'] = [1,4]
    f.conf['forgive'] = True
    f.print_stats()
```

which outputs the following (again using our example data from above):

```bash
Column stats:
    column min mean max     q1  median q3  std 
    1      -12 -11  -10     -11 -11    -10 0.7 
    4      17  74   2.3e+02 21  24     76  90  
Column outliers (1.5 * IQR):
    column,row value   
    4,9        2.3e+02 
```

Here we can see that cassava has identified the value in column 4 (`Wind_Speed`) and row 9 as an outlier, according to Tukey's rule.

#### Access the underlying QC and summary statistics data

Producing the plots and printing the reports is fine, but for tighter integration, we can access the underlying `message dict` that encapsulates the QC and statistics information.

##### Message dict

The general form of the `message dict` is:

```python
msg = {
    'x': x_coordinate,
    'y': y_coordinate,
    'data': data_dict,
    'status': status_code
}
```

* x: Integer column index of the input data (`None` indicates all columns)
* y: Integer row index of the input data (`None` indicates all rows)
* data: A `dict` of the output, specific to each method
* status: One of the possible status constants from `class CassavaStatus`

Note that all cassava column/row coordinates have origin zero.

For example, the `check_column_counts` method calculates the column count of each row in the input data.  In particular, it calculates and holds the column count of the configured first data row, and then compares the column counts of all subsequent rows to that of the first, and flags up if they differ.  As this is a per-row check, the x-coordinate is `None` because it refers to all columns for that row.  The column count for the first data row will always have `status = CassavaStatus.ok`:

```python
msg = {
    'x': None,
    'y': y,
    'data': {'is_first_row': True, 'ncols': len(row)},
    'status': CassavaStatus.ok
}
```

Subsequent rows will have `is_first_row = False`, and `status = CassavaStatus.ok` if their column counts agree with that of the first data row, otherwise they will have `status = CassavaStatus.error`.  (It is the `status` attribute that is used for colour-coding the output in the print functions.)

The following describe the `message['data'] dict` for each method:

* check_column_counts: {'is_first_row': Boolean, 'ncols': Integer column count}
* check_empty_columns: {'is_empty': Boolean}
* check_empty_rows: {'is_empty': Boolean}
* compute_column_stats: {'min': Minimum, 'mean': Mean, 'max': Maximum, 'q1': Quartile1, 'median': Quartile2, 'q3': Quartile3, 'std': Standard deviation}
* check_column_outliers_iqr: {'value': Cell value}

##### Examples

As an example, say we wanted to compute the percentage of empty columns and rows in our example file.  We could do:

```python
from cassava import Cassava

filename = 'data.csv'

with Cassava(path=filename) as f:
    f.read()
    ncols = len(f.rows[f.conf['first_data_row']])
    # Uncomment to only consider data rows, rather than total rows
    # f.conf['first_data_row'] = 1
    # nrows = len(f.rows) - f.conf['first_data_row']
    nrows = len(f.rows)
    empty_ncols = 0
    empty_nrows = 0

    for msg in f.check_empty_columns():
        if msg['data']['is_empty']:
            empty_ncols += 1

    for msg in f.check_empty_rows():
        if msg['data']['is_empty']:
            empty_nrows += 1

    print(f'Empty cols = {empty_ncols / ncols * 100:0.2f}%')
    print(f'Empty rows = {empty_nrows / nrows * 100:0.2f}%')
```

To print the mean of each configured column, we could do:

```python
filename = 'data.csv'
conf = Cassava.DEFAULTS.copy()
opts = {
    'header_row': 0,
    'first_data_row': 1,
    'ycol': [1,2,3,4],
    'forgive': True
}
conf.update(opts)

with Cassava(path=filename, conf=conf) as f:
    f.read()
    labels = f.get_column_labels_from_header(f.conf['ycol'])

    for msg, label in zip(f.compute_column_stats(), labels):
        print(f'{label} mean = {msg["data"]["mean"]:0.2f}')
```

