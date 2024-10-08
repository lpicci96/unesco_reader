"""Wrapper for the UNESCO API

This module wraps the API endpoints that exist in the UIS API.
"""

import requests


BASE_URL: str = "https://api.uis.unesco.org"


def get_data(indicator: str | list[str] = None,
             geo_unit: str | list[str] = None,
             start: int = None,
             end: int = None,
             indicator_metadata: bool = False,
             footnotes: bool = False,
             geo_unit_type: str = None,
             version: str = None,
             ) -> dict:
    """Function to get indicator data. Wrapper for the indicator data endpoint

    At least an indicator or a geo_unit must be provided.

    For more information about this endpoint visit: https://api.uis.unesco.org/api/public/documentation/operations/getIndicatorData

    Args:
        indicator: Ids of the requested indicators. Returns all available indicators if not provided.TODO: add information about getting available indicators
        geo_unit: Ids of the requested geographies (countries or regions). Returns all available geographies if not provided. TODO: add information about getting available geo units
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

    end_point: str = f"{BASE_URL}/api/public/data/indicators"

    if indicator is None and geo_unit is None:
        raise ValueError("At least an indicator or a geo_unit must be provided")

    querystring = {}
    if indicator:
        if isinstance(indicator, str):
            indicator = [indicator]
        querystring["indicator"] = indicator
    if geo_unit:
        if isinstance(geo_unit, str):
            geo_unit = [geo_unit]
        querystring["geoUnit"] = geo_unit
    if start:
        querystring["start"] = start
    if end:
        querystring["end"] = end
    if indicator_metadata:
        querystring["indicatorMetadata"] = "true"
    else:
        querystring["indicatorMetadata"] = "false"
    if footnotes:
        querystring["footnotes"] = "true"
    else:
        querystring["footnotes"] = "false"
    if geo_unit_type:
        querystring["geoUnitType"] = geo_unit_type
    if version:
        querystring["version"] = version

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    response = requests.get(end_point, headers=headers, params=querystring)

    return response.json()


def get_geo_units(version: str = None) -> dict:
    """Function to get available geographies.

    Args:
        version: The api version to read the data from. If not provided, defaults to the current default latest version.
    """

    end_point: str = f"{BASE_URL}/api/public/definitions/geounits"

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    querystring = {}
    if version:
        querystring["version"] = version

    response = requests.get(end_point, headers=headers, params=querystring)
    return response.json()


def get_indicators(disaggregations: bool = False, glossary_terms: bool = False, version: str = None) -> dict:
    """Function to get available indicators.

    Args:
        disaggregations: Whether to include disaggregations in the response. Default is False
        glossary_terms: Whether to include glossary terms in the response. Default is False
        version: The version to list the indicators definitions for. If not provided, the current default version is used.
    """

    end_point: str = f"{BASE_URL}/api/public/definitions/indicators"

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    querystring = {}
    if disaggregations:
        querystring["disaggregations"] = "true"
    else:
        querystring["disaggregations"] = "false"
    if glossary_terms:
        querystring["glossaryTerms"] = "true"
    else:
        querystring["glossaryTerms"] = "false"
    if version:
        querystring["version"] = version

    response = requests.get(end_point, headers=headers, params=querystring)
    return response.json()


def get_versions() -> dict:
    """Get all published data versions
    """

    end_point: str = f"{BASE_URL}/api/public/versions"

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    response = requests.get(end_point, headers=headers)
    return response.json()


def get_default_version() -> dict:
    """Get the current default data version
    """

    end_point: str = f"{BASE_URL}/api/public/versions/default"

    headers = {
        "Accept-Encoding": "gzip",
        "Accept": "application/json"
    }

    response = requests.get(end_point, headers=headers)
    return response.json()



