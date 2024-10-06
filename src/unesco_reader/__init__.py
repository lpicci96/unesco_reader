# read version from installed package
from importlib.metadata import version
from unesco_reader import bulk

__version__ = version("unesco_reader")
