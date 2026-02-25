"""Shared test configuration and fixtures."""

import pytest

from unesco_reader.config import clear_cache


@pytest.fixture(autouse=True)
def _clear_cache_between_tests():
    """Clear all session caches before each test to ensure test isolation."""
    clear_cache()
    yield
    clear_cache()
