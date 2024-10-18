"""Pandas support for UNESCO data."""

import pandas as pd

from unesco_reader import api


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
    """Add indicator labels to the data"""

    # Get indicators and create a dictionary mapping indicatorCode to indicator details
    indicators = api.get_indicators()
    indicator_map = {indicator['indicatorCode']: indicator['name'] for indicator in indicators}

    # Loop over the data and add the indicator name using the map for fast lookup
    for record in data:
        record['name'] = indicator_map.get(record['indicatorId'], None)

    return data

def _add_geo_unit_labels(data: list[dict]) -> list[dict]:
    """Add geo unit labels to the data. For regions, add both the region name and the region group"""

    # Get geo units and create a dictionary mapping geoUnit to geoUnit details
    geo_units = api.get_geo_units()
    geo_unit_map = {geo_unit['id']: geo_unit['name'] for geo_unit in geo_units}
    region_group_map = {geo_unit['id']: geo_unit['regionGroup'] if geo_unit['type'] == 'REGIONAL' else None for geo_unit in geo_units}

    # Loop over the data and add the geo unit name using the map for fast lookup
    for record in data:
        record['geoUnitName'] = geo_unit_map.get(record['geoUnit'], None)
        record['regionGroup'] = region_group_map.get(record['geoUnit'], None)

    return data



def get_data(indicator: str | list[str] = None,
             geo_unit: str | list[str] = None,
             start: int = None,
             end: int = None,
             geo_unit_type: str = None,
             version: str = None,
             footnotes: bool = False,
             raw: bool = False,
             labels: bool=False
             ) -> pd.DataFrame:
    """Get UIS data

    Query the UIS API for data based on the given parameters.
    At least an indicator or a geo_unit must be provided. If both are provided, the data is filtered by both.
    If only indicators are provided, data for all geographies is returned, and vice versa. To see available indicators
    or geographies, use the `available_indicators` or `available_geo_units` functions.
    """

    response = api.get_data(indicator=indicator,
                            geo_unit=geo_unit,
                            start=start,
                            end=end,
                            footnotes=footnotes,
                            geo_unit_type=geo_unit_type,
                            version=version)

    data = response['records']

    # if no data is found, raise an error
    if len(data) == 0:
        raise ValueError("No data found for the given parameters")

    if labels:
        data = _add_indicator_labels(data)
        data = _add_geo_unit_labels(data)

    # Return the raw data if raw=True in the original format from the API
    if raw:
        return data

    if footnotes:
        data = _normalize_footnotes(data)

    return pd.DataFrame(data).rename(columns={'indicatorId': 'indicator_code', "geoUnit": "geo_unit", "name": "indicator_name"})


def indicator_metadata(indicator: str, disaggregations: bool = False, glossary_terms: bool = False, version: str | None = None):
    """Get the metadata for a specific indicator"""

    indicators = api.get_indicators(disaggregations=disaggregations, glossary_terms=glossary_terms, version=version)

    # try find the specific indicator, could be either the code or the name. If not found, raise an error
    indicator_data = next((record for record in indicators if record['indicatorCode'] == indicator or record['name'] == indicator), None)
    if indicator_data is None:
        raise ValueError(f"Indicator {indicator} not found")

    return indicator_data


def available_indicators(theme: str | list[str] = None, min_year: int = None, geo_unit_type = None, raw=False, version: str = None) -> pd.DataFrame | list[dict]:
    """Get available indicators

    This functions returns the available indicators from the UIS API with some basic information, including theme,
    time range, last data update, and total records. The data is filtered based on the given parameters.

    Args:
        theme: Filter indicators for specific themes. Can be a single theme or a list of themes. Default returns all themes.
        min_year: The minimum year for which data is available. Default does not filter for minimum year.
        geo_unit_type: The type of geography for which data is available. Default is "ALL". Allowed values are ["NATIONAL", "REGIONAL", "ALL"]. ALL returns records with both "NATIONAL" and "REGIONAL" data.
        raw: If True, returns the data as a list of dictionaries in the original format from the API. Default is False.
        version: The data version to use. Default uses the latest default version.

    Returns:
        A pandas DataFrame with the available indicators or a list of dictionaries if raw=True.
    """

    indicators = api.get_indicators(version=version)

    if isinstance(theme, str):
        theme = [theme]

    # filtered_data = indicators
    if theme:
        indicators = [record for record in indicators if record['theme'] in theme]
    if min_year:
        indicators = [record for record in indicators if record['dataAvailability']['timeLine']['min'] <= min_year]

    # Filter by geo_unit_type
    if geo_unit_type:
        if geo_unit_type == "ALL":
            # Filter records with both 'REGIONAL' and 'NATIONAL'
            indicators = [record for record in indicators if "REGIONAL" in record['dataAvailability']['geoUnits']['types'] and "NATIONAL" in record['dataAvailability']['geoUnits']['types']]
        elif geo_unit_type in ["REGIONAL", "NATIONAL"]:
            # Filter records with either 'REGIONAL' or 'NATIONAL'
            indicators = [record for record in indicators if geo_unit_type in record['dataAvailability']['geoUnits']['types']]


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


