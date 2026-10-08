# Changelog

## [v0.5.0] - 2026-10-08

### Added

- Add support for specifying the plot figure size
- Add support for saving a plot (qc or stats) to a file rather than showing it
- Add support for a user-specified float format specifier for the print-stats table

### Changed

- Update project dependencies (minimium version of Python is now 3.10)
- Update box plot parameter name (labels is now tick_labels) - required by newer version of matplotlib (3.10.9)

## [v0.4.0] - 2024-03-10

### Added

- Add option to specify a comment character that introduces a file header section that is to be skipped
- Add support for alternative character encodings

### Changed

- As part of QC, emit a warning if input is UTF-8 encoded and contains a BOM
- Apply the -O option (don't show outliers) to the print stats command
- Include hint to check file character encoding when catching UnicodeDecodeError exception

## [v0.3.0] - 2023-01-08

### Added

- Add a console script to wrap the package main() function
- Add support for tuning plot options - in general, and specifically for making a scatter plot
- Add support for specifying how missing values are represented in the data
- Add support for specifying ranges for the y-columns

## [v0.2.0] - 2021-11-11

### Fixed

- Bugfix.  Specifying a single y-column where column index > 9 fails

### Changed

- Provide a shorthand option for the common case of -H 0 -i 1
- Provide focused exception messages with data context

## [v0.1.0] - 2021-09-28

### Added

- Add a functional main with different 'modes' for calling the plot or print, qc or stats, functions
- Add function to plot column statistics
- Add function to check and print outliers (Tukey's rule: 1.5 * IQR)
- Add simple function to report row counts information, such as total rows and data rows
- Add functions to compute and print column statistics
- Add kwarg to specify exception value (missing data) when reading data for the y-axis columns in forgive mode
- Add generator and colour-coded print functions for QC checks

### Changed

- print_column_outliers_iqr() should take an optional factor k to pass to the underlying check function, and so that it can print this factor in its header
- Provide option to plot multiple columns on individual plots in a grid
- Plot function should optionally not call show() to allow further customisation
- The 'forgive' mode should also apply to the x-axis
- Initial commit

