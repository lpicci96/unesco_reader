"""Tests for the API module"""

import pytest
import requests
from unittest.mock import patch

from unesco_reader import api

def test_convert_bool_to_string():
    """Test the convert_bool_to_string function"""
    assert api._convert_bool_to_string(True) == "true"
    assert api._convert_bool_to_string(False) == "false"
    assert api._convert_bool_to_string(None) is None


@patch('unesco_reader.api.requests.get')
def test_make_request_success(mock_get):
    """Test the _make_request function with a successful response"""
    mock_response = {
        "key": "value"
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = api._make_request("/some-endpoint", params={"param": "value"})

    mock_get.assert_called_once_with(
        'https://api.uis.unesco.org/some-endpoint',
        headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
        params={'param': 'value'},
        timeout=30
    )
    assert result == mock_response


@patch('unesco_reader.api.requests.get')
def test_make_request_success_no_params(mock_get):
    """Test the _make_request function with a successful response and no params"""
    mock_response = {
        "key": "value"
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = api._make_request("/some-endpoint")

    mock_get.assert_called_once_with(
        'https://api.uis.unesco.org/some-endpoint',
        headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
        params=None,  # No params
        timeout=30
    )
    assert result == mock_response


@patch('unesco_reader.api.requests.get')
def test_make_request_timeout(mock_get):
    """Test the _make_request function with a timeout error"""

    mock_get.side_effect = requests.exceptions.Timeout

    with pytest.raises(TimeoutError):
        api._make_request("/some-endpoint", params={"param": "value"})

    mock_get.assert_called_once_with(
        'https://api.uis.unesco.org/some-endpoint',
        headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
        params={'param': 'value'},
        timeout=30
    )


@patch('unesco_reader.api.requests.get')
def test_make_request_http_error(mock_get):
    """Test the _make_request function with an HTTP error"""

    mock_get.return_value.status_code = 500
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

    with pytest.raises(RuntimeError):
        api._make_request("/some-endpoint", params={"param": "value"})

    mock_get.assert_called_once_with(
        'https://api.uis.unesco.org/some-endpoint',
        headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
        params={'param': 'value'},
        timeout=30
    )


@patch('unesco_reader.api.requests.get')
def test_make_request_connection_error(mock_get):
    """Test the _make_request function with a connection error"""

    mock_get.side_effect = requests.exceptions.RequestException

    # Call the function and expect a ConnectionError
    with pytest.raises(ConnectionError):
        api._make_request("/some-endpoint", params={"param": "value"})

    # Ensure that the get request was called
    mock_get.assert_called_once_with(
        'https://api.uis.unesco.org/some-endpoint',
        headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
        params={'param': 'value'},
        timeout=30
    )


@patch('unesco_reader.api._make_request')
def test_get_data_success(mock_make_request):
    """Test the get_data function with a successful response"""

    mock_response = {"key": "value"}
    mock_make_request.return_value = mock_response

    # Call the get_data function
    result = api.get_data(indicator="CR.1", geo_unit="ITA", start=2010, end=2020)

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/data/indicators",
        {
            "indicator": ["CR.1"],
            "geoUnit": ["ITA"],
            "start": 2010,
            "end": 2020,
            "indicatorMetadata": "false",
            "footnotes": "false",
            "geoUnitType": None,
            "version": None
        }
    )

    # Assert the result
    assert result == mock_response


def test_get_data_missing_parameters():
    """Test the get_data function with missing parameters"""

    with pytest.raises(ValueError, match="At least one indicator or one geo_unit must be provided"):
        api.get_data(indicator=None, geo_unit=None)


def test_get_data_invalid_year_range():
    """Test the get_data function with an invalid year range"""

    with pytest.raises(ValueError, match="Start year cannot be greater than end year"):
        api.get_data(indicator="CR.1", geo_unit="ITA", start=2020, end=2019)


@patch('unesco_reader.api.logger.warning')
@patch('unesco_reader.api._make_request')
def test_get_data_geo_unit_and_geo_unit_type_warning(mock_make_request, mock_warning):
    """Test the get_data function with both geo_unit and geo_unit_type"""

    mock_response = {"key": "value"}
    mock_make_request.return_value = mock_response

    # Call get_data with both geo_unit and geo_unit_type
    api.get_data(indicator="CR.1", geo_unit="ITA", geo_unit_type="NATIONAL")

    # Assert that the warning was logged
    mock_warning.assert_called_once_with("Both geo_unit and geo_unit_type are specified. geo_unit_type will be ignored")


@patch('unesco_reader.api._make_request')
def test_get_geo_units_success(mock_make_request):
    """Test the get_geo_units function with a successful response"""

    mock_response = [{"geo_unit": "ITA"}, {"geo_unit": "ZWE"}]
    mock_make_request.return_value = mock_response

    # Call get_geo_units with default parameters (no version specified)
    result = api.get_geo_units()

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/definitions/geounits",
        {"version": None}
    )

    # Assert the result
    assert result == mock_response


@patch('unesco_reader.api._make_request')
def test_get_geo_units_with_version(mock_make_request):
    """Test the get_geo_units function with a specified version"""

    mock_response = [{"geo_unit": "ITA"}, {"geo_unit": "ZWE"}]
    mock_make_request.return_value = mock_response

    # Call get_geo_units with a specific version
    result = api.get_geo_units(version="asdfghjkl")

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/definitions/geounits",
        {"version": "asdfghjkl"}
    )

    # Assert the result
    assert result == mock_response


@patch('unesco_reader.api._make_request')
def test_get_indicators_success(mock_make_request):
    """Test the get_indicators function with a successful response"""

    mock_response = [{"indicator": "CR.1"}, {"indicator": "20"}]
    mock_make_request.return_value = mock_response

    # Call get_indicators with default parameters
    result = api.get_indicators()

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/definitions/indicators",
        {
            "disaggregations": "false",
            "glossaryTerms": "false",
            "version": None
        }
    )

    # Assert the result
    assert result == mock_response


@patch('unesco_reader.api._make_request')
def test_get_indicators_with_params(mock_make_request):
    """Test the get_indicators function with specified parameters"""

    mock_response = [{"indicator": "SE.PRM.TENR"}, {"indicator": "SE.SEC.ENRL"}]
    mock_make_request.return_value = mock_response

    # Call get_indicators with specified parameters
    result = api.get_indicators(disaggregations=True, glossary_terms=True, version="asdfghjkl")

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/definitions/indicators",
        {
            "disaggregations": "true",
            "glossaryTerms": "true",
            "version": "asdfghjkl"
        }
    )

    # Assert the result
    assert result == mock_response


@patch('unesco_reader.api._make_request')
def test_get_versions_success(mock_make_request):
    """Test the get_versions function with a successful response"""

    mock_response = [{"version": "2021"}, {"version": "2020"}]
    mock_make_request.return_value = mock_response

    # Call get_versions
    result = api.get_versions()

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/versions",
    )

    # Assert the result
    assert result == mock_response


@patch('unesco_reader.api._make_request')
def test_get_default_version_success(mock_make_request):
    """Test the get_default_version function with a successful response"""

    mock_response = {"version": "2021"}
    mock_make_request.return_value = mock_response

    # Call get_default_version
    result = api.get_default_version()

    # Assert the function call and parameters
    mock_make_request.assert_called_once_with(
        "/api/public/versions/default",
    )

    # Assert the result
    assert result == mock_response