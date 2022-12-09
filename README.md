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

You can see the available UIS datasets by calling `available_datasets()`



-   Free software: MIT license
-   Documentation: https://lpicci96.github.io/unesco_reader
    

## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.
