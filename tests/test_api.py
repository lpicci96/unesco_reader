"""Tests for the api module"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import Timeout, HTTPError, ConnectionError as RequestsConnectionError, RequestException
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
    assert api._check_for_too_many_records(mock_response) is None


def test_check_for_too_many_records_uri_too_long():
    """Test that _check_for_too_many_records raises TooManyRecordsError when the URI is too long (status code 414)."""

    mock_response = Mock()
    mock_response.status_code = 414

    with pytest.raises(
        api.TooManyRecordsError, match="Too many parameters passed to the API"
    ):
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
    mock_response = mock_success_response(
        mock_data_no_hints_no_metadata, status_code=200
    )

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = api._make_request(
            "/endpoint", params={"param1": "value1", "param2": "value2"}
        )

        # Assert that the result matches the expected JSON data
        assert result == mock_data_no_hints_no_metadata

        # Assert that requests.get was called with the correct arguments
        mock_get.assert_called_once_with(
            f"{api.API_URL}/endpoint",
            headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
            params={"param1": "value1", "param2": "value2"},
            timeout=30,
        )


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_timeout(mock_success_response):
    """Test that _make_request raises TimeoutError after retrying."""

    with patch("requests.get", side_effect=Timeout("Request timed out")) as mock_get:
        with pytest.raises(TimeoutError, match="Request timed out"):
            api._make_request("/endpoint", params={"param1": "value1"})

        # Should have been called twice (initial + 1 retry)
        assert mock_get.call_count == 2


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
        status_code=400,
    )

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(api.TooManyRecordsError, match="Too much data requested"):
            api._make_request("/endpoint", params={"param1": "value1"})


def test_make_request_connection_error(mock_success_response):
    """Test that _make_request raises ConnectionError when a non-retryable RequestException occurs."""

    # Simulate a general RequestException (not ConnectionError, so no retry)
    with patch(
        "requests.get", side_effect=RequestException("Connection error occurred")
    ):
        with pytest.raises(
            ConnectionError,
            match="Could not connect to API. Error: Connection error occurred",
        ):
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
        "param4": None,
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
            timeout=30,
        )


def test_make_request_sorts_parameters(mock_success_response):
    """Test that _make_request sorts parameters alphabetically before making the API call."""
    # Set up the mock response for a successful request
    mock_response = mock_success_response({"key": "value"}, status_code=200)

    # Define parameters in non-alphabetical order
    unsorted_params = {"z_param": "value_z", "a_param": "value_a", "m_param": "value_m"}

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = api._make_request("/endpoint", params=unsorted_params)

        # Assert the result matches the expected response
        assert result == {"key": "value"}

        # Check that requests.get was called with sorted parameters
        mock_get.assert_called_once_with(
            f"{api.API_URL}/endpoint",
            headers={"Accept-Encoding": "gzip", "Accept": "application/json"},
            params={"a_param": "value_a", "m_param": "value_m", "z_param": "value_z"},
            timeout=30,
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
    mock_response = mock_success_response(
        mock_data_no_hints_no_metadata, status_code=200
    )

    with patch(
        "unesco_reader.api._make_request", return_value=mock_response.json()
    ) as mock_make_request:
        # Call get_data with basic parameters
        result = api.get_data(indicator="CR.1", geoUnit="ZWE")

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
                "version": None,
            },
        )


def test_get_data_missing_required_parameters():
    """Test that get_data raises a ValueError when neither geo_unit nor indicator is provided."""

    with pytest.raises(
        ValueError, match="At least one indicator or one geoUnit must be provided"
    ):
        api.get_data()


def test_get_data_geo_unit_with_geo_unit_type(caplog):
    """Test that get_data logs a warning and sets geo_unit_type to None when both geo_unit and geo_unit_type are provided."""

    with caplog.at_level(logging.WARNING):
        # Case 1: geo_unit as a string and geo_unit_type provided
        with patch("unesco_reader.api._make_request") as mock_make_request:
            api.get_data(indicator="CR.1", geoUnit="ZWE", geoUnitType="NATIONAL")

            # Assert that a warning is logged
            assert "geoUnitType will be ignored" in caplog.text

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
                    "version": None,
                },
            )

        # Clear caplog for the next case
        caplog.clear()

        # Case 2: geo_unit as a list and geo_unit_type provided
        with patch("unesco_reader.api._make_request") as mock_make_request:
            api.get_data(
                indicator="CR.1", geoUnit=["ZWE", "USA"], geoUnitType="REGIONAL"
            )

            # Assert that a warning is logged
            assert "geoUnitType will be ignored" in caplog.text

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
                    "version": None,
                },
            )


def test_get_data_invalid_year_range():
    """Test that get_data raises a ValueError when start year is greater than end year."""

    # Attempt to call get_data with start year greater than end year
    with pytest.raises(
        ValueError,
        match="Start year \\(2020\\) cannot be greater than end year \\(2010\\)",
    ):
        api.get_data(indicator="CR.1", geoUnit="ZWE", start=2020, end=2010)


def test_check_valid_version_valid():
    """Test that _check_valid_version accepts a valid version string from mock_list_versions."""

    # Mock get_versions to return the mock_list_versions data
    with patch("unesco_reader.api.get_versions", return_value=mock_list_versions):
        # check that _check_valid_version does not raise an exception for a valid version
        assert api._check_valid_version("20241030-9d4d089e") is None


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


def test_get_geo_units_success(mock_success_response):
    """Test that get_geo_units returns the expected data with no parameters."""

    # Use the mock data for a successful response
    mock_response = mock_success_response(
        [{"key": "value"}, {"key": "value"}], status_code=200
    )

    with patch(
        "unesco_reader.api._make_request", return_value=mock_response.json()
    ) as mock_make_request:
        # Call get_geo_units with no parameters
        result = api.get_geo_units()

        # Assert that the result matches the mock response data
        assert result == [{"key": "value"}, {"key": "value"}]

        # Verify that _make_request was called with the correct endpoint and parameters
        mock_make_request.assert_called_once_with(
            "/api/public/definitions/geounits", {"version": None}
        )


def test_get_indicators_success(mock_success_response):
    """Test that get_indicators returns the expected data with no parameters."""

    # Use the mock data for a successful response
    mock_response = mock_success_response(
        [{"key": "value"}, {"key": "value"}], status_code=200
    )

    with patch(
        "unesco_reader.api._make_request", return_value=mock_response.json()
    ) as mock_make_request:
        # Call get_indicators with no parameters
        result = api.get_indicators()

        # Assert that the result matches the mock response data
        assert result == [{"key": "value"}, {"key": "value"}]

        # Verify that _make_request was called with the correct endpoint and parameters
        mock_make_request.assert_called_once_with(
            "/api/public/definitions/indicators",
            {"disaggregations": "false", "glossaryTerms": "false", "version": None},
        )


# --- Retry logic tests ---


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retries_on_timeout_then_succeeds(mock_success_response):
    """Test that _make_request retries on timeout and succeeds on the second attempt."""

    mock_response = mock_success_response({"key": "value"}, status_code=200)

    with patch(
        "requests.get", side_effect=[Timeout("timed out"), mock_response]
    ) as mock_get:
        result = api._make_request("/endpoint")

        assert result == {"key": "value"}
        assert mock_get.call_count == 2


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retries_on_connection_error_then_succeeds(mock_success_response):
    """Test that _make_request retries on connection error and succeeds on the second attempt."""

    mock_response = mock_success_response({"key": "value"}, status_code=200)

    with patch(
        "requests.get",
        side_effect=[RequestsConnectionError("connection refused"), mock_response],
    ) as mock_get:
        result = api._make_request("/endpoint")

        assert result == {"key": "value"}
        assert mock_get.call_count == 2


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retries_on_connection_error_then_raises():
    """Test that _make_request raises ConnectionError after exhausting retries on connection errors."""

    with patch(
        "requests.get",
        side_effect=RequestsConnectionError("connection refused"),
    ) as mock_get:
        with pytest.raises(ConnectionError, match="connection refused"):
            api._make_request("/endpoint")

        assert mock_get.call_count == 2


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retries_on_503(mock_success_response):
    """Test that _make_request retries on a 503 status code and succeeds on the second attempt."""

    mock_503 = mock_success_response({}, status_code=503)
    mock_503.raise_for_status.side_effect = HTTPError("503 Service Unavailable")
    mock_200 = mock_success_response({"key": "value"}, status_code=200)

    with patch("requests.get", side_effect=[mock_503, mock_200]) as mock_get:
        result = api._make_request("/endpoint")

        assert result == {"key": "value"}
        assert mock_get.call_count == 2


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retries_on_502(mock_success_response):
    """Test that _make_request retries on a 502 status code and succeeds on the second attempt."""

    mock_502 = mock_success_response({}, status_code=502)
    mock_502.raise_for_status.side_effect = HTTPError("502 Bad Gateway")
    mock_200 = mock_success_response({"key": "value"}, status_code=200)

    with patch("requests.get", side_effect=[mock_502, mock_200]) as mock_get:
        result = api._make_request("/endpoint")

        assert result == {"key": "value"}
        assert mock_get.call_count == 2


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_no_retry_on_404(mock_success_response):
    """Test that _make_request does not retry on a 404 (non-retryable) status code."""

    mock_404 = mock_success_response({"error": "Not Found"}, status_code=404)
    mock_404.raise_for_status.side_effect = HTTPError("404 Not Found")

    with patch("requests.get", return_value=mock_404) as mock_get:
        with pytest.raises(RuntimeError, match="404 Not Found"):
            api._make_request("/endpoint")

        assert mock_get.call_count == 1


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retry_logs_warning(mock_success_response, caplog):
    """Test that a warning is logged when a retry occurs."""

    mock_200 = mock_success_response({"key": "value"}, status_code=200)

    with patch(
        "requests.get", side_effect=[Timeout("timed out"), mock_200]
    ):
        with caplog.at_level(logging.WARNING):
            api._make_request("/endpoint")

            assert "Retrying (1/1)" in caplog.text


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_make_request_retry_logs_warning_on_503(mock_success_response, caplog):
    """Test that a warning is logged when retrying a 503 response."""

    mock_503 = mock_success_response({}, status_code=503)
    mock_503.raise_for_status.side_effect = HTTPError("503 Service Unavailable")
    mock_200 = mock_success_response({"key": "value"}, status_code=200)

    with patch("requests.get", side_effect=[mock_503, mock_200]):
        with caplog.at_level(logging.WARNING):
            api._make_request("/endpoint")

            assert "Received 503 from API" in caplog.text
            assert "Retrying (1/1)" in caplog.text


# --- set_max_retries tests ---


def test_set_max_retries_valid():
    """Test that set_max_retries sets the retry count."""

    api.set_max_retries(3)
    assert api._max_retries == 3

    # Reset to default
    api.set_max_retries(1)


def test_set_max_retries_zero():
    """Test that set_max_retries accepts 0 to disable retries."""

    api.set_max_retries(0)
    assert api._max_retries == 0

    # Reset to default
    api.set_max_retries(1)


def test_set_max_retries_negative():
    """Test that set_max_retries raises ValueError for negative values."""

    with pytest.raises(ValueError, match="retries must be a non-negative integer"):
        api.set_max_retries(-1)


def test_set_max_retries_non_integer():
    """Test that set_max_retries raises ValueError for non-integer values."""

    with pytest.raises(ValueError, match="retries must be a non-negative integer"):
        api.set_max_retries(1.5)


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_set_max_retries_disables_retries(mock_success_response):
    """Test that setting retries to 0 disables retry behavior."""

    api.set_max_retries(0)

    try:
        with patch("requests.get", side_effect=Timeout("timed out")) as mock_get:
            with pytest.raises(TimeoutError, match="timed out"):
                api._make_request("/endpoint")

            # Only one call, no retry
            assert mock_get.call_count == 1
    finally:
        api.set_max_retries(1)


@patch("unesco_reader.api.RETRY_DELAY", 0)
def test_set_max_retries_multiple_retries(mock_success_response):
    """Test that setting retries to 2 allows two retry attempts."""

    api.set_max_retries(2)
    mock_200 = mock_success_response({"key": "value"}, status_code=200)

    try:
        with patch(
            "requests.get",
            side_effect=[Timeout("t1"), Timeout("t2"), mock_200],
        ) as mock_get:
            result = api._make_request("/endpoint")

            assert result == {"key": "value"}
            assert mock_get.call_count == 3
    finally:
        api.set_max_retries(1)


def test_set_max_retries_exposed_at_package_level():
    """Test that set_max_retries is accessible from the top-level package."""

    import unesco_reader

    assert hasattr(unesco_reader, "set_max_retries")
    assert callable(unesco_reader.set_max_retries)
