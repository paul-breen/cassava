import argparse

from cassava import Cassava

DEF_OPT_DELIMITER = ','

def parse_cmdln():
    """
    Parse the command line

    :returns: An object containing the command line arguments and options
    :rtype: argparse.Namespace
    """

    epilog = """Examples

Given a CSV file with a single header row (at row 0), datetimes in the first column (column 0) to be treated as the independent variable, and three similarly-scaled dependent variables:

datetime,v1,v2,v3
31/12/2020 00:00:00,1.0,1.1,0.9
31/12/2020 00:01:00,1.0,1.2,1.1

Then the following invocation will allow all three variables to be plotted on a single plot as a timeseries:

python3 plot_csv.py -H 0 -i 1 -x 0 -d -f '%d/%m/%Y %H:%M:%S' -y 1,2,3 input.csv
"""

    parser = argparse.ArgumentParser(description='plot and quality-check CSV (or similarly-delimited) data files', epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('in_file', help='input file')
    parser.add_argument('-H', '--header-row', help='row containing the header', dest='header_row', type=int, default=Cassava.DEFAULTS['header_row'])
    parser.add_argument('-i', '--first-data-row', help='first row containing data to plot', dest='first_data_row', default=Cassava.DEFAULTS['first_data_row'], type=int)
    parser.add_argument('-x', '--x-column', help='column containing values for the x-axis', dest='xcol', default=Cassava.DEFAULTS['xcol'], type=int)
    parser.add_argument('-y', '--y-column', help='column containing values for the y-axis (specify multiple columns separated by commas to plot multiple curves on y-axis)', dest='ycol', default=str(Cassava.DEFAULTS['ycol'][0]), type=str)
    parser.add_argument('-d', '--x-as-datetime', help='treat the x-axis values as datetimes', action='store_true', default=Cassava.DEFAULTS['x_as_datetime'])
    parser.add_argument('-f', '--datetime-format', help='datetime format specification', dest='datetime_format', default=Cassava.DEFAULTS['datetime_format'])
    parser.add_argument('-l', '--delimiter', help='alternative delimiter', dest='delimiter', default=Cassava.DEFAULTS['delimiter'], type=str)
    parser.add_argument('-s', '--skip-initial-space', help='ignore whitespace immediately following the delimiter', dest='skip_initial_space', action='store_true', default=Cassava.DEFAULTS['skip_initial_space'])
    parser.add_argument('-F', '--forgive', help='be forgiving when parsing numeric data', dest='forgive', action='store_true', default=Cassava.DEFAULTS['forgive'])
    parser.add_argument('-v', '--verbose', help='emit verbose messages', dest='verbose', action='store_true', default=Cassava.DEFAULTS['verbose'])

    args = parser.parse_args()

    # Check whether delimiter was specified as a tab.  If so, it will have
    # been escaped, so we unescape it so that it appears as a tab
    if args.delimiter == '\\t':
        args.delimiter = '\t'

    # ycol option can have multiple delimited values
    if DEF_OPT_DELIMITER in str(args.ycol):
        args.ycol = args.ycol.split(DEF_OPT_DELIMITER)

    # Ensure ycol is an int list after all processing
    args.ycol = [int(ycol) for ycol in args.ycol]

    return args

def main():
    """
    Main function
    """

    args = parse_cmdln()
    conf = Cassava.DEFAULTS.copy()

    # Grab the input file.  All remaining options go in the configuration
    in_file = args.in_file
    del args.in_file
    conf.update(vars(args))

    with Cassava(path=in_file, conf=conf) as f:
        f.read()
        f.plot()

if __name__ == '__main__':
    main()

