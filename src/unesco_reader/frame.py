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


def get_data(indicator: str | list[str] = None,
             geo_unit: str | list[str] = None,
             start: int = None,
             end: int = None,
             indicator_metadata: bool = False,
             geo_unit_type: str = None,
             version: str = None,
             footnotes: bool = False,
             raw: bool = False,
             ) -> pd.DataFrame:
    """Get UIS data"""

    response = api.get_data(indicator=indicator,
                            geo_unit=geo_unit,
                            start=start,
                            end=end,
                            indicator_metadata=indicator_metadata,
                            footnotes=footnotes,
                            geo_unit_type=geo_unit_type,
                            version=version)

    data = response['records']

    # if no data is found, raise an error
    if len(data) == 0:
        raise ValueError("No data found for the given parameters")

    if footnotes:
        data = _normalize_footnotes(data)

    # if raw data is requested, return the data in original format
    if raw:
        return data

    return pd.DataFrame(data)


def indicator_metadata(indicator: str):
    pass


def available_indicators(theme: str = None, raw=False):
    """ """

    indicators = api.get_indicators()


def indicator_info(indicator: str):
    pass


def available_geo_units(raw=False):
    pass
