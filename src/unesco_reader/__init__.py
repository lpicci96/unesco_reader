# read version from installed package
from importlib.metadata import version
from unesco_reader.uis import info, UIS, clear_all_caches, available_datasets

__version__ = version("unesco_reader")
