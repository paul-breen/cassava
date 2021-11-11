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

def test_parse_cmdln_escaped_tab_delimiter():
    sys.argv = ['main', '-l', '\\t', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.delimiter == '\t'

def test_parse_cmdln_unescaped_tab_delimiter():
    sys.argv = ['main', '-l', '\t', 'plot', 'qc', 'data.csv']
    args = m.parse_cmdln()
    assert args.delimiter == '\t'

def test_main_print_qc():
    in_file = base + '/data/dt-valid.csv'
    sys.argv = ['main', '-H', '0', '-i', '1', '-y', '1', 'print', 'qc', in_file]
    args = m.parse_cmdln()
    m.main()

