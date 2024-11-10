# read version from installed package
from importlib.metadata import version
from unesco_reader import bulk
from unesco_reader import api

# TODO: bring custom exceptions to the top level if a user needs to catch them or put in exceptions.py

from unesco_reader.core import get_data, get_metadata, available_indicators, available_geo_units, available_versions, default_version, available_themes

__version__ = version("unesco_reader")
