"""Configuration file for unesco_reader

This file contains the configuration for the logger used in the unesco_reader package and
the custom exceptions used in the package.

"""

import logging
from typing import Literal


# Custom Exceptions


class NoDataError(Exception):
    """This is a custom exception that is raised when no UIS data exists"""

    pass


# Configure Logging
logger = logging.getLogger(__name__)
shell_handler = logging.StreamHandler()  # Create terminal handler
logger.setLevel(logging.INFO)  # Set levels for the logger, shell and file
shell_handler.setLevel(logging.INFO)  # Set levels for the logger, shell and file

# Format the outputs   "%(levelname)s (%(asctime)s): %(message)s"
fmt_file = "%(levelname)s: %(message)s"

# "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
fmt_shell = "%(levelname)s: %(message)s"

shell_formatter = logging.Formatter(fmt_shell)  # Create formatters
shell_handler.setFormatter(shell_formatter)  # Add formatters to handlers
logger.addHandler(shell_handler)  # Add handlers to the logger


# TYPES

GEO_UNIT_TYPE = Literal["NATIONAL", "REGIONAL"]