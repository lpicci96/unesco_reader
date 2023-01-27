# unesco_reader

[![PyPI](https://img.shields.io/pypi/v/unesco_reader.svg)](https://pypi.org/project/YOUR_PACKAGE_NAME/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unesco_reader.svg)](https://pypi.org/project/YOUR_PACKAGE_NAME/)
[![Documentation Status](https://readthedocs.org/projects/unesco-reader/badge/?version=latest)](https://unesco-reader.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/lpicci96/unesco_reader/branch/main/graph/badge.svg)](https://codecov.io/gh/lpicci96/unesco_reader)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/unesco_reader.svg)](https://pypi.org/project/YOUR_PACKAGE_NAME/)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)


Pythonic access to UNESCO data

`unesco_reader` is a Python package providing a simple interface to access UNESCO data. 
UNESCO does not currently provide an API to access its data, particularly the widely used 
UNESCO Institute for Statistics (UIS) data. Users must download the data from the UIS bulk download
services as a zipped file, and then extract the data from the zip file. This requires several manual steps,
and some of the datasets are too large to be read easily with a standard spreadsheet program
and must be read programmatically. UNESCO provides some guidance on how to do this in their 
[python tutorial](https://apiportal.uis.unesco.org/bdds-tutorial).

With `unesco_reader`, users don't need to worry about downloading the data, extracting it from the zip file,
and following the python tutorial - this is all taken care of. This package handles accessing the data directly from the UNESCO website, and provides a simple interface to
explore the data.


## Installation

```bash
$ pip install unesco-reader
```

## Usage

To access UIS data, import the `uis` module from `unesco_reader`
```python
from unesco_reader import uis
```


You can see available datasets or retrieve information for a particular dataset. 
To see all available datasets from UIS, run the following function:

```python
uis.available_datasets()
```
The output will be a list of available dataset codes `['SDG', 'OPRI', 'SCI', 'SDG11', 'DEM']`.

Optionally you can return available datasets as names, and see available 
datasets that belong to a particular category.

```python
uis.available_datasets(as_names=True, category='education')
```

To see details about a particular dataset, call the `dataset_info()` 
function passing in either the dataset code or name.

```python
uis.dataset_info('SDG')
```

Information about the dataset will be printed:
```
----------------  -----------------------------------------------
dataset_name      SDG Global and Thematic Indicators
dataset_code      SDG
dataset_category  education
link              https://apimgmtstzgjpfeq2u763lag.blob...
----------------  -----------------------------------------------
```

To extract and explore the data in a particular dataset, use the `UIS` class. 
A `UIS` object allows a user to extract the data, either from directly from
UIS bulk download services, or from a zipped file downloaded locally, 
and explore and analyze the data easily.

To use, first create an instance of `UIS`, passing either the dataset code or name. 
Here we create an object for the "SDG" dataset.

```python
sdg = uis.UIS("SDG")
```

Once instantiated, you can retrieve relevant information about the dataset

```python
sdg.dataset_name # SDG Global and Thematic Indicators
sdg.dataset_code # SDG
sdg.dataset_category # education
sdg.link # https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/uisdatastore/SDG.zip
```

To access and start exploring the data, you need to load the data to the object
using the `load_data` method. This will download the data from the UNESCO website,
clean it, and format it as a pandas DataFrame stored in the object. Optionally,
if you have downloaded the zipped file locally, you can pass the path to the file.

```python
sdg = UIS("SDG")
sdg.load_data()
```

Once the data is loaded, you can access it using the `get_data` method.

```python
df = sdg.get_data()
print(df)
```
The result will be a pandas DataFrame with the data. Here is a sample what the data looks like:

| INDICATOR_ID           | INDICATOR_NAME                                   | COUNTRY_ID | COUNTRY_NAME | YEAR | VALUE |
| ---------------------- | ------------------------------------------------ | ---------- | ------------ | ---- | ----- |
| ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2014 | 0.0   |
| ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2015 | 0.0   |
| ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2016 | 0.0   |
| ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2017 | 0.0   |
| ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2018 | 0.0   |

In the `get_data` you can specify whether you want to return country or regional (if available) data,
and whether to include metadata in the dataframe. 

Several other tools are available to explore the data. 
Please see the [documentation](https://unesco-reader.readthedocs.io/en/latest/) for more details.


## Contributing

Interested in contributing? Check out the contributing guidelines.
Please note that this project is released with a Code of Conduct.
By contributing to this project, you agree to abide by its terms.

## License

`unesco_reader` was created by Luca Picci. It is licensed under the terms of the MIT license.

## Credits

`unesco_reader` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the
`py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
