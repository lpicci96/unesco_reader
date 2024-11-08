"""Pandas support for UNESCO data.


TODO: implement basic multithreading for faster data retrieval


"""

import pandas as pd
from typing import Literal

from unesco_reader import api
from unesco_reader.config import NoDataError, logger, GEO_UNIT_TYPE


def _log_hints(response: dict) -> None:
    """If there are any hints in the response, log them

    If a response from the api contains hints, it means there are some issues with the request or the data.
    This function logs the hints as warnings. There may be multiple hints, so they are logged one by one.

    Args:
        response: The response from the API
    """

    if "hints" in response and len(response['hints']) > 0:
        for hint in response['hints']:
            logger.warning(hint['message'])


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

    # Create lookup dictionaries for quick access by code or name
    code_lookup = {unit['indicatorCode'] for unit in indicator_data}
    name_to_code = {unit['name']: unit['indicatorCode'] for unit in indicator_data}

    # Ensure indicators is a list for uniform processing
    is_single = isinstance(indicators, str)
    indicators = [indicators] if is_single else indicators

    converted_indicators = []
    for indicator in indicators:
        # Check if the indicator is already a code
        if indicator in code_lookup:
            converted_indicators.append(indicator)
        # Check if the indicator is a name and convert to code
        elif indicator in name_to_code:
            converted_indicators.append(name_to_code[indicator])
        # else return the original indicator as a fallback
        else:
            converted_indicators.append(indicator)  # Append the original indicator as a fallback

    # Return a string if a single indicator was provided, otherwise return a list
    return converted_indicators[0] if is_single else converted_indicators


def _convert_geo_units_to_code(geo_units: str | list[str]) -> str | list[str]:
    """Convert geo units to their respective codes

    This function converts the geo unit names to their respective codes. If the geo unit is already a code, it is left as is.
    If the geo unit is not found, it is left as is and will be handled as an error by the API.

    Args:
        geo_units: The geo unit name or list of geo unit names to convert to codes
    """

    geo_units_data = api.get_geo_units() # Fetch the geo unit data

    # Create lookup dictionaries for quick access by code or name
    code_lookup = {unit['id'] for unit in geo_units_data}
    name_to_code = {unit['name']: unit['id'] for unit in geo_units_data}

    # Ensure geo_units is a list for uniform processing, and keep track if it was a single value
    is_single = isinstance(geo_units, str)
    geo_units = [geo_units] if is_single else geo_units

    # loop over the geo_units and convert them to codes
    converted_geo_units = []
    for geo_unit in geo_units:
        # Check if the geo_unit is already a code
        if geo_unit in code_lookup:
            converted_geo_units.append(geo_unit)
        # Check if the geo_unit is a name and convert to code
        elif geo_unit in name_to_code:
            converted_geo_units.append(name_to_code[geo_unit])
        # else return the original geo_unit as a fallback
        else:
            converted_geo_units.append(geo_unit)

    return converted_geo_units[0] if is_single else converted_geo_units


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
        if len(record['footnotes']) == 0:
            record['footnotes'] = None
            continue
        footnotes_str = [f"{footnote['type']}, {footnote['subtype']}: {footnote['value']}"
                         for footnote in record['footnotes']]
        record['footnotes'] = ' ; '.join(footnotes_str)

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
    indicator_map = {indicator['indicatorCode']: indicator['name'] for indicator in indicators}

    # Loop over the data and add the indicator name using the map for fast lookup
    for record in data:
        record['name'] = indicator_map.get(record['indicatorId'], None)

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
    geo_unit_map = {geo_unit['id']: geo_unit['name'] for geo_unit in geo_units}
    region_group_map = {geo_unit['id']: geo_unit['regionGroup'] if geo_unit['type'] == 'REGIONAL' else None for geo_unit in geo_units}

    # Loop over the data and add the geo unit name using the map for fast lookup
    for record in data:
        record['geoUnitName'] = geo_unit_map.get(record['geoUnit'], None)
        record['regionGroup'] = region_group_map.get(record['geoUnit'], None)

    return data



def get_data(indicator: str | list[str] | None = None,
             geo_unit: str | list[str] | None = None,
             start: int | None = None,
             end: int | None = None,
             labels: bool=False,
             geo_unit_type: GEO_UNIT_TYPE | None = None,
             footnotes: bool = False,
             *,
             raw: bool = False,
             version: str | None = None
             ) -> pd.DataFrame | list[dict]:
    """Get UIS data

    Query the UIS API for data based on the given parameters. At least one indicator or one geo_unit must be provided. If only indicators are provided, data for all geographies is returned, and vice versa. To see available indicators or geographies, use the `available_indicators` or `available_geo_units` functions respectively. If both a geo_unit and geo_unit_type are provided, the geo_unit_type is ignored.

    Args:
        indicator: The indicator code or name to request data for. If None, data for all indicators is returned. By default, None. To see all available indicators, use the `available_indicators` function. A future version of this function will use regex to match indicator names.
        geo_unit: The geo unit code or name to request data for. If None, data for all geo units is returned. By default, None. To see all available geo units, use the `available_geo_units` function. A future version of this function will use regex to match geo unit names.
        start: The start year to request data for. Includes the year itself. Default is None, which returns the earliest available year.
        end: The end year to request data for. Includes the year itself. Default is None, which returns the latest available year.
        labels: If True, adds indicator and geo unit labels to the data. Default is False.
        geo_unit_type: The type of geography to request data for. Allowed values are NATIONAL and REGIONAL. If a geo_unit is provided, this parameter is ignored. Default is both national and regional data
        footnotes: If True, includes footnotes in the response. Default is False.
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A pandas DataFrame with the data or a list of dictionaries if raw=True.
    """

    # Convert the indicators and geo_units to their respective codes
    if indicator:
        indicator = _convert_indicator_codes_to_code(indicator)
    if geo_unit:
        geo_unit = _convert_geo_units_to_code(geo_unit)

    # get the data from the API. If both indicator and geo_unit are None, the api module will raise an error
    response = api.get_data(indicator=indicator,
                            geo_unit=geo_unit,
                            start=start,
                            end=end,
                            footnotes=footnotes,
                            geo_unit_type=geo_unit_type,
                            version=version)


    # log hints if any
    _log_hints(response)

    # extract the data from the response
    data = response['records']

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

    return (pd.DataFrame(data)
            .rename(columns={'indicatorId': 'indicator_code',
                             "geoUnit": "geo_unit",
                             "name": "indicator_name",
                             "geoUnitName": "geo_unit_name",
                                "regionGroup": "region_group",
                             })
            )


def get_metadata(indicator: str | list[str] | None = None,
                 disaggregations: bool = False,
                 glossary_terms: bool = False,*, version: str | None = None) -> list[dict]:
    """Get the metadata for indicators

    Get the metadata for the given indicators. If no indicator is provided, metadata for all indicators is returned.
    Optionally include disaggregations and glossary terms in the response.

    Args:
        indicator: The indicator code or name to get metadata for. If None, metadata for all indicators is returned. Default is None which returns metadata for all indicators. To see all available indicators, use the `available_indicators` function. In a future version, this function will use regex to match indicator names.
        disaggregations: Include disaggregations in the response. Default is False.
        glossary_terms: Include glossary terms in the response. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A list of dictionaries with the metadata for the indicators
    """

    # Convert the indicators to their respective codes
    if indicator:
        indicator = _convert_indicator_codes_to_code(indicator)

    indicators = api.get_indicators(disaggregations=disaggregations, glossary_terms=glossary_terms, version=version)

    # Filter the indicators based on the given indicator codes
    if indicator:
        indicators = [record for record in indicators if record['indicatorCode'] in indicator]

        # check if no data is found
        if len(indicators) == 0:
            raise NoDataError("No indicator metadata found for the given indicators")

    return indicators



def available_indicators(theme: str | list[str] | None = None, min_year: int | None = None, geo_unit_type: GEO_UNIT_TYPE | Literal['ALL'] = "ALL",*, raw: bool=False, version: str | None = None) -> pd.DataFrame | list[dict]:
    """Get available indicators

    This functions returns the available indicators from the UIS API with some basic information, including theme,
    time range, last data update, and total records. The data is filtered based on the given parameters.

    Args:
        theme: Filter indicators for specific themes. Can be a single theme or a list of themes. Default returns all themes.
        min_year: The earliest year for which the indicator data must be available. Includes the year itself. Default is None, which returns all available data.
        geo_unit_type: The type of geography for which data is available. Default is "ALL" which gets all available types. Allowed values are ["NATIONAL", "REGIONAL", "ALL"].
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A pandas DataFrame with the available indicators or a list of dictionaries if raw=True.
    """

    indicators = api.get_indicators(version=version)

    if isinstance(theme, str):
        theme = [theme]

    # filtered based on theme
    if theme:
        indicators = [record for record in indicators if record['theme'] in theme]

    # Filter based on min_year
    if min_year:
        indicators = [record for record in indicators if record['dataAvailability']['timeLine']['min'] <= min_year]

    # Filter based on geo_unit_type
    if geo_unit_type == "ALL":
            # Filter records with both 'REGIONAL' and 'NATIONAL'
        indicators = [record for record in indicators if "REGIONAL" in record['dataAvailability']['geoUnits']['types'] and "NATIONAL" in record['dataAvailability']['geoUnits']['types']]
    elif geo_unit_type in ["REGIONAL", "NATIONAL"]:
            # Filter records with either 'REGIONAL' or 'NATIONAL'
        indicators = [record for record in indicators if geo_unit_type in record['dataAvailability']['geoUnits']['types']]
    else:
        raise ValueError("geo_unit_type must be 'NATIONAL', 'REGIONAL', or 'ALL'")

    # If no data is found, raise an error
    if len(indicators) == 0:
        raise NoDataError("No indicators found for the given parameters")

    # If raw=True, return the list of dictionaries directly
    if raw:
        return indicators

    # Flatten the data for DataFrame return
    for record in indicators:
        record['min_year'] = record['dataAvailability']['timeLine']['min']
        record['max_year'] = record['dataAvailability']['timeLine']['max']
        record['total_records'] = record['dataAvailability']['totalRecordCount']
        geo_units = record['dataAvailability']['geoUnits']['types']

        # Handle geo_unit_type based on the conditions
        if "REGIONAL" in geo_units and "NATIONAL" in geo_units:
            record['geo_unit_type'] = "ALL"
        else:
            record['geo_unit_type'] = geo_units[0] if geo_units else None

        # Remove the 'dataAvailability' key since it's been flattened
        record.pop('dataAvailability')

    # Convert to pandas DataFrame and return
    return (pd.DataFrame(indicators)
            .rename(columns={'indicatorCode': 'indicator_code',
                             "name": "indicator_name",
                             "lastDataUpdate": "last_data_update",
                             "lastDataUpdateDescription": "last_data_update_description",
                             })
            )

def available_geo_units(geo_unit_type = None, raw: bool = False, version: str | None = None) -> pd.DataFrame | list[dict]:
    """ """

    geo_units = api.get_geo_units(version=version)

    if geo_unit_type:
        geo_units = [record for record in geo_units if geo_unit_type in record['type']]

    if raw:
        return geo_units

    return pd.DataFrame(geo_units).rename(columns={"id": "geo_unit_code",
                                                   'name': 'geo_unit_name',
                                                   "regionGroup": "region_group",
                                                   "type": "geo_unit_type",})

def available_themes(raw: bool = False) -> pd.DataFrame | dict:
    """get the available themes for the latest data version or a specific version"""

    themes = api.get_default_version()['themeDataStatus']

    if raw:
        return themes

    return pd.DataFrame(themes).rename(columns={"lastUpdate": "last_update",})


def default_version() -> str:
    """Get the default data version"""

    return api.get_default_version()['version']


