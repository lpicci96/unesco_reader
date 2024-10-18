"""Wrapper for the UNESCO API

This module wraps the API endpoints that exist in the UIS API.
For more information about the API visit: https://api.uis.unesco.org/api/public/documentation/
"""

import requests


API_URL: str = "https://api.uis.unesco.org"


def _get(endpoint: str, params: dict | None = None) -> dict:
    """ Make a request to an API endpoint and return the response object

    Args:
        endpoint: The endpoint to make the request to
        params: Parameters to pass to the endpoint

    Returns:
        The response object as a dictionary
    """

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    try:
        response = requests.get(f"{API_URL}{endpoint}", headers=headers, params=params, timeout=10)

        # check if 400 error raised meaning too many records requested
        if response.status_code == 400:
            raise ValueError("Too many records requested. Please reduce the number of records request by "
                             "splitting the request into multiple smaller requests"
                             " or consider using the bulk API")

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

    if value is None:
        return None
    return "true" if value else "false"


def _build_querystring(**kwargs) -> dict:
    """Build a querystring from a dictionary of parameters

    Builds a querystring for the following parameters:
    - indicator
    - geoUnit
    - start
    - end
    - indicatorMetadata
    - footnotes
    - geoUnitType
    - version
    - disaggregations
    - glossaryTerms

    Args:
        params: The parameters to build the querystring from

    Returns:
        A querystring
    """

    querystring = {
        "indicator": [kwargs.get('indicator')] if isinstance(kwargs.get('indicator'), str) else kwargs.get('indicator'),
        "geoUnit": [kwargs.get('geo_unit')] if isinstance(kwargs.get('geo_unit'), str) else kwargs.get('geo_unit'),
        "start": kwargs.get('start'),
        "end": kwargs.get('end'),
        "indicatorMetadata": _convert_bool_to_string(kwargs.get('indicator_metadata')),
        "footnotes": _convert_bool_to_string(kwargs.get('footnotes')),
        "geoUnitType": kwargs.get('geo_unit_type'),
        "version": kwargs.get('version'),
        "disaggregations": _convert_bool_to_string(kwargs.get('disaggregations')),
        "glossaryTerms": _convert_bool_to_string(kwargs.get('glossary_terms')),
    }

    # Remove any key-value pairs where the value is None and sort the dictionary to ensure use of caching
    querystring = {k: v for k, v in sorted(querystring.items()) if v is not None}

    return querystring


def get_data(indicator: str | list[str] = None,
             geo_unit: str | list[str] = None,
             start: int = None,
             end: int = None,
             indicator_metadata: bool = False,
             footnotes: bool = False,
             geo_unit_type: str = None, #TODO create a type for this
             version: str = None,
             ) -> dict:
    """Function to get indicator data. Wrapper for the indicator data endpoint

    At least an indicator or a geo_unit must be provided.

    For more information about this endpoint visit: https://api.uis.unesco.org/api/public/documentation/operations/getIndicatorData

    Args:
        indicator: Ids of the requested indicators. Returns all available indicators if not provided.
        geo_unit: Ids of the requested geographies (countries or regions). Returns all available geographies if not provided.
        start: The start year to request data for. Includes the year itself. Default is the earliest available year
        end: The end year to request data for. Includes the year itself. Default is the latest available year
        indicator_metadata: Whether to include indicator metadata in the response. Default is False
        footnotes: Whether to include footnotes (per data point) in the response. Default is False
        geo_unit_type: The type of geography to request data for. Allowed values are NATIONAL and REGIONAL
                       If a geo_unit is provided, this parameter is ignored. Default is both national and regional data
                       Available values: NATIONAL, REGIONAL
        version: The api version to read the data from. If not provided, defaults to the current default latest version.

    Returns:
        A dictionary with the response data
    """

    end_point: str = "/api/public/data/indicators"

    if indicator is None and geo_unit is None:
        raise ValueError("At least one indicator or one geo_unit must be provided")

    querystring = _build_querystring(**locals())
    response = _get(end_point, querystring)
    return response


def get_geo_units(version: str = None) -> dict:
    """Function to get available geographies.

    Args:
        version: The api version to read the data from. If not provided, defaults to the current default latest version.
    """

    end_point: str = f"/api/public/definitions/geounits"

    querystring = _build_querystring(**locals())
    response = _get(end_point, querystring)
    return response


def get_indicators(disaggregations: bool = False, glossary_terms: bool = False, version: str = None) -> dict:
    """Function to get available indicators.

    Args:
        disaggregations: Whether to include disaggregations in the response. Default is False
        glossary_terms: Whether to include glossary terms in the response. Default is False
        version: The version to list the indicators definitions for. If not provided, the current default version is used.
    """

    end_point: str = "/api/public/definitions/indicators"

    querystring = _build_querystring(**locals())
    response = _get(end_point, querystring)
    return response


def get_versions() -> dict:
    """Get all published data versions
    """

    end_point: str = "/api/public/versions"

    response = _get(end_point)
    return response


def get_default_version() -> dict:
    """Get the current default data version
    """

    end_point: str = "/api/public/versions/default"

    response = _get(end_point)
    return response



