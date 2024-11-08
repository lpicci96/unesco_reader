# read version from installed package
from importlib.metadata import version
from unesco_reader import bulk
from unesco_reader import api

# TODO: bring custom exceptions to the top level if a user needs to catch them

from unesco_reader.frame import get_data, get_metadata, available_indicators

__version__ = version("unesco_reader")
