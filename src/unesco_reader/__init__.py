# read version from installed package
from importlib.metadata import version
from unesco_reader import bulk
from unesco_reader import api

from unesco_reader.frame import get_data, available_indicators, available_geo_units, indicator_metadata, available_themes

__version__ = version("unesco_reader")
