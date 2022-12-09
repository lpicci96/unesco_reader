# unesco_reader


[![image](https://img.shields.io/pypi/v/unesco_reader.svg)](https://pypi.python.org/pypi/unesco_reader)
![image](https://img.shields.io/pypi/dm/unesco-reader)


unesco_reader is a python package to explore and extract data from UNESCO Institute of Statistics (UIS). 

## Motivation

Currently there is so API service to query UIS data (as of 23 June 2020). 
The only way to download UIS data is through the explorer or through their bulk download services,
by downloading a zipped folder for each dataset locally. 
This package allows you to explore UIS datasets programmatically.


Installation
------------

unesco_reader can be installed from PyPI: from the command line:

```
pip install unesco-reader
```

Usage
-----

### Basic Usage

Use with Python

To use, import the `uis` module from `unesco_reader`
```
from unesco_reader import uis
```

You can see available datasets or retrieve information for a particular dataset

To see all available datasets from UIS, run the following function:

```
print(uis.available_datasets()

>>> ['SDG', 'OPRI', 'SCI', 'SDG11', 'DEM']
```

Optionally you can return available datasets as names, and see available datasets that belong to a particular category.

```
print(uis.available_datasets(as_names=True, category='education'))

>>> ['SDG Global and Thematic Indicators' 'Other Policy Relevant Indicators']
```

To see details about a particular dataset, call the `dataset_info()` function passing in either the dataset code or name.
```
uis.dataset_info('SDG')

>>> ----------------  ----------------------------------------------------------------------------------------
    dataset_name      SDG Global and Thematic Indicators
    dataset_code      SDG
    dataset_category  education
    regional          True
    link              https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/SDG.zip
    ----------------  ----------------------------------------------------------------------------------------
```

To exctract and explore the data in a particular dataset, use the `UIS` class. A `UIS` object allows a user to 
- extract the data, either from directly from UIS bulk download services, or from a zipped file downloaded locally
- explore the data easily and retrieve relevant information about the data

To use, create an instance of `UIS`, passing either the dataset code or name. Here we create an object for the "SDG" dataset.

```
from unesco_reader.uis import UIS
sdg = UIS("SDG")
```

Once instantiated, you can retrieve relevant information about the dataset

```
sdg = UIS("SDG")
print(sdg.name)

>>> 'SDG Global and Thematic Indicators'
```

To load the data to the object, use the `load_data` method. If you already downloaded the zipped file from UIS, you can pass
a path to the file, and the data will be read from this local path. Otherwise, the data will be exctracted directly from the web.

```
sdg = UIS("SDG")
sdg.load_data()
```

To retrieve the data as a dataframe, use the `get_data` method. 

```
sdg = UIS("SDG")
sdg.load_data()
df = sdg.get_data()
print(df)
```
The above code would result in a dataframe similar to this:

| INDICATOR_ID              | INDICATOR_NAME                                   | COUNTRY_ID | COUNTRY_NAME | YEAR | VALUE |
| ------------------------- | ------------------------------------------------ | ---------- | ------------ | ---- | ----- |
| 0  ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2014 | 0.0   |
| 1  ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2015 | 0.0   |
| 2  ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2016 | 0.0   |
| 3  ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2017 | 0.0   |
| 4  ADMI.ENDOFLOWERSEC.MAT | Administration of a nationally-representative... | ABW        | Aruba        | 2018 | 0.0   |


You can pass in additional parameters specifying to return regional data (if available in the dataset) and to include metadata in the dataframe

```
sdg.get_data(grouping="regional", include_metadata=True)
```

To see additional information about the dataset use the `info` method

```
sdg.info()

>>> --------------------  ----------------------------------------------------------------------------------------
    code                  SDG
    name                  SDG Global and Thematic Indicators
    url                   https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/SDG.zip
    category              education
    available indicators  1609
    available countries   241
    time range            1950 - 2022
    available regions     179
    --------------------  ----------------------------------------------------------------------------------------
```

Several other tools to explore the data exist (full documentation coming soon) and additional tools will be added as this package is in active development
Any suggestions for new features or improvements are welcome!



-   Free software: MIT license
-   Documentation: https://lpicci96.github.io/unesco_reader
    

## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
