# Changelog

## v0.3.0 - 2023-01-28
- Reformatted package to use `poetry` for dependency management
- Removed `link` and `regional` from uis_datasets.csv and from 
functions and methods returning info. `link` for a dataset 
can still be accessed through the `UIS` class.

## v0.2.0 - 2023-01-25
- Created tests to cover `common` and `uis` modules
- Reformatted uis module function to read CSVs from zip file
- Reformatted UIS class attributes to be set in `__init__` method

## v0.1.2 - 2022-12-10
- Fixed bug preventing regional data from being returned
- Optimized metadata retrieval

## v0.1.1 - 2022-12-09
- Fixed a bug for typing caused in python 3.8

## v0.1.0 - 2022-12-09
- Initial release of `unesco_reader` `uis` module

## v0.0.1 - 2022-09-16

- Initial release for testing