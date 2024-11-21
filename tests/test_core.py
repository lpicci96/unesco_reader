"""Tests for the core module."""

import pytest
from unittest.mock import Mock, patch
import pandas as pd

from unesco_reader import core
from mock_api_response import (
    mock_data_no_hints_no_metadata,
    mock_no_data_hints,
    mock_no_data_multiple_hints,
    mock_indicators_no_agg_no_glossary,
    mock_geo_units,
    mock_data_footnotes,
    mock_default_version,
    mock_list_versions,
)
from unesco_reader.exceptions import NoDataError


def test_log_hints_no_hints(caplog):
    """Test that no warnings are logged when the response has no 'hints' key or an empty list."""
    # Use the mock response without hints
    with caplog.at_level("WARNING"):
        core._log_hints(mock_data_no_hints_no_metadata)
        assert len(caplog.records) == 0  # No warnings logged


def test_log_hints_single_hint(caplog):
    """Test that a single warning is logged when the response contains one hint."""
    # Use the mock response with a single hint
    with caplog.at_level("WARNING"):
        core._log_hints(mock_no_data_hints)
        assert len(caplog.records) == 1  # One warning logged
        assert (
            "The indicator could not be found, invalid" in caplog.text
        )  # Verify the logged message


def test_log_hints_multiple_hints(caplog):
    """Test that multiple warnings are logged when the response contains multiple hints."""
    # Use the mock response with multiple hints
    with caplog.at_level("WARNING"):
        core._log_hints(mock_no_data_multiple_hints)
        assert len(caplog.records) == 2  # Two warnings logged
        assert "The indicator could not be found, invalid 1" in caplog.text
        assert "The indicator could not be found, invalid 2" in caplog.text


def test_convert_codes_single_code():
    """Test that a valid code input remains unchanged."""
    # Mock mapper
    mapper = {"Name1": "CODE1", "Name2": "CODE2"}

    # Test input: a valid code
    result = core._convert_codes("CODE1", mapper)

    # Assert the code remains unchanged
    assert result == "CODE1"


def test_convert_codes_single_name():
    """Test that a valid name input is correctly converted to its corresponding code."""
    # Mock mapper
    mapper = {"Name1": "CODE1", "Name2": "CODE2"}

    # Test input: a valid name
    result = core._convert_codes("Name1", mapper)

    # Assert the name is correctly converted to the code
    assert result == "CODE1"


def test_convert_codes_mixed_types():
    """Test that a list with valid codes and names converts names to codes and leaves codes unchanged."""
    # Mock mapper
    mapper = {"Name1": "CODE1", "Name2": "CODE2"}

    # Test input: a list with valid codes and names
    result = core._convert_codes(["CODE1", "Name2", "InvalidName"], mapper)

    # Assert that:
    # - "CODE1" remains unchanged (valid code)
    # - "Name2" is converted to "CODE2" (valid name)
    # - "InvalidName" is left unchanged (not in mapper)
    assert result == ["CODE1", "CODE2", "InvalidName"]


def test_convert_indicator_codes_to_code_single_name():
    """Test that a single indicator name is correctly converted to its corresponding code."""
    # Mock the API response
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=mock_indicators_no_agg_no_glossary,
    ):
        # Test input: a valid name
        result = core._convert_indicator_codes_to_code(
            "Official entrance age to early childhood educational development (years)"
        )

        # Assert the name is correctly converted to the code
        assert result == "10"


def test_convert_indicator_codes_to_code_single_code():
    """Test that a single indicator code remains unchanged."""
    # Mock the API response
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=mock_indicators_no_agg_no_glossary,
    ):
        # Test input: a valid code
        result = core._convert_indicator_codes_to_code("10")

        # Assert the code remains unchanged
        assert result == "10"


def test_convert_indicator_codes_to_code_mixed_inputs():
    """Test that a list with valid codes and names converts names to codes and leaves codes unchanged."""
    # Mock the API response
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=mock_indicators_no_agg_no_glossary,
    ):
        # Test input: a mix of valid codes, valid names, and an invalid input
        result = core._convert_indicator_codes_to_code(
            [
                "10",
                "Start month of the academic school year (tertiary education)",
                "InvalidName",
            ]
        )

        # Assert:
        # - "10" remains unchanged (valid code)
        # - The valid name is converted to "10403"
        # - "InvalidName" is left unchanged (not found in mapper)
        assert result == ["10", "10403", "InvalidName"]


def test_convert_geo_units_to_code_single_name():
    """Test that a single geo unit name is correctly converted to its corresponding code."""
    # Mock the API response
    with patch("unesco_reader.api.get_geo_units", return_value=mock_geo_units):
        # Test input: a valid geo unit name
        result = core._convert_geo_units_to_code("Aruba")

        # Assert the name is correctly converted to the code
        assert result == "ABW"


def test_convert_geo_units_to_code_single_code():
    """Test that a single geo unit code remains unchanged."""
    # Mock the API response
    with patch("unesco_reader.api.get_geo_units", return_value=mock_geo_units):
        # Test input: a valid geo unit code
        result = core._convert_geo_units_to_code("ABW")

        # Assert the code remains unchanged
        assert result == "ABW"


def test_convert_geo_units_to_code_mixed_inputs():
    """Test that a list with valid codes and names converts names to codes and leaves codes unchanged."""
    # Mock the API response
    with patch("unesco_reader.api.get_geo_units", return_value=mock_geo_units):
        # Test input: a mix of valid codes, valid names, and an invalid input
        result = core._convert_geo_units_to_code(
            ["ABW", "Afghanistan", "InvalidGeoUnit"]
        )

        # Assert:
        # - "ABW" remains unchanged (valid code)
        # - "Afghanistan" is converted to "AFG" (valid name)
        # - "InvalidGeoUnit" is left unchanged (not found in mapper)
        assert result == ["ABW", "AFG", "InvalidGeoUnit"]


def test_normalize_footnotes():
    """Test that footnotes are normalized correctly for different scenarios."""
    # Use the mock data
    data = mock_data_footnotes

    # Apply the function
    result = core._normalize_footnotes(data)

    # Assert for the first record with a single footnote
    assert result[0]["footnotes"] == "Source, Data sources: some footnote"

    # Assert for the second record with no footnotes
    assert result[1]["footnotes"] is None

    # Assert for the third record with multiple footnotes
    assert (
        result[2]["footnotes"]
        == "Source, Data sources: footnote 1 ; Category, Subcategory: footnote 2"
    )


def test_add_indicator_labels():
    """Test that indicator labels are correctly added to the data."""
    # Mock the API response

    mock_indicators = [
        {"indicatorCode": "CR.1", "name": "Completion rate, primary education"},
        {"indicatorCode": "CR.2", "name": "Completion rate, secondary education"},
    ]

    mock_data_with_indicators = [
        {"indicatorId": "CR.1", "geoUnit": "USA", "value": 95},
        {"indicatorId": "CR.2", "geoUnit": "CAN", "value": 85},
        {
            "indicatorId": "CR.3",
            "geoUnit": "MEX",
            "value": 75,
        },  # Not in mock_indicators
    ]

    # test
    with patch("unesco_reader.api.get_indicators", return_value=mock_indicators):
        # Apply the function
        result = core._add_indicator_labels(mock_data_with_indicators)

        # Assert for the first record
        assert result[0]["name"] == "Completion rate, primary education"

        # Assert for the second record
        assert result[1]["name"] == "Completion rate, secondary education"

        # Assert for the third record (not in mock_indicators)
        assert result[2]["name"] is None


def test_add_geo_unit_labels():
    """Test that geo unit labels and region groups are correctly added to the data."""
    # Mock the API response

    _mock_geo_units = [
        {"id": "USA", "name": "United States", "type": "NATIONAL"},
        {"id": "CAN", "name": "Canada", "type": "NATIONAL"},
        {
            "id": "REG1",
            "name": "Region 1",
            "type": "REGIONAL",
            "regionGroup": "Group A",
        },
    ]

    mock_data_with_geo_units = [
        {"geoUnit": "USA", "indicatorId": "CR.1", "value": 95},
        {"geoUnit": "CAN", "indicatorId": "CR.2", "value": 85},
        {"geoUnit": "REG1", "indicatorId": "CR.3", "value": 75},
        {"geoUnit": "MEX", "indicatorId": "CR.4", "value": 65},  # Not in mock_geo_units
    ]

    with patch("unesco_reader.api.get_geo_units", return_value=_mock_geo_units):
        # Apply the function
        result = core._add_geo_unit_labels(mock_data_with_geo_units)

        # Assert for the first record (National Geo Unit)
        assert result[0]["geoUnitName"] == "United States"
        assert result[0]["regionGroup"] is None

        # Assert for the second record (National Geo Unit)
        assert result[1]["geoUnitName"] == "Canada"
        assert result[1]["regionGroup"] is None

        # Assert for the third record (Regional Geo Unit)
        assert result[2]["geoUnitName"] == "Region 1"
        assert result[2]["regionGroup"] == "Group A"

        # Assert for the fourth record (Missing Geo Unit)
        assert result[3]["geoUnitName"] is None
        assert result[3]["regionGroup"] is None


def test_get_data_basic_call():
    """Test that get_data returns a DataFrame for basic inputs."""
    # Mock the private functions and API call
    with patch(
        "unesco_reader.core._convert_indicator_codes_to_code", return_value="CR.1"
    ) as mock_convert_indicators, patch(
        "unesco_reader.core._convert_geo_units_to_code", return_value="ZWE"
    ) as mock_convert_geo_units, patch(
        "unesco_reader.api.get_data", return_value=mock_data_no_hints_no_metadata
    ) as mock_api_call, patch(
        "unesco_reader.core._add_indicator_labels"
    ) as mock_add_indicator_labels, patch(
        "unesco_reader.core._add_geo_unit_labels"
    ) as mock_add_geo_unit_labels:

        # Call get_data with minimal parameters
        result = core.get_data(
            indicator="CR.1", geoUnit="ZWE", footnotes=False, labels=False, raw=False
        )

        # Assert that API call was made with the correct parameters
        mock_api_call.assert_called_once_with(
            indicator="CR.1",
            geoUnit="ZWE",
            start=None,
            end=None,
            footnotes=False,
            geoUnitType=None,
            version=None,
        )

        # Assert private functions were called
        mock_convert_indicators.assert_called_once_with("CR.1")
        mock_convert_geo_units.assert_called_once_with("ZWE")

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Assert _add_indicator_labels and _add_geo_unit_labels were not called
        mock_add_indicator_labels.assert_not_called()
        mock_add_geo_unit_labels.assert_not_called()

        # Assert the DataFrame columns are as expected
        expected_columns = [
            "indicatorId",
            "geoUnit",
            "year",
            "value",
            "magnitude",
            "qualifier",
        ]
        assert list(result.columns) == expected_columns

        assert len(result) > 0


def test_get_data_raw_call():
    """Test that get_data returns raw API data when raw=True."""
    # Mock the private functions and API call

    with patch(
        "unesco_reader.core._convert_indicator_codes_to_code", return_value="CR.1"
    ) as mock_convert_indicators, patch(
        "unesco_reader.core._convert_geo_units_to_code", return_value="ZWE"
    ) as mock_convert_geo_units, patch(
        "unesco_reader.api.get_data", return_value=mock_data_no_hints_no_metadata
    ) as mock_api_call:

        # Call get_data with raw=True
        result = core.get_data(
            indicator="CR.1", geoUnit="ZWE", footnotes=False, labels=False, raw=True
        )

        # Assert that API call was made with the correct parameters
        mock_api_call.assert_called_once_with(
            indicator="CR.1",
            geoUnit="ZWE",
            start=None,
            end=None,
            footnotes=False,
            geoUnitType=None,
            version=None,
        )

        # Assert private functions were called
        mock_convert_indicators.assert_called_once_with("CR.1")
        mock_convert_geo_units.assert_called_once_with("ZWE")

        # Assert the result matches the raw API response
        assert result == mock_data_no_hints_no_metadata["records"]
        assert isinstance(result, list)


def test_get_data_with_labels():
    """Test that get_data returns a DataFrame when labels=True."""
    # Mock the private functions and API call

    mock_labels = [
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2010,
            "value": 88.2,
            "magnitude": None,
            "qualifier": None,
            "name": "Completion rate, primary education, both sexes (%)",
            "geoUnitName": "Zimbabwe",
            "regionGroup": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2012,
            "value": 83,
            "magnitude": None,
            "qualifier": None,
            "name": "Completion rate, primary education, both sexes (%)",
            "geoUnitName": "Zimbabwe",
            "regionGroup": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2014,
            "value": 86.77,
            "magnitude": None,
            "qualifier": None,
            "name": "Completion rate, primary education, both sexes (%)",
            "geoUnitName": "Zimbabwe",
            "regionGroup": None,
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "ZWE",
            "year": 2015,
            "value": 88.07,
            "magnitude": None,
            "qualifier": None,
            "name": "Completion rate, primary education, both sexes (%)",
            "geoUnitName": "Zimbabwe",
            "regionGroup": None,
        },
    ]

    with patch(
        "unesco_reader.core._convert_indicator_codes_to_code", return_value="CR.1"
    ) as mock_convert_indicators, patch(
        "unesco_reader.core._convert_geo_units_to_code", return_value="ZWE"
    ) as mock_convert_geo_units, patch(
        "unesco_reader.api.get_data", return_value=mock_data_no_hints_no_metadata
    ) as mock_api_call, patch(
        "unesco_reader.core._add_indicator_labels", return_value=mock_labels
    ) as mock_add_indicator_labels, patch(
        "unesco_reader.core._add_geo_unit_labels", return_value=mock_labels
    ) as mock_add_geo_unit_labels:

        # Call get_data with labels=True
        result = core.get_data(
            indicator="CR.1", geoUnit="ZWE", footnotes=False, labels=True, raw=False
        )

        # Assert that API call was made with the correct parameters
        mock_api_call.assert_called_once_with(
            indicator="CR.1",
            geoUnit="ZWE",
            start=None,
            end=None,
            footnotes=False,
            geoUnitType=None,
            version=None,
        )

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        # Assert the DataFrame columns are as expected
        expected_columns = [
            "indicatorId",
            "geoUnit",
            "year",
            "value",
            "magnitude",
            "qualifier",
            "name",
            "geoUnitName",
            "regionGroup",
        ]
        assert list(result.columns) == expected_columns


def test_get_data_with_footnotes():
    """Test that get_data returns a DataFrame with normalized footnotes when footnotes=True."""
    # Mock the private functions and API call

    mock_data_with_footnotes = [
        {
            "indicatorId": "CR.1",
            "geoUnit": "AFG",
            "year": 2011,
            "value": 1,
            "magnitude": None,
            "qualifier": None,
            "footnotes": [
                {"type": "Source", "subtype": "Data sources", "value": "some footnote"}
            ],
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "AFG",
            "year": 2015,
            "value": 2,
            "magnitude": None,
            "qualifier": None,
            "footnotes": [],
        },
        {
            "indicatorId": "CR.1",
            "geoUnit": "AFG",
            "year": 2022,
            "value": 3,
            "magnitude": None,
            "qualifier": None,
            "footnotes": [
                {"type": "Source", "subtype": "Data sources", "value": "footnote 1"},
                {"type": "Category", "subtype": "Subcategory", "value": "footnote 2"},
            ],
        },
    ]

    with patch(
        "unesco_reader.core._convert_indicator_codes_to_code", return_value="CR.1"
    ) as mock_convert_indicators, patch(
        "unesco_reader.core._convert_geo_units_to_code", return_value="AFG"
    ) as mock_convert_geo_units, patch(
        "unesco_reader.api.get_data", return_value=mock_data_no_hints_no_metadata
    ) as mock_api_call, patch(
        "unesco_reader.core._normalize_footnotes", return_value=mock_data_with_footnotes
    ) as mock_normalize_footnotes:

        # Call get_data with footnotes=True
        result = core.get_data(
            indicator="CR.1", geoUnit="AFG", footnotes=True, labels=False, raw=False
        )

        # Assert that API call was made with the correct parameters
        mock_api_call.assert_called_once_with(
            indicator="CR.1",
            geoUnit="AFG",
            start=None,
            end=None,
            footnotes=True,
            geoUnitType=None,
            version=None,
        )

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        assert "footnotes" in result.columns


def test_get_data_no_data_error():
    """Test that get_data raises NoDataError when no data is returned."""
    # Mock the API response with no records
    mock_no_data_response = {"hints": [], "records": [], "indicatorMetadata": []}

    with patch(
        "unesco_reader.core._convert_indicator_codes_to_code", return_value="CR.1"
    ) as mock_convert_indicators, patch(
        "unesco_reader.core._convert_geo_units_to_code", return_value="ZWE"
    ) as mock_convert_geo_units, patch(
        "unesco_reader.api.get_data", return_value=mock_no_data_response
    ) as mock_api_call:

        # Call get_data and expect NoDataError
        with pytest.raises(NoDataError, match="No data found for the given parameters"):
            core.get_data(
                indicator="CR.1",
                geoUnit="ZWE",
                footnotes=False,
                labels=False,
                raw=False,
            )


def test_get_metadata_single_indicator():
    """Test that get_metadata returns metadata for a single valid indicator."""
    # Mock the API response
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=mock_indicators_no_agg_no_glossary,
    ) as mock_api_call, patch(
        "unesco_reader.core._convert_indicator_codes_to_code", return_value=["10"]
    ) as mock_convert_indicators:

        # Call get_metadata
        result = core.get_metadata(
            indicator="Official entrance age to early childhood educational development (years)"
        )

        # Assert that API call was made
        mock_api_call.assert_called_once_with(
            disaggregations=False, glossaryTerms=False, version=None
        )

        # Assert private function was called
        mock_convert_indicators.assert_called_once_with(
            ["Official entrance age to early childhood educational development (years)"]
        )

        # Assert the result contains the correct metadata
        assert len(result) == 1
        assert result[0]["indicatorCode"] == "10"


def test_get_metadata_with_invalid_indicator(caplog):
    """Test that a warning is logged when some requested indicators are not found."""
    # Mock the API response
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=mock_indicators_no_agg_no_glossary,
    ) as mock_api_call, patch(
        "unesco_reader.core._convert_indicator_codes_to_code",
        return_value=["10", "InvalidCode"],
    ) as mock_convert_indicators:

        # Call get_metadata with one valid and one invalid indicator
        result = core.get_metadata(
            indicator=[
                "Official entrance age to early childhood educational development (years)",
                "InvalidIndicator",
            ]
        )

        # Assert that API call was made
        mock_api_call.assert_called_once_with(
            disaggregations=False, glossaryTerms=False, version=None
        )

        # Assert private function was called
        mock_convert_indicators.assert_called_once_with(
            [
                "Official entrance age to early childhood educational development (years)",
                "InvalidIndicator",
            ]
        )

        # Check that a warning is logged
        assert (
            "Metadata not found for the following indicators: ['InvalidCode']"
            in caplog.text
        )

        # Assert the result contains only the valid metadata
        assert len(result) == 1
        assert result[0]["indicatorCode"] == "10"


def test_get_metadata_invalid_indicator():
    """Test that get_metadata raises NoDataError when an invalid indicator is requested."""
    # Mock the API response
    with patch(
        "unesco_reader.api.get_indicators", return_value=[]
    ) as mock_api_call, patch(
        "unesco_reader.core._convert_indicator_codes_to_code",
        return_value=["InvalidCode"],
    ) as mock_convert_indicators:

        # Call get_metadata and expect NoDataError
        with pytest.raises(
            NoDataError, match="No indicator metadata found for the given indicators"
        ):
            core.get_metadata(indicator="InvalidIndicator")


def test_indicators_df():
    """Test that _indicators_df correctly processes indicator data using mock_indicators_no_agg_no_glossary."""
    # Call the function with mock data
    result = core._indicators_df(mock_indicators_no_agg_no_glossary)

    # Assert the result is a DataFrame
    assert isinstance(result, pd.DataFrame)

    # Assert the expected columns are present
    expected_columns = {
        "indicatorCode",
        "name",
        "lastDataUpdate",
        "lastDataUpdateDescription",
        "min",
        "max",
        "totalRecordCount",
        "geoUnitType",
    }
    assert set(result.columns).issuperset(expected_columns)


def test_available_indicators_success():
    """Test that available_indicators returns a correctly processed DataFrame."""
    # Mock the API call

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators
        result = core.available_indicators()

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Assert the DataFrame columns
        expected_columns = {
            "indicatorCode",
            "name",
            "theme",
            "lastDataUpdate",
            "lastDataUpdateDescription",
            "min",
            "max",
            "totalRecordCount",
            "geoUnitType",
        }
        assert set(result.columns).issuperset(expected_columns)


def test_available_indicators_filter_theme():
    """Test that available_indicators returns a correctly processed DataFrame when filtering by theme."""
    # Mock the API call

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators
        result = core.available_indicators(theme="EDUCATION")

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        assert len(result) == 1
        assert result["theme"].unique() == "EDUCATION"


def test_available_indicators_filter_min_year():
    """Test that available_indicators returns a correctly processed DataFrame when filtering by min_year."""
    # Mock the API call

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators
        result = core.available_indicators(minStart=1990)

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        assert len(result) == 1
        assert result["min"].unique() == 1970


def test_available_indicators_filter_geo_unit_type_regional():
    """Test when filtering for specific geo unit - regional"""

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators
        result = core.available_indicators(geoUnitType="REGIONAL")

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        assert len(result) == 1
        assert result["indicatorCode"].unique() == "10403"
        assert result["geoUnitType"].unique() == "ALL"


def test_available_indicators_filter_geo_unit_type_national():
    """Test when filtering for specific geo unit - regional"""

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators
        result = core.available_indicators(geoUnitType="NATIONAL")

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2


def test_available_indicators_filter_geo_unit_type_all():
    """Test when filtering for specific geo unit - regional"""

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators
        result = core.available_indicators(geoUnitType="ALL")

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["geoUnitType"].unique() == "ALL"


def test_available_indicators_raw_with_filter():
    """Test that available_indicators returns raw API data when raw=True and filters are applied."""

    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators with raw=True and filters
        result = core.available_indicators(theme="EDUCATION", raw=True)

        # Assert the result matches the raw API response
        assert result == [
            {
                "indicatorCode": "10",
                "name": "Official entrance age to early childhood educational development (years)",
                "theme": "EDUCATION",
                "lastDataUpdate": "2024-10-29",
                "lastDataUpdateDescription": "September 2024 Data Release",
                "dataAvailability": {
                    "totalRecordCount": 4675,
                    "timeLine": {"min": 1970, "max": 2023},
                    "geoUnits": {"types": ["NATIONAL"]},
                },
            }
        ]


def test_available_indicators_no_data_error():
    """Test that available_indicators raises NoDataError when no data is returned."""
    # Mock the API response with no records
    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]
    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators and expect NoDataError
        with pytest.raises(
            NoDataError, match="No indicators found for the given parameters"
        ):
            core.available_indicators(theme="INVALID_THEME")


def test_available_indicators_theme_warning_logged(caplog):
    """Test available_indicators logs a warning when some requested themes are not found."""

    # Mock the API response with no records
    _mock_indicators_no_agg_no_glossary = [
        {
            "indicatorCode": "10",
            "name": "Official entrance age to early childhood educational development (years)",
            "theme": "EDUCATION",
            "lastDataUpdate": "2024-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 4675,
                "timeLine": {"min": 1970, "max": 2023},
                "geoUnits": {"types": ["NATIONAL"]},
            },
        },
        {
            "indicatorCode": "10403",
            "name": "Start month of the academic school year (tertiary education)",
            "theme": "DEMOGRAPHICS",
            "lastDataUpdate": "2010-10-29",
            "lastDataUpdateDescription": "September 2024 Data Release",
            "dataAvailability": {
                "totalRecordCount": 5192,
                "timeLine": {"min": 1991, "max": 2023},
                "geoUnits": {"types": ["NATIONAL", "REGIONAL"]},
            },
        },
    ]

    with patch(
        "unesco_reader.api.get_indicators",
        return_value=_mock_indicators_no_agg_no_glossary,
    ) as mock_api_call:

        # Call available_indicators with one valid and one invalid theme
        result = core.available_indicators(theme=["EDUCATION", "INVALID_THEME"])

        # Check that a warning is logged
        assert (
            "Indicators not found for the following themes: ['INVALID_THEME']"
            in caplog.text
        )

        # Assert the result contains only the valid metadata
        assert len(result) == 1
        assert result["theme"].unique() == "EDUCATION"


def test_available_geo_units_success():
    """Test that available_geo_units returns a correctly processed DataFrame."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_geo_units", return_value=mock_geo_units
    ) as mock_api_call:

        # Call available_geo_units
        result = core.available_geo_units()

        # Assert the API call was made
        mock_api_call.assert_called_once_with(version=None)

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Assert the DataFrame columns
        expected_columns = {
            "id",
            "name",
            "type",
            "regionGroup",
        }
        assert set(result.columns).issuperset(expected_columns)


def test_available_geo_units_raw_success():
    """Test that available_geo_units returns a correctly processed list when raw is requested."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_geo_units", return_value=mock_geo_units
    ) as mock_api_call:

        # Call available_geo_units
        result = core.available_geo_units(raw=True)

        # Assert the API call was made
        mock_api_call.assert_called_once_with(version=None)

        # Assert the result is a DataFrame
        assert isinstance(result, list)


def test_available_geo_units_filter():
    """Test that available_geo_units returns a correctly processed list when raw is requested."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_geo_units", return_value=mock_geo_units
    ) as mock_api_call:

        # Call available_geo_units
        result = core.available_geo_units(geo_unit_type="REGIONAL")

        # Assert the API call was made
        mock_api_call.assert_called_once_with(version=None)

        assert len(result) == 1
        assert result["type"].unique() == "REGIONAL"


def test_available_geo_units_filter_raw():
    """Test that available_geo_units returns a correctly processed list when raw is requested."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_geo_units", return_value=mock_geo_units
    ) as mock_api_call:

        # Call available_geo_units
        result = core.available_geo_units(geo_unit_type="REGIONAL", raw=True)

        # Assert the API call was made
        mock_api_call.assert_called_once_with(version=None)

        assert len(result) == 1


def test_available_themes_success():
    """Test that available_themes returns a correctly processed DataFrame."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_default_version", return_value=mock_default_version
    ) as mock_api_call:

        # Call available_themes
        result = core.available_themes()

        # Assert the API call was made
        mock_api_call.assert_called_once_with()

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Assert the DataFrame columns
        expected_columns = {"theme", "lastUpdate", "description"}
        assert set(result.columns).issuperset(expected_columns)


def test_available_themes_success_raw():
    """Test that available_themes returns a correctly processed list of dicts."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_default_version", return_value=mock_default_version
    ) as mock_api_call:

        # Call available_themes
        result = core.available_themes(raw=True)

        # Assert the result is a DataFrame
        assert isinstance(result, list)
        assert len(result) == 4


def test_default_version():
    """Test that default version."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_default_version", return_value=mock_default_version
    ) as mock_api_call:

        # Call available_themes
        result = core.default_version()

        # Assert the result is a DataFrame
        assert isinstance(result, str)


def test_available_versions_success():
    """Test that available_versions returns a correctly processed DataFrame."""
    # Mock the API call
    with patch(
        "unesco_reader.api.get_versions", return_value=mock_list_versions
    ) as mock_api_call:

        # Call available_versions
        result = core.available_versions()

        # Assert the API call was made
        mock_api_call.assert_called_once_with()

        # Assert the result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Assert the DataFrame columns
        expected_columns = {"version", "publicationDate", "description"}
        assert set(result.columns).issuperset(expected_columns)


def test_available_versions_success_raw():
    """Test that available_versions returns a correctly processed list when raw is passed"""

    _mock_list_versions = [
        {
            "version": "20241030-9d4d089e",
            "publicationDate": "2024-10-30T17:28:00.868Z",
            "description": "Drop data for CIV on MYS for 1988 and 1998 and update some other education datapoints",
            "themeDataStatus": [
                {
                    "theme": "EDUCATION",
                    "lastUpdate": "2024-10-29",
                    "description": "September 2024 Data Release",
                },
                {
                    "theme": "SCIENCE_TECHNOLOGY_INNOVATION",
                    "lastUpdate": "2024-02-24",
                    "description": "February 2024 Data Release",
                },
                {
                    "theme": "CULTURE",
                    "lastUpdate": "2023-11-25",
                    "description": "November 2023 Data Release",
                },
                {
                    "theme": "DEMOGRAPHIC_SOCIOECONOMIC",
                    "lastUpdate": "2024-10-29",
                    "description": "September 2024 Data Release",
                },
            ],
        }
    ]
    # Mock the API call
    with patch(
        "unesco_reader.api.get_versions", return_value=_mock_list_versions
    ) as mock_api_call:

        # Call available_versions
        result = core.available_versions(raw=True)

        # Assert the API call was made
        mock_api_call.assert_called_once_with()

        # Assert the result is a DataFrame
        assert isinstance(result, list)
        assert len(result) == 1
