import argparse
import json

from cassava import Cassava, __version__

DEF_OPT_DELIMITER = ','
DEF_OPT_RANGE_DELIMITER = '-'
COMMANDS = {
    'plot': {'subcommands': ['qc','stats']},
    'print': {'subcommands': ['qc','stats']}
}

def str_range_list_to_list(x, item_sep=DEF_OPT_DELIMITER, range_sep=DEF_OPT_RANGE_DELIMITER):
    """
    Convert a string range list to a list

    For example, given '1,2,3,8-12,14,17', return [1,2,3,8,9,10,11,12,14,17]

    :param x: String, possibly including a range specification
    :type x: str
    :param item_sep: The separator between items in the string
    :type item_sep: str
    :param range_sep: The separator between range end-points in the string
    :type range_sep: str
    :returns: The fully actualised list
    :rtype: list
    """

    y = []
    items = x.split(item_sep)

    for i in items:
        if range_sep in i:
            lim = i.split(range_sep)
            y.extend([r for r in range(int(lim[0]), int(lim[1])+1)])
        else:
            y.append(i)

    return y

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

Then the following invocation will allow all three variables to be plotted on a single plot as a timeseries, to allow a visual QC inspection:

python3 -m cassava -H 0 -i 1 -x 0 -d -f '%d/%m/%Y %H:%M:%S' -y 1,2,3 plot qc input.csv

and this will print a QC report, instead of plotting:

python3 -m cassava -H 0 -i 1 -x 0 -d -f '%d/%m/%Y %H:%M:%S' -y 1,2,3 print qc input.csv
"""

    parser = argparse.ArgumentParser(description='plot and quality-check CSV (or similarly-delimited) data files', epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter, prog='cassava')

    # Add commands.  These will appear before positional arguments on the
    # command line
    subparsers = parser.add_subparsers(help="commands")
    parser.set_defaults(command=None)

    for command in COMMANDS:
        sub = subparsers.add_parser(command)
        sub.set_defaults(command=command)
        subsubparsers = sub.add_subparsers(help="subcommands")

        sub.set_defaults(subcommand=COMMANDS[command]['subcommands'][0])

        for subcommand in COMMANDS[command]['subcommands']:
            subsub = subsubparsers.add_parser(subcommand)
            subsub.set_defaults(subcommand=subcommand)

    parser.add_argument('in_file', help='input file')
    parser.add_argument('-H', '--header-row', help='row containing the header', dest='header_row', type=int, default=Cassava.DEFAULTS['header_row'])
    parser.add_argument('-i', '--first-data-row', help='first row containing data to plot', dest='first_data_row', default=Cassava.DEFAULTS['first_data_row'], type=int)
    parser.add_argument('-C', '--common-header-row', help='shorthand for -H 0 -i 1, as this is such a commonplace configuration', action='store_true')
    parser.add_argument('-x', '--x-column', help='column containing values for the x-axis', dest='xcol', default=Cassava.DEFAULTS['xcol'], type=int)
    parser.add_argument('-y', '--y-column', help='column containing values for the y-axis (specify multiple columns separated by commas and/or as ranges to plot multiple curves on y-axis)', dest='ycol', default=str(Cassava.DEFAULTS['ycol'][0]), type=str)
    parser.add_argument('-d', '--x-as-datetime', help='treat the x-axis values as datetimes', action='store_true', default=Cassava.DEFAULTS['x_as_datetime'])
    parser.add_argument('-f', '--datetime-format', help='datetime format specification', dest='datetime_format', default=Cassava.DEFAULTS['datetime_format'])
    parser.add_argument('-m', '--missing-value', help='value to be treated as missing data', dest='missing_value', default=Cassava.DEFAULTS['missing_value'])
    parser.add_argument('-l', '--delimiter', help='alternative delimiter', dest='delimiter', default=Cassava.DEFAULTS['delimiter'], type=str)
    parser.add_argument('-s', '--skip-initial-space', help='ignore whitespace immediately following the delimiter', dest='skip_initial_space', action='store_true', default=Cassava.DEFAULTS['skip_initial_space'])
    parser.add_argument('-F', '--forgive', help='be forgiving when parsing numeric data', dest='forgive', action='store_true', default=Cassava.DEFAULTS['forgive'])

    parser.add_argument('-N', '--plot-in-n-columns', help='number of columns for a multi-plot grid', dest='ncols', default=None, type=int)
    parser.add_argument('-k', '--tukey-fence-factor', help="factor to multiply IQR by in Tukey's rule", dest='k', default=1.5, type=float)
    parser.add_argument('-O', '--hide-outliers', help="don't show outliers on stats plots", dest='showfliers', action='store_false', default=True)
    parser.add_argument('-P', '--plot-options', help="options for the plot, specified as a simple JSON object", dest='plot_opts', default={}, type=json.loads)
    parser.add_argument('-S', '--scatter-plot', help="set plot options (see -P) to produce a scatter plot", dest='plot_opts', action='store_const', const={'marker': '.', 'ls': ''})

    parser.add_argument('-v', '--verbose', help='emit verbose messages', dest='verbose', action='store_true', default=Cassava.DEFAULTS['verbose'])
    parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    # This is shorthand for a common header configuration
    if args.common_header_row:
        args.header_row = 0
        args.first_data_row = 1

    # Check whether delimiter was specified as a tab.  If so, it will have
    # been escaped, so we unescape it so that it appears as a tab
    if args.delimiter == '\\t':
        args.delimiter = '\t'

    # ycol option can have multiple delimited values
    if DEF_OPT_DELIMITER in str(args.ycol) or DEF_OPT_RANGE_DELIMITER in str(args.ycol):
        args.ycol = str_range_list_to_list(args.ycol)

    # ycol must be a list, so that we don't iterate over digits in a string
    if not isinstance(args.ycol, list):
        args.ycol = [args.ycol]

    # Ensure ycol is an int list after all processing
    args.ycol = [int(ycol) for ycol in args.ycol]

    return args

def main():
    """
    Main function
    """

    args = parse_cmdln()
    conf = Cassava.DEFAULTS.copy()

    # All options go in the configuration
    in_file = args.in_file
    command = args.command
    subcommand = args.subcommand
    del args.in_file
    del args.command
    del args.subcommand
    conf.update(vars(args))

    with Cassava(path=in_file, conf=conf) as f:
        f.read()

        if command == 'plot':
            if subcommand == 'qc':
                if args.ncols:
                    layout = f.compute_multi_plot_layout(args.ncols)
                else:
                    layout = (1,1)

                f.plot(layout=layout, opts=args.plot_opts)
            elif subcommand == 'stats':
                f.plot_stats(k=args.k, showfliers=args.showfliers)
            else:
                raise ValueError('Unsupported subcommand')
        elif command == 'print':
            if subcommand == 'qc':
                f.print_qc()
            elif subcommand == 'stats':
                f.print_stats(k=args.k)
            else:
                raise ValueError('Unsupported subcommand')
        else:
            raise ValueError('Unsupported command')

if __name__ == '__main__':
    main()

