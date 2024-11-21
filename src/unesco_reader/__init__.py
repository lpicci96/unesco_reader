"""
unesco_reader

A package for reading data from the UNESCO Institute for Statistics API, with additional functionality and convenience, including error handling, filtering, and basic pandas support.

Usage:

Import the package:
>>> import unesco_reader as uis

Get data for an indicator and geo unit:
>>> df = uis.get_data("CR.1", "ZWE")

Get data with additional fiels like indicator and geo unit names, and footnotes:
>>> df = uis.get_data("CR.1", "ZWE", footnotes=True, labels=True)

Get metadata for an indicator:
>>> metadata = uis.get_metadata("CR.1")

Get metadata with disaggregations and glossary terms:
>>> metadata = uis.get_metadata("CR.1", disaggregations=True, glossaryTerms=True)

Get available indicators:
>>> indicators = uis.available_indicators()

Get available indicators for a specific theme and with data starting at least in 2010:
>>> indicators = uis.available_indicators(theme="education", minStart=2010)

Get available geo units:
>>> geo_units = uis.available_geo_units()

Get available regional geo units:
>>> geo_units = uis.available_geo_units(geoUnitType="REGIONAL")

Get available data versions:
>>> versions = uis.available_versions()

Get the default data version:
>>> default_version = uis.default_version()


A basic thin wrapper around all the API endpoints is available in the `api` module. This module
does not provide any additional functionality and mirrors the API endpoints directly.


Additional information:
- The package does not implement any caching as caching is handled by the API itself.
- Field names are not modified and are returned as they are from the API.
- Currently there are no rate limits for the API other than 100,000 row response limit. This package does not implement and multitheading or async functionality to handle this limit, as the intended usage for the API is to get make smaller requests for specific data points.
"""

from importlib.metadata import version
from unesco_reader import api
from unesco_reader import exceptions

from unesco_reader.core import (
    get_data,
    get_metadata,
    available_indicators,
    available_geo_units,
    available_versions,
    default_version,
    available_themes,
)

__version__ = version("unesco_reader")
