"""Tests for the session caching functionality."""

from unittest.mock import patch, MagicMock

from unesco_reader import api
from unesco_reader.config import clear_cache, _cached_functions
from mock_api_response import mock_list_versions, mock_geo_units


def test_get_indicators_caches_result():
    """Test that get_indicators returns cached result on repeated calls."""

    mock_response = [{"indicatorCode": "10", "name": "Test"}]

    with patch("unesco_reader.api._make_request", return_value=mock_response) as mock:
        result1 = api.get_indicators()
        result2 = api.get_indicators()

        assert result1 == result2
        mock.assert_called_once()  # only one actual API call


def test_get_geo_units_caches_result():
    """Test that get_geo_units returns cached result on repeated calls."""

    with patch("unesco_reader.api._make_request", return_value=mock_geo_units) as mock:
        result1 = api.get_geo_units()
        result2 = api.get_geo_units()

        assert result1 == result2
        mock.assert_called_once()


def test_get_versions_caches_result():
    """Test that get_versions returns cached result on repeated calls."""

    with patch(
        "unesco_reader.api._make_request", return_value=mock_list_versions
    ) as mock:
        result1 = api.get_versions()
        result2 = api.get_versions()

        assert result1 == result2
        mock.assert_called_once()


def test_get_default_version_caches_result():
    """Test that get_default_version returns cached result on repeated calls."""

    mock_response = {"version": "20241030-9d4d089e"}

    with patch("unesco_reader.api._make_request", return_value=mock_response) as mock:
        result1 = api.get_default_version()
        result2 = api.get_default_version()

        assert result1 == result2
        mock.assert_called_once()


def test_get_indicators_different_args_not_cached():
    """Test that get_indicators with different arguments makes separate API calls."""

    mock_response = [{"indicatorCode": "10", "name": "Test"}]

    with patch("unesco_reader.api._make_request", return_value=mock_response) as mock:
        api.get_indicators(disaggregations=False)
        api.get_indicators(disaggregations=True)

        assert mock.call_count == 2


def test_clear_cache_invalidates_cached_results():
    """Test that clear_cache forces fresh API calls on subsequent requests."""

    mock_response = [{"indicatorCode": "10", "name": "Test"}]

    with patch("unesco_reader.api._make_request", return_value=mock_response) as mock:
        api.get_indicators()
        assert mock.call_count == 1

        clear_cache()

        api.get_indicators()
        assert mock.call_count == 2  # called again after cache clear


def test_clear_cache_clears_all_cached_functions():
    """Test that clear_cache clears all registered cached functions."""

    mock_indicators = [{"indicatorCode": "10", "name": "Test"}]
    mock_versions = [{"version": "v1"}]

    with (
        patch(
            "unesco_reader.api._make_request",
            side_effect=[
                mock_indicators,
                mock_versions,
                mock_indicators,
                mock_versions,
            ],
        ) as mock,
    ):
        api.get_indicators()
        api.get_versions()
        assert mock.call_count == 2

        clear_cache()

        api.get_indicators()
        api.get_versions()
        assert mock.call_count == 4  # all caches cleared, fresh calls made


def test_get_data_is_not_cached():
    """Test that get_data is not cached and always makes a fresh API call."""

    mock_response = {"hints": [], "records": [{"value": 1}], "indicatorMetadata": []}

    with patch("unesco_reader.api._make_request", return_value=mock_response) as mock:
        api.get_data(indicator="CR.1", geoUnit="ZWE")
        api.get_data(indicator="CR.1", geoUnit="ZWE")

        assert mock.call_count == 2  # not cached, called twice


def test_cached_functions_are_registered():
    """Test that all cached API functions are registered for cache clearing."""

    # The four cached functions should be registered
    assert len(_cached_functions) >= 4


def test_clear_cache_exposed_at_package_level():
    """Test that clear_cache is accessible from the top-level package."""

    import unesco_reader

    assert hasattr(unesco_reader, "clear_cache")
    assert callable(unesco_reader.clear_cache)


def test_session_cache_shallow_mutation_protection():
    """Mutating a returned value must not corrupt the cache."""
    from unesco_reader.config import session_cache

    @session_cache(maxsize=2)
    def get_items():
        return [{"key": "value"}]

    try:
        result1 = get_items()
        result1[0]["key"] = "corrupted"
        result1.append({"extra": True})

        result2 = get_items()
        assert result2 == [{"key": "value"}], "Cache was corrupted by shallow mutation"
    finally:
        get_items.cache_clear()


def test_session_cache_deep_mutation_protection():
    """Mutating nested structures must not corrupt the cache."""
    from unesco_reader.config import session_cache

    @session_cache(maxsize=2)
    def get_nested():
        return {"a": {"b": [1, 2, 3]}}

    try:
        result1 = get_nested()
        result1["a"]["b"].append(999)
        result1["a"]["new_key"] = "injected"

        result2 = get_nested()
        assert result2 == {"a": {"b": [1, 2, 3]}}, "Cache was corrupted by deep mutation"
    finally:
        get_nested.cache_clear()


def test_available_versions_does_not_corrupt_get_versions_cache():
    """available_versions() pops 'themeDataStatus'; this must not affect get_versions()."""
    from unesco_reader import core

    with patch("unesco_reader.api._make_request", return_value=mock_list_versions):
        clear_cache()
        # available_versions internally pops themeDataStatus
        core.available_versions()
        # get_versions should still return records with themeDataStatus intact
        versions = api.get_versions()
        for v in versions:
            assert "themeDataStatus" in v, "get_versions cache corrupted by available_versions"


def test_available_indicators_does_not_corrupt_get_indicators_cache():
    """available_indicators() pops 'dataAvailability'; this must not affect get_indicators()."""
    from unesco_reader import core

    mock_indicators = [
        {
            "indicatorCode": "CR.1",
            "name": "Test",
            "lastDataUpdate": "2024-01-01",
            "dataAvailability": {
                "timeLine": {"min": 2000, "max": 2020},
                "totalRecordCount": 100,
                "geoUnits": {"types": ["NATIONAL"]},
            },
        }
    ]

    with patch("unesco_reader.api._make_request", return_value=mock_indicators):
        clear_cache()
        # available_indicators internally pops dataAvailability
        core.available_indicators()
        # get_indicators should still have dataAvailability
        indicators = api.get_indicators()
        for ind in indicators:
            assert "dataAvailability" in ind, "get_indicators cache corrupted by available_indicators"


def test_session_cache_cache_clear_still_works():
    """cache_clear on the wrapper must invalidate the underlying lru_cache."""
    from unesco_reader.config import session_cache

    call_count = 0

    @session_cache(maxsize=2)
    def counter():
        nonlocal call_count
        call_count += 1
        return call_count

    try:
        assert counter() == 1
        assert counter() == 1  # cached
        counter.cache_clear()
        assert counter() == 2  # fresh call after clear
    finally:
        counter.cache_clear()
