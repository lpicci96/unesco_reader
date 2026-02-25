"""Live API smoke tests for core public helpers.

These tests intentionally hit the UNESCO API and are opt-in.
Run them with:
    RUN_LIVE_SMOKE_TESTS=1 pytest -q tests/test_smoke_core.py
"""

import os

import pandas as pd
import pytest

from unesco_reader import core


pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_SMOKE_TESTS") != "1",
        reason="Set RUN_LIVE_SMOKE_TESTS=1 to run live API smoke tests",
    ),
]


def test_default_version_smoke_live():
    """Smoke test that default_version returns a non-empty version string from the live API."""
    result = core.default_version()
    assert isinstance(result, str)
    assert result


def test_available_versions_smoke_live():
    """Smoke test that available_versions returns non-empty tabular data from the live API."""
    result = core.available_versions()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert set(result.columns).issuperset({"version", "publicationDate", "description"})


def test_available_themes_smoke_live():
    """Smoke test that available_themes returns non-empty tabular data from the live API."""
    result = core.available_themes()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert set(result.columns).issuperset({"theme", "lastUpdate", "description"})


def test_available_indicators_smoke_live():
    """Smoke test that available_indicators returns non-empty tabular data from the live API."""
    result = core.available_indicators()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert set(result.columns).issuperset({"indicatorCode", "name", "theme"})


def test_available_geo_units_smoke_live():
    """Smoke test that available_geo_units returns non-empty tabular data from the live API."""
    result = core.available_geo_units()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert set(result.columns).issuperset({"id", "name", "type"})


def test_get_data_cr1_smoke_live():
    """Smoke test that get_data returns non-empty data for indicator CR.1 from the live API."""
    result = core.get_data(indicator="CR.1", geoUnit="USA")
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert set(result.columns).issuperset({"indicatorId", "geoUnit", "year", "value"})
