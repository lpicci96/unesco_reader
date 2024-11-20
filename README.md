

[![PyPI](https://img.shields.io/pypi/v/unesco_reader.svg)](https://pypi.org/project/unesco_reader/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unesco_reader.svg)](https://pypi.org/project/unesco_reader/)
[![Documentation Status](https://readthedocs.org/projects/unesco-reader/badge/?version=latest)](https://unesco-reader.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/lpicci96/unesco_reader/branch/main/graph/badge.svg)](https://codecov.io/gh/lpicci96/unesco_reader)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

# unesco_reader

Pythonic access to UNESCO data

`unesco_reader` provides simple and convenient access to data published by the UNESCO Institute of Statistics (UIS).
It offers a simple wrapper for the [UIS API](https://api.uis.unesco.org/api/public/documentation/) endpoints, and offers
added convenience including pandas support.

> __Note__: Versions `<v3.0.0` were developed before the release of the API and offered support 
> for accessing the bulk data files. This functionality has been deprecated in the latest version
> in favor of the API for programmatic access to the data. To access bulk data files, please visit
> the [bulk data download page](https://databrowser.uis.unesco.org/resources/bulk).


## Installation

```bash
$ pip install unesco-reader
```

## Simple Usage

#### Importing the package
```python
import unesco_reader as uis
```


#### Access the data
```python

df = uis.get_data(indicator="CR.1", country="Afghanistan")

```

At least a country or an indicator must be requested. Currently, there is a 100,000 record limit
for the API response. If this limit is exceeded an error is raise. To request more data, please
make multiple requests with fewer parameters. 

#### Access the metadata
```python
metadata = uis.get_metadata(indicator="CR.1")
```

#### Access the available indicators
```python
indicators = uis.available_indicators()
```

#### Access the available countries
```python
countries = uis.available_geo_units()
```

#### Access available themes
```python
themes = uis.available_themes()
```

#### Access data versions

To get the code for latest data versions published:
```python
version = uis.default_version()
```

To see all available versions and accompanying information:
```python
versions = uis.available_versions()
```


## Access the basic wrapper

`unesco_reader` offers out-of-the-box convenience for accessing data through the UIS API.
If you need more control, you can access the thin wrapper around the API endpoint 
through the `api` module.


## Contributing

All contributions are welcome! If you find a bug, 
or have a suggestion for a new feature, or an 
improvement on the documentation please open an issue.
Since this project is under current development, 
please check open issues and make sure the issue has 
not been raised already.

A detailed overview of the contribution process can be found
[here](https://github.com/lpicci96/unesco_reader/blob/main/CONTRIBUTING.md).
By contributing to this project, you agree to abide by its terms.

## License

`unesco_reader` was created by Luca Picci. It is licensed under the terms of the MIT license.

## Credits

`unesco_reader` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the
`py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
