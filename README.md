# unesco_reader

[![PyPI](https://img.shields.io/pypi/v/unesco_reader.svg)](https://pypi.org/project/unesco_reader/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unesco_reader.svg)](https://pypi.org/project/unesco_reader/)
[![Documentation Status](https://readthedocs.org/projects/unesco-reader/badge/?version=latest)](https://unesco-reader.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/lpicci96/unesco_reader/branch/main/graph/badge.svg)](https://codecov.io/gh/lpicci96/unesco_reader)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)


Pythonic access to UNESCO data

`unesco_reader` is a Python package providing a simple interface to access UNESCO Institute of Statistics (UIS)
data. UIS currently does not offer API access to its data. Users must download zipped files and extract the data.
This process requires several manual steps explained in their [python tutorial](https://apiportal.uis.unesco.org/bdds-tutorial). This package simplifies the process by providing a simple
interface to access, explore, and analyze the data, using pandas DataFrames. This package also
allows users to view dataset documentation and other information such as the latest update date for, and all
available datasets from UIS.

### Note</b>: 
UIS data is expected to be accessible through the DataCommons API in the future and should
be the preferred method to access the data. Future versions of this package may include support for the API,
or may be deprecated and remain as a legacy package.

This package is designed to scrape data from the UIS website. As a result of this approach
the package may be subject to breakage if the website structure or data file formats change. 
Please report any unexpected errors or issues you encounter. All feedback, suggestions, and contributions are welcome!

## Installation

```bash
$ pip install unesco-reader
```

## Usage

Importing the package
```python
import unesco_reader as uis
```

Retrieve information about all the available datasets from UIS.
```python
uis.info()
```
This function will display all available datasets and relevant information about them.
```
>>>
name                                                               latest_update    theme
-----------------------------------------------------------------  ---------------  ---------
SDG Global and Thematic Indicators                                 February 2024    Education
Other Policy Relevant Indicators (OPRI)                            February 2024    Education
Research and Development (R&D) SDG 9.5                             February 2024    Science
Research and Development (R&D) – Other Policy Relevant Indicators  February 2024    Science
...
```

Retrieve a list of all available datasets from UIS.
```python
uis.available_datasets()

>>> ['SDG Global and Thematic Indicators',
     'Other Policy Relevant Indicators (OPRI)',
     'Research and Development (R&D) SDG 9.5',
     ...]
```

Optionally you can specify a theme to filter the datasets.
```python
uis.available_datasets(theme='Education')
```


To access data for a particular dataset, use the `UIS` class passing the name of the dataset. 
A `UIS` object allows a user to easily access, explore, and analyse the data.
On instantiation, the data will be extracted from the UIS website, or if it has already been 
extracted, it will be read from the cache (more on caching below)

```python
sdg = uis.UIS("SDG Global and Thematic Indicators")
```

Basic information about the dataset can be accessed using the `info` method.
```python
sdg.info()
```
This will display information about the dataset, such as the name, and the latest update, and theme

```
>>>
-------------  ----------------------------------
name           SDG Global and Thematic Indicators
latest update  February 2024
theme          Education
-------------  ----------------------------------
```

Information is also accessible through the attributes of the object.
```python
sdg.name
sdg.latest_update
sdg.theme
sdg.readme
```

The `readme` attribute contains the dataset documentation. To display the documentation, use the `display_readme` method.
```python
sdg.display_readme()
```

Various methods exist to access the data.
To access country data:
```python
sdg.get_country_data()
```
This will return a pandas DataFrame with the country data, in a structured and expected format.
By default the dataframe will not contain metadata. To include metadata in the output, set the `include_metadata` parameter to `True`.
Countries may also be filtered for a specific region by specifying the region's ID in the `region` parameter.
To see available regions use the `get_regions` method.

```python
sdg.get_country_data(include_metadata=True, region='WB: World')
```

To access regional data:
```python
sdg.get_region_data()
```
This will return a pandas DataFrame with the regional data, in a structured and expected format.
By default the dataframe will not contain metadata. To include metadata in the output, set the `include_metadata` parameter to `True`.

Metadata, available countries, available regions, and variables are also accessible through class objects.
```python
sdg.get_metadata()
sdg.get_countries()
sdg.get_regions()
sdg.get_variables()
```

To refresh the data and extract the latest data from the UIS website, use the `refresh` method.
```python
sdg.refresh()
```

### Caching

Caching is used to prevent unnecessary requests to the UIS website and enhance performance.
To refresh data returned by functions, use the `refresh` parameter.
```python
uis.info(refresh=True)
uis.available_datasets(refresh=True)
```
`refresh=True` will clear the cache and force extraction of the data and information from the UIS website.

For the `UIS` class, the `refresh` method will clear the cache and extract the latest data from the UIS website.
```python
sdg.refresh()
```

To clear all cached data, use the `clear_all_caches` method.
```python
uis.clear_all_caches()
```


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
