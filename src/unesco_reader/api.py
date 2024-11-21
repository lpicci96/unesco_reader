"""Wrapper for the UNESCO API

This module wraps the API endpoints that exist in the UIS API.
For more information about the API visit: https://api.uis.unesco.org/api/public/documentation/

Endpoints:

- get_data: Get indicator data
- get_geo_units: Get available geo units
- get_indicators: Get available indicators
- get_versions: Get all published data versions
- get_default_version: Get the current default data version

"""

import requests

from unesco_reader.config import GeoUnitType, logger
from unesco_reader.exceptions import TooManyRecordsError


API_URL: str = "https://api.uis.unesco.org"
TIMEOUT: int = 30


def _check_valid_version(version: str | None) -> None:
    """Check if the version is valid. If the version is not None, it must be a string and must be a valid version in the API

    Args:
        version: The version to check

    Raises:
        ValueError: If the version is not valid
    """

    if version is not None and not isinstance(version, str):
        raise ValueError("Data version must be a string")

    # check that the version is a valid version in the api
    if version is not None:
        versions = get_versions()
        if version not in [v["version"] for v in versions]:
            raise ValueError(f"Invalid data version: {version}")


def _check_for_too_many_records(response: requests.Response) -> None:
    """Check if too many records have been requested.

    If too many records have been requested or the URI is too long, raise an error. A maximum of 100 000 records can be returned in a single query. If more records are requested, an error is raised.
    If this error occurs, the response is 400 and the message is {"message":"Too much data requested (224879 records), please reduce the amount of records queried to less than 100000 by using the available filter options.","error":"Bad Request","statusCode":400}

    If the URI is too long, it means too many parameters have been passed to the API and an error is raised.

    Args:
        response: The response object from the API

    Raises:
        TooManyRecordsError: If too many records have been requested
        TooManyRecordsError: If the URI is too long
    """

    # if too many records are requested raise an error with the error message from the API
    if response.status_code == 400:
        error_message = response.json().get("message")
        if "Too much data requested" in error_message:
            raise TooManyRecordsError(error_message)

    # if URI Too Long raise a custom error rather than the default one from requests, indicating that too many parameters have been passed to the API
    if response.status_code == 414:
        raise TooManyRecordsError(
            "Too many parameters passed to the API. Please reduce the amount of parameters passed to the API"
        )


def _make_request(endpoint: str, params: dict | None = None) -> dict | list:
    """Make a request to an API endpoint and return the response object

    Args:
        endpoint: The endpoint to make the request to
        params: Parameters to pass to the endpoint

    Returns:
        The response object as a dictionary
    """

    headers = {"Accept-Encoding": "gzip", "Accept": "application/json"}

    if params is not None:
        params = {k: v for k, v in sorted(params.items()) if v is not None}

        # check if the version is valid
        if "version" in params:
            _check_valid_version(params["version"])

    try:
        response = requests.get(
            f"{API_URL}{endpoint}", headers=headers, params=params, timeout=TIMEOUT
        )
        _check_for_too_many_records(
            response
        )  # check if too many records have been requested
        response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        return response.json()

    except requests.exceptions.Timeout as e:
        raise TimeoutError(f"Request timed out. Error: {str(e)}")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error occurred: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to API. Error: {str(e)}")


def _convert_bool_to_string(value: bool | None) -> str | None:
    """Convert a boolean to a string. If the value is None, return None"""

    return None if value is None else "true" if value else "false"


def get_data(
    indicator: str | list[str] | None = None,
    geoUnit: str | list[str] | None = None,
    start: int | None = None,
    end: int | None = None,
    indicatorMetadata: bool = False,
    footnotes: bool = False,
    geoUnitType: GeoUnitType | None = None,
    version: str | None = None,
) -> dict:
    """Function to get indicator data. Wrapper for the indicator data endpoint

    At least an indicator or a geo_unit must be provided.

    For more information about this endpoint visit: https://api.uis.unesco.org/api/public/documentation/operations/getIndicatorData

    Args:
        indicator: IDs of the requested indicators. Returns all available indicators if not provided.
        geoUnit: IDs of the requested geographies (countries or regions). Returns all available geographies if not provided.
        start: The start year to request data for. Includes the year itself. Default is the earliest available year.
        end: The end year to request data for. Includes the year itself. Default is the latest available year
        indicatorMetadata: Include indicator metadata in the response. Default is False
        footnotes: Include footnotes (per data point) in the response. Default is False
        geoUnitType: The type of geography to request data for. Allowed values are NATIONAL and REGIONAL
                       If a geo_unit is provided, this parameter is ignored. Default is both national and regional data
        version: The API data version to request. If not provided, defaults to the current default version.

    Returns:
        A dictionary with the response data
    """

    end_point: str = "/api/public/data/indicators"

    # if indicator is None and geo_unit is None, raise an error
    if indicator is None and geoUnit is None:
        raise ValueError("At least one indicator or one geo_unit must be provided")

    # if geo_unit and geo_unit_type is specified, log a message and ignore geo_unit_type
    if geoUnit and geoUnitType:
        logger.warning(
            "Both geo_unit and geo_unit_type are specified. geo_unit_type will be ignored"
        )
        geoUnitType = None  # set to None to ignore it to avoid unexpected results from API call and to avoid unnecessary API calls

    # check if the geo_unit_type is valid
    if geoUnitType is not None and geoUnitType not in ["NATIONAL", "REGIONAL"]:
        raise ValueError("geo_unit_type must be either NATIONAL or REGIONAL")

    # handle cases where start is greater than end
    if start and end and start > end:
        raise ValueError(
            f"Start year ({start}) cannot be greater than end year ({end})"
        )

    params = {
        "indicator": [indicator] if isinstance(indicator, str) else indicator,
        "geoUnit": [geoUnit] if isinstance(geoUnit, str) else geoUnit,
        "start": start,
        "end": end,
        "indicatorMetadata": _convert_bool_to_string(indicatorMetadata),
        "footnotes": _convert_bool_to_string(footnotes),
        "geoUnitType": geoUnitType,
        "version": version,
    }

    return _make_request(end_point, params)


def get_geo_units(version: str | None = None) -> list[dict]:
    """Get geo units

    Get all available geo units for a given API data version (or the current default version if no explicit version is provided).

    Args:
        version: The API data version to query. If not provided, defaults to the current default version.

    Returns:
        A list of dictionaries with geo units
    """

    end_point: str = f"/api/public/definitions/geounits"

    params = {"version": version}

    return _make_request(end_point, params)


def get_indicators(
    disaggregations: bool = False,
    glossaryTerms: bool = False,
    version: str | None = None,
) -> list[dict]:
    """Get available indicators

    Get all available indicators, optionally with glossary terms and disaggregations, for the given API data version
    (or the current default version if no explicit version is provided).

    Args:
        disaggregations: Include disaggregations in the response. Default is False
        glossaryTerms: Include glossary terms in the response. Default is False
        version: The API data version to query. If not provided, the current default version is used.

    Returns:
        A list of dictionaries with the available indicators
    """

    end_point: str = "/api/public/definitions/indicators"

    params = {
        "disaggregations": _convert_bool_to_string(disaggregations),
        "glossaryTerms": _convert_bool_to_string(glossaryTerms),
        "version": version,
    }

    return _make_request(end_point, params)


def get_versions() -> list[dict]:
    """Get all published data versions

    Returns:
        A list of dictionaries with the different data versions and their metadata
    """

    end_point: str = "/api/public/versions"

    return _make_request(end_point)


def get_default_version() -> dict:
    """Get the current default data version

    Returns:
        A dictionary with the default data version and its metadata
    """

    end_point: str = "/api/public/versions/default"

    return _make_request(end_point)
