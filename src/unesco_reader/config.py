"""Configuration file for unesco_reader

This file contains shared configuration for the unesco_reader package,
including custom types and caching utilities.

"""

from functools import lru_cache
from typing import Literal

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
