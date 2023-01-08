import os
import sys
import argparse

import pytest

import cassava.__main__ as m

base = os.path.dirname(__file__)

def test_parse_cmdln_single_y_column_single_digit():
    sys.argv = ['main', '-y', '3', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.ycol == [3]

def test_parse_cmdln_single_y_column_multiple_digits():
    # After comma-splitting, it should still be [32], not [3,2]
    sys.argv = ['main', '-y', '32', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.ycol == [32]

def test_parse_cmdln_multiple_y_columns_single_digits():
    sys.argv = ['main', '-y', '3,2', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.ycol == [3,2]

def test_parse_cmdln_multiple_y_columns_multiple_digits():
    sys.argv = ['main', '-y', '32,33', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.ycol == [32,33]

def test_parse_cmdln_multiple_y_columns_range():
    sys.argv = ['main', '-y', '3-6', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.ycol == [3,4,5,6]

def test_parse_cmdln_multiple_y_columns_individual_and_range():
    sys.argv = ['main', '-y', '1,2,3,8-12,14,17', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.ycol == [1,2,3,8,9,10,11,12,14,17]

def test_parse_cmdln_escaped_tab_delimiter():
    sys.argv = ['main', '-l', '\\t', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.delimiter == '\t'

def test_parse_cmdln_unescaped_tab_delimiter():
    sys.argv = ['main', '-l', '\t', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.delimiter == '\t'

def test_parse_cmdln_common_header_row():
    sys.argv = ['main', '-C', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.common_header_row is True
    assert args.header_row == 0
    assert args.first_data_row == 1

def test_parse_cmdln_common_header_row_overrides_opts():
    sys.argv = ['main', '-C', '-H', '7', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.common_header_row is True
    assert args.header_row == 0
    assert args.first_data_row == 1

    sys.argv = ['main', '-C', '-i', '8', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.common_header_row is True
    assert args.header_row == 0
    assert args.first_data_row == 1

    sys.argv = ['main', '-C', '-H', '7', '-i', '8', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.common_header_row is True
    assert args.header_row == 0
    assert args.first_data_row == 1

def test_parse_cmdln_when_no_common_header_row_instead_uses_opts():
    sys.argv = ['main', '-H', '7', '-i', '8', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.common_header_row is False
    assert args.header_row == 7
    assert args.first_data_row == 8

def test_parse_cmdln_no_plot_options():
    sys.argv = ['main', '-C', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.plot_opts == {}

def test_parse_cmdln_scatter_plot_options():
    sys.argv = ['main', '-C', '-S', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.plot_opts == {'marker': '.', 'ls': ''}

def test_parse_cmdln_custom_plot_options():
    json_opt_arg = '{"lw": 4, "c": "green", "ls": "--"}'
    sys.argv = ['main', '-C', '-P', json_opt_arg, 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.plot_opts == {'lw': 4, 'c': 'green', 'ls': '--'}

def test_main_print_qc():
    in_file = base + '/data/dt-valid.csv'
    sys.argv = ['main', '-H', '0', '-i', '1', '-y', '1', 'print', 'qc', in_file]
    args = m.parse_cmdln()
    m.main()

