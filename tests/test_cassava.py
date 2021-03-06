import os
import datetime

import pytest
import numpy as np

import cassava

base = os.path.dirname(__file__)

def test_version():
    assert cassava.__version__ == '0.2.1'

def dt_strs_to_dts(ds, fmt='%Y-%m-%dT%H:%M:%S'):
    return [datetime.datetime.strptime(d, fmt) for d in ds]

@pytest.fixture
def init_cassava():
    def _init_cassava(opts):
        conf = cassava.Cassava.DEFAULTS.copy()
        conf.update(opts)
        f = cassava.Cassava(conf=conf)

        return f

    return _init_cassava

@pytest.fixture
def dummy_rows(ncolumns=10, nrows=10):
    rows = []

    header_row = [f'v{i}' for i in range(ncolumns)]
    rows.append(header_row)

    for j in range(nrows):
        row = [j * ncolumns + i for i in range(ncolumns)]
        rows.append(row)

    return rows
 
@pytest.fixture
def dummy_cassava(init_cassava, dummy_rows):
    opts = {
        'header_row': 0,
        'first_data_row': 1
    }
    f = init_cassava(opts)
    f.rows = dummy_rows
    f.store_header()

    return f
  
@pytest.fixture
def dummy_unconfigured_cassava(init_cassava, dummy_rows):
    opts = {}
    f = init_cassava(opts)
    f.rows = dummy_rows
    f.store_header()

    return f
 
@pytest.fixture
def cells_missing_cassava():
    in_file = base + '/data/cells-missing.csv'
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1,2,3,4],
        'x_as_datetime': True
    }
    conf = cassava.Cassava.DEFAULTS.copy()
    conf.update(opts)

    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()

        yield f
 
def test_store_header_ok(dummy_cassava):
    f = dummy_cassava
    assert f.header_row == ['v0','v1','v2','v3','v4','v5','v6','v7','v8','v9']

def test_store_header_skips_unconfigured_header_row_ok(dummy_unconfigured_cassava):
    f = dummy_unconfigured_cassava
    assert f.header_row == []

def test_get_column_labels_from_header_ok(dummy_cassava):
    f = dummy_cassava
    labels = f.get_column_labels_from_header([0,2])
    assert labels == ['v0','v2']

def test_get_column_labels_from_header_skips_unconfigured_header_row_ok(dummy_unconfigured_cassava):
    f = dummy_unconfigured_cassava
    labels = f.get_column_labels_from_header([0,2])
    assert labels == []

def test_get_column_data_ok(dummy_cassava):
    f = dummy_cassava
    data = f.get_column_data(0)
    assert data == [0,10,20,30,40,50,60,70,80,90]

def test_get_column_data_first_data_row_beyond_data(dummy_cassava):
    f = dummy_cassava
    f.conf['first_data_row'] = 11
    data = f.get_column_data(0)
    assert data == []

def test_get_column_data_invalid_column(dummy_cassava):
    f = dummy_cassava

    with pytest.raises(IndexError):
        data = f.get_column_data(11)

def test_get_column_data_invalid_column_forgive_mode(dummy_cassava):
    """
    In 'forgive' mode, invalid data (those that throw an exception) are
    replaced with `exc_value` (default is NaN).  In the case where an invalid
    column index is given, this will result in a list consisting solely of NaNs
    """

    f = dummy_cassava
    f.conf['forgive'] = True
    data = f.get_column_data(11)
    assert data == [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]

def test_get_column_data_column_invalid_column_forgive_mode_custom_exc_value(dummy_cassava):
    f = dummy_cassava
    f.conf['forgive'] = True
    data = f.get_column_data(11, exc_value=-999)
    assert data == [-999,-999,-999,-999,-999,-999,-999,-999,-999,-999]

def test_get_column_data_datetime_ok():
    in_file = base + '/data/dt-valid.csv'
    conf = cassava.Cassava.DEFAULTS.copy()
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1],
        'x_as_datetime': True
    }
    conf.update(opts)
    dts = ['1999-12-31T23:50:00','1999-12-31T23:51:00','1999-12-31T23:52:00','1999-12-31T23:53:00','1999-12-31T23:54:00','1999-12-31T23:55:00','1999-12-31T23:56:00','1999-12-31T23:57:00','1999-12-31T23:58:00','1999-12-31T23:59:00']
    expected = dt_strs_to_dts(dts, fmt='%Y-%m-%dT%H:%M:%S')

    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()

        # This is the underlying function of get_x_axis_data()
        x = f.get_column_data(f.conf['xcol'], f.conf['datetime_format'], func=datetime.datetime.strptime)
        assert x == expected

def test_get_x_axis_data_datetime_ok():
    in_file = base + '/data/dt-valid.csv'
    conf = cassava.Cassava.DEFAULTS.copy()
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1],
        'x_as_datetime': True
    }
    conf.update(opts)
    dts = ['1999-12-31T23:50:00','1999-12-31T23:51:00','1999-12-31T23:52:00','1999-12-31T23:53:00','1999-12-31T23:54:00','1999-12-31T23:55:00','1999-12-31T23:56:00','1999-12-31T23:57:00','1999-12-31T23:58:00','1999-12-31T23:59:00']
    expected = dt_strs_to_dts(dts, fmt='%Y-%m-%dT%H:%M:%S')

    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()
        x = f.get_x_axis_data()
        assert x == expected

def test_get_x_axis_data_invalid_date():
    in_file = base + '/data/dt-invalid-date.csv'
    conf = cassava.Cassava.DEFAULTS.copy()
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1],
        'x_as_datetime': True
    }
    conf.update(opts)

    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()

        with pytest.raises(ValueError):
            x = f.get_x_axis_data()

def test_get_x_axis_data_invalid_time():
    in_file = base + '/data/dt-invalid-time.csv'
    conf = cassava.Cassava.DEFAULTS.copy()
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1],
        'x_as_datetime': True
    }
    conf.update(opts)

    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()

        with pytest.raises(ValueError):
            x = f.get_x_axis_data()

def test_get_x_axis_data_missing_datetime():
    in_file = base + '/data/dt-missing.csv'
    conf = cassava.Cassava.DEFAULTS.copy()
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1],
        'x_as_datetime': True
    }
    conf.update(opts)

    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()

        with pytest.raises(ValueError):
            x = f.get_x_axis_data()

def test_get_x_axis_data_different_datetime_format():
    in_file = base + '/data/dt-different-format.csv'
    conf = cassava.Cassava.DEFAULTS.copy()
    opts = {
        'header_row': 0,
        'first_data_row': 1,
        'xcol': 0,
        'ycol': [1],
        'x_as_datetime': True
    }
    conf.update(opts)

    # The datetime is in a different format to the default.  Ensure this is
    # caught, and then change the format and try again
    with cassava.Cassava(path=in_file, conf=conf) as f:
        f.read()

        with pytest.raises(ValueError):
            x = f.get_x_axis_data()

        f.conf['datetime_format'] = '%d/%m/%Y %H:%M:%S'
        x = f.get_x_axis_data()

def test_compute_stats(dummy_cassava):
    f = dummy_cassava
    f.conf['ycol'] = [0]
    y = f.get_y_axis_data(f.conf['ycol'][0])
    stats = f.compute_stats(y)

def test_compute_stats_copes_with_some_nans(dummy_cassava):
    f = dummy_cassava
    f.conf['ycol'] = [0]
    f.conf['forgive'] = True
    y = f.get_y_axis_data(f.conf['ycol'][0])

    # Some NaNs in the data should be handled OK, with the stats being
    # computed on the remaining data
    y[2] = np.nan
    stats = f.compute_stats(y)

def test_compute_stats_copes_with_wholly_nans(dummy_cassava):
    f = dummy_cassava
    f.conf['ycol'] = [11]
    f.conf['forgive'] = True
    y = f.get_y_axis_data(f.conf['ycol'][0])

    # If the data are solely NaNs, then a warning is emitted
    with pytest.warns(RuntimeWarning):
        stats = f.compute_stats(y)

def test_compute_multi_plot_layout():
    conf = cassava.Cassava.DEFAULTS.copy()
    f = cassava.Cassava(conf=conf)

    # Default ncols=2, so this will push the last column onto the next row
    f.conf['ycol'] = [2,3,4]
    layout = f.compute_multi_plot_layout()
    assert layout == (2,2)

    # All columns will fit on a single row
    f.conf['ycol'] = [2,3,4]
    layout = f.compute_multi_plot_layout(ncols=3)
    assert layout == (1,3)

    # ncols > actual column count, so will be overridden to 2
    f.conf['ycol'] = [2,3]
    layout = f.compute_multi_plot_layout(ncols=3)
    assert layout == (1,2)

def test_check_column_counts(dummy_cassava):
    f = dummy_cassava
    f.conf['ycol'] = [0]
    f.conf['forgive'] = True
    f.rows[2] = [1,2,3]                # Make the second data row short
    msgs = [msg for msg in f.check_column_counts()]

    expected  = {'x': None, 'y': 1, 'data': {'is_first_row': True, 'ncols': 10}, 'status': cassava.CassavaStatus.ok}
    assert msgs[0] == expected

    expected  = {'x': None, 'y': 2, 'data': {'is_first_row': False, 'ncols': 3}, 'status': cassava.CassavaStatus.error}
    assert msgs[1] == expected

def test_check_empty_columns(cells_missing_cassava):
    f = cells_missing_cassava
    msgs = [msg for msg in f.check_empty_columns()]

    for x in range(5, 8):
        expected = {'x': x, 'y': None, 'data': {'is_empty': True}, 'status': cassava.CassavaStatus.error}
        assert msgs[x] == expected

def test_check_empty_rows(cells_missing_cassava):
    f = cells_missing_cassava
    msgs = [msg for msg in f.check_empty_rows()]

    for y in range(11, 16):
        expected = {'x': None, 'y': y, 'data': {'is_empty': True}, 'status': cassava.CassavaStatus.error}
        assert msgs[y] == expected

def test_check_column_outliers_iqr(dummy_cassava):
    f = dummy_cassava
    f.conf['ycol'] = [1]
    f.rows[2][1] = 1000                # Make cell 1,2 an outlier
    msgs = [msg for msg in f.check_column_outliers_iqr()]

    expected = {'x': 1, 'y': 2, 'data': {'value': 1000}, 'status': cassava.CassavaStatus.error}
    assert msgs[0] == expected

