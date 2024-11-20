from importlib.metadata import version
from unesco_reader import api
from unesco_reader import exceptions

from unesco_reader.core import get_data, get_metadata, available_indicators, available_geo_units, available_versions, default_version, available_themes

__version__ = version("unesco_reader")
