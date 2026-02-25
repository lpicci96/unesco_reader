"""Configuration file for unesco_reader

This file contains the configuration for the logger used in the unesco_reader package and
the custom exceptions used in the package.

"""

import logging
from functools import lru_cache
from typing import Literal

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


# Custom TYPES
GeoUnitType = Literal["NATIONAL", "REGIONAL"]


# Cache
_cached_functions: list = []


def session_cache(maxsize: int = 32):
    """LRU cache decorator for API definition endpoints.

    Caches results for the lifetime of the session. Use ``clear_cache``
    to manually invalidate all cached data.

    Args:
        maxsize: Maximum number of entries in the cache.
    """

    def decorator(func):
        cached_func = lru_cache(maxsize=maxsize)(func)
        _cached_functions.append(cached_func)
        return cached_func

    return decorator


def clear_cache() -> None:
    """Clear all caches used by the package."""
    for func in _cached_functions:
        func.cache_clear()
