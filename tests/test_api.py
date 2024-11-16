"""Tests for the api module"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import Timeout, HTTPError, RequestException
import logging


from unesco_reader import api
from mock_api_response import mock_data_no_hints_no_metadata, mock_list_versions


@pytest.fixture
def mock_success_response():
    """Fixture that provides a customizable mock response. By default, returns a mock response with status code 200 and empty JSON."""

    def _mock(response_data, status_code=200):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = response_data
        return mock_response

    return _mock


def test_check_for_too_many_records_success():
   """Test _check_for_too_many_records with a valid response"""

   mock_response = Mock()
   mock_response.status_code = 200
   mock_response.json.return_value = {}  # an empty json response

   # Ensure that no exception is raised when the response is valid
   try:
      api._check_for_too_many_records(mock_response)

   except api.TooManyRecordsError:
       pytest.fail("Unexpected TooManyRecordsError raised for a valid response")

def test_check_for_too_many_records_uri_too_long():
    """Test that _check_for_too_many_records raises TooManyRecordsError when the URI is too long (status code 414)."""

    mock_response = Mock()
    mock_response.status_code = 414

    with pytest.raises(api.TooManyRecordsError, match="Too many parameters passed to the API"):
        api._check_for_too_many_records(mock_response)


def test_check_for_too_many_records_too_much_data():
    """Test that _check_for_too_many_records raises TooManyRecordsError when too much data is requested (status code 400)."""

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "message": "Too much data requested (224879 records), please reduce the amount of records queried to less than 100000 by using the available filter options."
    }

    with pytest.raises(api.TooManyRecordsError, match="Too much data requested"):
        api._check_for_too_many_records(mock_response)



def test_make_request_success(mock_success_response):
    """Test that _make_request returns the correct JSON data when the response is successful."""

    # Pass in the specific mock data object and status code
    mock_response = mock_success_response(mock_data_no_hints_no_metadata, status_code=200)

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = api._make_request("/endpoint", params={"param1": "value1", "param2": "value2"})

        # Assert that the result matches the expected JSON data
        assert result == mock_data_no_hints_no_metadata

        # Assert that requests.get was called with the correct arguments
        mock_get.assert_called_once_with(
            f"{api.API_URL}/endpoint",
            headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
            params={"param1": "value1", "param2": "value2"},
            timeout=30
        )

def test_make_request_timeout(mock_success_response):
    """Test that _make_request raises TimeoutError when a timeout occurs."""

    with patch("requests.get", side_effect=Timeout("Request timed out")):
        with pytest.raises(TimeoutError, match="Request timed out"):
            api._make_request("/endpoint", params={"param1": "value1"})


def test_make_request_http_error(mock_success_response):
    """Test that _make_request raises RuntimeError when an HTTP error occurs (e.g., 4xx/5xx status codes)."""
    mock_response = mock_success_response({"error": "Not Found"}, status_code=404)

    with patch("requests.get", return_value=mock_response) as mock_get:
        mock_get.side_effect = HTTPError("404 Client Error: Not Found for url")

        with pytest.raises(RuntimeError, match="404 Client Error: Not Found for url"):
            api._make_request("/endpoint", params={"param1": "value1"})


def test_make_request_too_many_records(mock_success_response):
    """Test that _make_request raises TooManyRecordsError when too much data is requested (status code 400 with specific message)."""

    # Set up a mock response that simulates the "too much data requested" error
    mock_response = mock_success_response(
        {
            "message": "Too much data requested (224879 records), please reduce the amount of records queried to less than 100000 by using the available filter options."
        },
        status_code=400
    )

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(api.TooManyRecordsError, match="Too much data requested"):
            api._make_request("/endpoint", params={"param1": "value1"})


def test_make_request_connection_error(mock_success_response):
    """Test that _make_request raises ConnectionError when a general request exception occurs."""

    # Simulate a general RequestException
    with patch("requests.get", side_effect=RequestException("Connection error occurred")):
        with pytest.raises(ConnectionError, match="Could not connect to API. Error: Connection error occurred"):
            api._make_request("/endpoint", params={"param1": "value1"})


def test_make_request_filters_none_values(mock_success_response):
    """Test that _make_request filters out parameters with None values before making the API call."""

    # Set up the mock response for a successful request
    mock_response = mock_success_response({"key": "value"}, status_code=200)

    # Define parameters with some None values
    params_with_none = {
        "param1": "value1",
        "param2": None,
        "param3": "value3",
        "param4": None
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = api._make_request("/endpoint", params=params_with_none)

        # Assert the result matches the expected response
        assert result == {"key": "value"}

        # Check that requests.get was called with filtered parameters (without None values)
        mock_get.assert_called_once_with(
            f"{api.API_URL}/endpoint",
            headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
            params={"param1": "value1", "param3": "value3"},
            timeout=30
        )


def test_make_request_sorts_parameters(mock_success_response):
    """Test that _make_request sorts parameters alphabetically before making the API call."""
    # Set up the mock response for a successful request
    mock_response = mock_success_response({"key": "value"}, status_code=200)

    # Define parameters in non-alphabetical order
    unsorted_params = {
        "z_param": "value_z",
        "a_param": "value_a",
        "m_param": "value_m"
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = api._make_request("/endpoint", params=unsorted_params)

        # Assert the result matches the expected response
        assert result == {"key": "value"}

        # Check that requests.get was called with sorted parameters
        mock_get.assert_called_once_with(
            f"{api.API_URL}/endpoint",
            headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
            params={"a_param": "value_a", "m_param": "value_m", "z_param": "value_z"},
            timeout=30
        )


def test_convert_bool_to_string():
    """
    Test the _convert_bool_to_string function to ensure correct string conversion.
    """
    # True input
    assert api._convert_bool_to_string(True) == "true"

    # False input
    assert api._convert_bool_to_string(False) == "false"

    # None input
    assert api._convert_bool_to_string(None) is None


def test_get_data_success(mock_success_response):
    """Test that get_data returns the expected data with minimal required parameters (indicator and geo_unit)."""

    # Use the mock data for a successful response
    mock_response = mock_success_response(mock_data_no_hints_no_metadata, status_code=200)

    with patch("unesco_reader.api._make_request", return_value=mock_response.json()) as mock_make_request:
        # Call get_data with basic parameters
        result = api.get_data(indicator="CR.1", geo_unit="ZWE")

        # Assert that the result matches the mock response data
        assert result == mock_data_no_hints_no_metadata

        # Verify that _make_request was called with the correct endpoint and parameters
        mock_make_request.assert_called_once_with(
            "/api/public/data/indicators",
            {
                "indicator": ["CR.1"],
                "geoUnit": ["ZWE"],
                "start": None,
                "end": None,
                "indicatorMetadata": "false",
                "footnotes": "false",
                "geoUnitType": None,
                "version": None
            }
        )

def test_get_data_missing_required_parameters():
    """Test that get_data raises a ValueError when neither geo_unit nor indicator is provided."""

    with pytest.raises(ValueError, match="At least one indicator or one geo_unit must be provided"):
        api.get_data()


def test_get_data_geo_unit_with_geo_unit_type(caplog):
    """Test that get_data logs a warning and sets geo_unit_type to None when both geo_unit and geo_unit_type are provided."""

    with caplog.at_level(logging.WARNING):
        # Case 1: geo_unit as a string and geo_unit_type provided
        with patch("unesco_reader.api._make_request") as mock_make_request:
            api.get_data(indicator="CR.1", geo_unit="ZWE", geo_unit_type="NATIONAL")

            # Assert that a warning is logged
            assert "geo_unit_type will be ignored" in caplog.text

            # Verify that geo_unit_type is set to None in the parameters sent to _make_request
            mock_make_request.assert_called_once_with(
                "/api/public/data/indicators",
                {
                    "indicator": ["CR.1"],
                    "geoUnit": ["ZWE"],
                    "start": None,
                    "end": None,
                    "indicatorMetadata": "false",
                    "footnotes": "false",
                    "geoUnitType": None,
                    "version": None
                }
            )

        # Clear caplog for the next case
        caplog.clear()

        # Case 2: geo_unit as a list and geo_unit_type provided
        with patch("unesco_reader.api._make_request") as mock_make_request:
            api.get_data(indicator="CR.1", geo_unit=["ZWE", "USA"], geo_unit_type="REGIONAL")

            # Assert that a warning is logged
            assert "geo_unit_type will be ignored" in caplog.text

            # Verify that geo_unit_type is set to None in the parameters sent to _make_request
            mock_make_request.assert_called_once_with(
                "/api/public/data/indicators",
                {
                    "indicator": ["CR.1"],
                    "geoUnit": ["ZWE", "USA"],
                    "start": None,
                    "end": None,
                    "indicatorMetadata": "false",
                    "footnotes": "false",
                    "geoUnitType": None,
                    "version": None
                }
            )


def test_get_data_invalid_year_range():
    """Test that get_data raises a ValueError when start year is greater than end year."""

    # Attempt to call get_data with start year greater than end year
    with pytest.raises(ValueError, match="Start year \\(2020\\) cannot be greater than end year \\(2010\\)"):
        api.get_data(indicator="CR.1", geo_unit="ZWE", start=2020, end=2010)


def test_check_valid_version_valid():
    """Test that _check_valid_version accepts a valid version string from mock_list_versions."""

    # Mock get_versions to return the mock_list_versions data
    with patch("unesco_reader.api.get_versions", return_value=mock_list_versions):
        # Test with a valid version that exists in mock_list_versions
        try:
            api._check_valid_version("20241030-9d4d089e")
        except ValueError:
            pytest.fail("Unexpected ValueError raised for a valid version")

def test_check_valid_version_invalid():
    """Test that _check_valid_version raises ValueError for a non-existent version."""

    # Mock get_versions to return the mock_list_versions data
    with patch("unesco_reader.api.get_versions", return_value=mock_list_versions):
        with pytest.raises(ValueError, match="Invalid data version: 20240101-xxxxxx"):
            api._check_valid_version("20240101-xxxxxx")

def test_check_valid_version_invalid_type():
    """Test that _check_valid_version raises ValueError if version is not a string."""

    with pytest.raises(ValueError, match="Data version must be a string"):
        api._check_valid_version(20241030)  # Passing an integer instead of a string

