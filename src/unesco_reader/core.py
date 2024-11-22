"""Core functions for the unesco_reader package

This module contains the core functions for the unesco_reader package.
These functions are used to interact with the UIS API to get data, metadata, and available indicators and geo units, themes, and data versions.
The module handles indicator and entity conversions and normalizes data for easy processing to dataframes.
The module handles errors and logs hints from the API responses
"""

import pandas as pd
from typing import Literal

from unesco_reader import api
from unesco_reader.config import logger, GeoUnitType
from unesco_reader.exceptions import TooManyRecordsError, NoDataError


def _log_hints(response: dict) -> None:
    """If there are any hints in the response, log them

    If a response from the api contains hints, it means there are some issues with the request or the data.
    This function logs the hints as warnings. There may be multiple hints, so they are logged one by one.

    Args:
        response: The response from the API
    """

    if "hints" in response and len(response["hints"]) > 0:
        for hint in response["hints"]:
            logger.warning(hint["message"])


def _convert_codes(indicators: str | list[str], mapper: dict) -> str | list[str]:
    """Convert names to their respective codes

    This function is used to convert geo units or indicators from names to their respective codes.
    If the name is already a code, it is left as is.

    Args:
        indicators: The indicator name or list of indicator names to convert to codes
        mapper: The dictionary mapping names to codes

    Returns:
        The code or list of codes
    """

    # Ensure indicators is a list for uniform processing and keep track if it was a single value (str)
    is_single = isinstance(indicators, str)
    indicators = [indicators] if is_single else indicators

    converted_indicators = (
        []
    )  # Initialize an empty list to store the converted indicators
    for indicator in indicators:
        # Check if the indicator is already a code
        if indicator in mapper.values():
            converted_indicators.append(indicator)
        # Check if the indicator is a name and convert to code
        elif indicator in mapper.keys():
            converted_indicators.append(mapper[indicator])
        # else return the original indicator as a fallback
        else:
            converted_indicators.append(
                indicator
            )  # Append the original indicator as a fallback

    # Return a string if a single indicator was provided, otherwise return a list
    return converted_indicators[0] if is_single else converted_indicators


def _convert_indicator_codes_to_code(indicators: str | list[str]) -> str | list[str]:
    """Convert indicators to their respective codes

    This function converts the indicator names to their respective codes. If the indicator is already a code, it is left as is.
    If the indicator is not found, it is left as is and will be handled as an error by the API.

    Args:
        indicators: The indicator name or list of indicator names to convert to codes

    Returns:
        The indicator code or list of indicator codes
    """

    # Fetch the indicator data from the API only once
    indicator_data = api.get_indicators()
    mapper = {
        unit["name"]: unit["indicatorCode"] for unit in indicator_data
    }  # Create a dictionary mapping names to codes

    return _convert_codes(indicators, mapper)


def _convert_geo_units_to_code(geo_units: str | list[str]) -> str | list[str]:
    """Convert geo units to their respective codes

    This function converts the geo unit names to their respective codes. If the geo unit is already a code, it is left as is.
    If the geo unit is not found, it is left as is and will be handled as an error by the API.

    Args:
        geo_units: The geo unit name or list of geo unit names to convert to codes
    """

    geo_units_data = api.get_geo_units()  # Fetch the geo unit data
    mapper = {
        unit["name"]: unit["id"] for unit in geo_units_data
    }  # Create a dictionary mapping names to codes

    return _convert_codes(geo_units, mapper)


def _normalize_footnotes(data: list[dict]) -> list[dict]:
    """Normalize the footnotes column

    The footnotes can have 1 or multiple records with keys - "type", "subtype", "value".
    eg:
    {...
    'footnotes': [{'type': 'Source',
    'subtype': 'Data sources',
    'value': "Country's submission to UIS Survey of Formal Education Questionnaire A"}],
    ...
    }

    This function normalizes the footnotes into a single string for a dataframe column with the structure:
    "type, subtype: value"
    eg:
    "Source, Data sources: Country's submission to UIS Survey of Formal Education Questionnaire A"

    For multiple footnotes, the normalized string is concatenated with a semicolon.
    """

    for record in data:
        if len(record["footnotes"]) == 0:
            record["footnotes"] = None
            continue
        footnotes_str = [
            f"{footnote['type']}, {footnote['subtype']}: {footnote['value']}"
            for footnote in record["footnotes"]
        ]
        record["footnotes"] = " ; ".join(footnotes_str)

    return data


def _add_indicator_labels(data: list[dict]) -> list[dict]:
    """Add indicator labels to the data

    Args:
        data: The data to which to add the indicator labels

    Returns:
        The data with the indicator labels added
    """

    # Get indicators and create a dictionary mapping indicatorCode to indicator details
    indicators = api.get_indicators()
    indicator_map = {
        indicator["indicatorCode"]: indicator["name"] for indicator in indicators
    }

    # Loop over the data and add the indicator name using the map for fast lookup
    for record in data:
        record["name"] = indicator_map.get(record["indicatorId"], None)

    return data


def _add_geo_unit_labels(data: list[dict]) -> list[dict]:
    """Add geo unit labels to the data. For regions, add both the region name and the region group

    Args:
        data: The data to which to add the geo unit labels

    Returns:
        The data with the geo unit labels added
    """

    # Get geo units and create a dictionary mapping geoUnit to geoUnit details
    geo_units = api.get_geo_units()
    geo_unit_map = {geo_unit["id"]: geo_unit["name"] for geo_unit in geo_units}
    region_group_map = {
        geo_unit["id"]: (
            geo_unit["regionGroup"] if geo_unit["type"] == "REGIONAL" else None
        )
        for geo_unit in geo_units
    }

    # Loop over the data and add the geo unit name using the map for fast lookup
    for record in data:
        record["geoUnitName"] = geo_unit_map.get(record["geoUnit"], None)
        record["regionGroup"] = region_group_map.get(record["geoUnit"], None)

    return data


def get_data(
    indicator: str | list[str] | None = None,
    geoUnit: str | list[str] | None = None,
    start: int | None = None,
    end: int | None = None,
    labels: bool = False,
    geoUnitType: GeoUnitType | None = None,
    footnotes: bool = False,
    *,
    raw: bool = False,
    version: str | None = None,
) -> pd.DataFrame | list[dict]:
    """Get UIS data

    Query the UIS API for data based on the given parameters. At least one indicator or one geo_unit must be provided. If only indicators are provided, data for all geographies is returned, and vice versa. To see available indicators or geographies, use the `available_indicators` or `available_geo_units` functions respectively. If both a geo_unit and geo_unit_type are provided, the geo_unit_type is ignored.

    Args:
        indicator: The indicator code or name to request data for. If None, data for all indicators is returned. By default, None. To see all available indicators, use the `available_indicators` function.
        geoUnit: The geo unit code or name to request data for. If None, data for all geo units is returned. By default, None. To see all available geo units, use the `available_geo_units` function.
        start: The start year to request data for. Includes the year itself. Default is None, which returns the earliest available year.
        end: The end year to request data for. Includes the year itself. Default is None, which returns the latest available year.
        labels: If True, adds indicator and geo unit labels to the data. Default is False.
        geoUnitType: The type of geography to request data for. Allowed values are NATIONAL and REGIONAL. If geoUnit is provided, this parameter is ignored. Default is both national and regional data
        footnotes: If True, includes footnotes in the response. Default is False.
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A pandas DataFrame with the data or a list of dictionaries if raw=True.
    """

    # Convert the indicators and geo_units to their respective codes
    if indicator:
        indicator = _convert_indicator_codes_to_code(indicator)
    if geoUnit:
        geoUnit = _convert_geo_units_to_code(geoUnit)

    # get the data from the API. If both indicator and geo_unit are None, the api module will raise an error
    try:
        response = api.get_data(
            indicator=indicator,
            geoUnit=geoUnit,
            start=start,
            end=end,
            footnotes=footnotes,
            geoUnitType=geoUnitType,
            version=version,
        )
    except TooManyRecordsError:
        raise TooManyRecordsError(
            "Too much data requested. Please make multiple requests with fewer parameters. A maximum of 1000 records can be requested at a time."
        )

    # log hints if any
    _log_hints(response)

    # extract the data from the response
    data = response["records"]

    # if no data is found, raise an error
    if len(data) == 0:
        raise NoDataError("No data found for the given parameters")

    # Add labels if requested
    if labels:
        data = _add_indicator_labels(data)
        data = _add_geo_unit_labels(data)

    # Return the raw data if raw=True in the original format from the API
    if raw:
        return data

    # Normalize the footnotes if requested
    if footnotes:
        data = _normalize_footnotes(data)

    return pd.DataFrame(data)


def get_metadata(
    indicator: str | list[str] | None = None,
    disaggregations: bool = False,
    glossaryTerms: bool = False,
    *,
    version: str | None = None,
) -> list[dict]:
    """Get the metadata for indicators

    Get the metadata for the given indicators. If no indicator is provided, metadata for all indicators is returned.
    Optionally include disaggregations and glossary terms in the response.

    Args:
        indicator: The indicator code or name to get metadata for. If None, metadata for all indicators is returned. Default is None which returns metadata for all indicators. To see all available indicators, use the `available_indicators` function.
        disaggregations: Include disaggregations in the response. Default is False.
        glossaryTerms: Include glossary terms in the response. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A list of dictionaries with the metadata for the indicators
    """

    if isinstance(indicator, str):
        indicator = [indicator]

    # Convert the indicators to their respective codes
    response = api.get_indicators(
        disaggregations=disaggregations, glossaryTerms=glossaryTerms, version=version
    )

    # Filter the indicators based on the given indicator codes
    if indicator:
        indicator = _convert_indicator_codes_to_code(indicator)
        response = [
            record for record in response if record["indicatorCode"] in indicator
        ]

        # check if no data is found
        if len(response) == 0:
            raise NoDataError("No indicator metadata found for the given indicators")

        # log message if indicators are not found, specifying which indicators were not found
        if len(indicator) != len(response):

            # get the set of indicators not found
            not_found = set(indicator) - {
                record["indicatorCode"] for record in response
            }

            logger.warning(
                f"Metadata not found for the following indicators: {list(not_found)}"
            )

    return response


def _indicators_df(indicators: list[dict]) -> pd.DataFrame:
    """Return available indicators as a DataFrame. This function flattens the data for easy DataFrame conversion then returns the DataFrame.

    Args:
        indicators: The list of indicators to convert to a DataFrame

    Returns:
        A pandas DataFrame with the available indicators
    """

    # Flatten the data for DataFrame return
    for record in indicators:
        record["min"] = record["dataAvailability"]["timeLine"]["min"]
        record["max"] = record["dataAvailability"]["timeLine"]["max"]
        record["totalRecordCount"] = record["dataAvailability"]["totalRecordCount"]
        geo_units = record["dataAvailability"]["geoUnits"]["types"]

        # Handle geo_unit_type based on the conditions
        if "REGIONAL" in geo_units and "NATIONAL" in geo_units:
            record["geoUnitType"] = "ALL"
        else:
            record["geoUnitType"] = geo_units[0] if geo_units else None

        # Remove the 'dataAvailability' key since it's been flattened
        record.pop("dataAvailability")

    # Convert to pandas DataFrame and return
    return pd.DataFrame(indicators).assign(
        last_data_update=lambda d: pd.to_datetime(d.lastDataUpdate)
    )


def available_indicators(
    theme: str | list[str] | None = None,
    minStart: int | None = None,
    geoUnitType: GeoUnitType | Literal["ALL"] | None = None,
    *,
    raw: bool = False,
    version: str | None = None,
) -> pd.DataFrame | list[dict]:
    """Get available indicators

    This functions returns the available indicators from the UIS API with some basic information, including theme,
    time range, last data update, and total records. The data is filtered based on the given parameters.

    Args:
        theme: Filter indicators for specific themes. Can be a single theme or a list of themes. Default returns all themes. Use the `available_themes` function to see all available themes.
        minStart: The earliest start year for the indicator data. Includes the start year itself. Default is None, which returns all available data.
        geoUnitType: The type of geography for which data is available. Default is None which does not filter and gets any available type. Allowed values are "NATIONAL" (country-level data), "REGIONAL" (regional-level data), "ALL" (both national and regional data), or None for all types.
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A pandas DataFrame with the available indicators or a list of dictionaries if raw=True.
    """

    # Get the indicators from the API
    indicators = api.get_indicators(version=version)

    if isinstance(theme, str):
        theme = [theme]

    # filtered based on theme
    if theme:
        # make sure themes are capitalised
        theme = [t.upper() for t in theme]

        # filter the indicators based on the theme
        indicators = [record for record in indicators if record["theme"] in theme]

        # if some themes are not found log a message with the themes not found
        if (
            len(theme) != len({record["theme"] for record in indicators})
            and len(indicators) > 0
        ):
            not_found = set(theme) - {record["theme"] for record in indicators}
            logger.warning(
                f"Indicators not found for the following themes: {list(not_found)}"
            )

    # Filter based on min_year
    if minStart:
        indicators = [
            record
            for record in indicators
            if record["dataAvailability"]["timeLine"]["min"] <= minStart
        ]

    # Filter based on geo_unit_type
    if geoUnitType:
        if geoUnitType == "ALL":
            # Filter records with both 'REGIONAL' and 'NATIONAL'
            indicators = [
                record
                for record in indicators
                if "REGIONAL" in record["dataAvailability"]["geoUnits"]["types"]
                and "NATIONAL" in record["dataAvailability"]["geoUnits"]["types"]
            ]
        elif geoUnitType in ["REGIONAL", "NATIONAL"]:
            # Filter records with either 'REGIONAL' or 'NATIONAL'
            indicators = [
                record
                for record in indicators
                if geoUnitType in record["dataAvailability"]["geoUnits"]["types"]
            ]
        else:
            raise ValueError(
                "geo_unit_type must be NATIONAL, REGIONAL, ALL, or None for any type. By default if the geo_unit_type is not specified or is None, it returns any available type."
            )

    # If no data is found, raise an error
    if len(indicators) == 0:
        raise NoDataError("No indicators found for the given parameters")

    # If raw=True, return the list of dictionaries directly
    if raw:
        return indicators

    # Convert to pandas DataFrame and return
    return _indicators_df(indicators)


def available_geo_units(
    geoUnitType: GeoUnitType | None = None,
    *,
    raw: bool = False,
    version: str | None = None,
) -> pd.DataFrame | list[dict]:
    """Get available geo units

    Get all available geo units for a given API data version (or the current default version if no explicit version is provided), along with some basic information like the region group and type of geography.

    Args:
        geoUnitType: The type of geography to request data for. Allowed values are NATIONAL and REGIONAL. Default is None which returns all available types.
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A pandas DataFrame with the available geo units or a list of dictionaries if raw=True.

    """

    geo_units = api.get_geo_units(version=version)

    if geoUnitType:
        # filter the geo_units based on the geo_unit_type
        if geoUnitType not in ["NATIONAL", "REGIONAL"]:
            raise ValueError("geo_unit_type must be either NATIONAL or REGIONAL")
        geo_units = [record for record in geo_units if geoUnitType in record["type"]]

    if raw:
        return geo_units

    return pd.DataFrame(geo_units)


def available_themes(*, raw: bool = False) -> pd.DataFrame | dict:
    """Get the available themes and basic information including latest update and description

    Args:
        raw: If True, returns the data as a dictionary in the original format from the API. Default is False.
    """

    themes = api.get_default_version()["themeDataStatus"]

    if raw:
        return themes

    return pd.DataFrame(themes).assign(
        lastUpdate=lambda d: pd.to_datetime(d.lastUpdate)
    )


def default_version() -> str:
    """Get the default data version"""

    return api.get_default_version()["version"]


def available_versions(*, raw: bool = False) -> pd.DataFrame | list[dict]:
    """Get available data versions and basic information including publication date and description

    Args:
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.

    Returns:
        A pandas DataFrame with the available versions or a list of dictionaries if raw=True.
    """

    versions = api.get_versions()

    # remove theme details
    for version in versions:
        version.pop("themeDataStatus")

    if raw:
        return versions

    return pd.DataFrame(versions).assign(
        publicationDate=lambda d: pd.to_datetime(d.publicationDate)
    )
