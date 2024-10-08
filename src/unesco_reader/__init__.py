# read version from installed package
from importlib.metadata import version
from unesco_reader import bulk
from unesco_reader import api

__version__ = version("unesco_reader")
