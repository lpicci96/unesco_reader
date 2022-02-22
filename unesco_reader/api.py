"""
Functions to query UNESCO
=========================

Functions query data from the UNESCO Institute of Statistics Bulk download services
here: https://apiportal.uis.unesco.org/bdds
"""


import pandas as pd
from typing import Optional
from unesco_reader.utils import read_zip


def datasets():
    """
    Metadata for available UNESCO Institute of Statistics datasets

    Returns
    -------
    pd.DataFrame

    """

    dataset_dict = {
        "dataset": [
            "SDG Global and Thematic Indicators",
            "Other Policy Relevant Indicators (OPRI)",
            "Research and Development (R&D)",
            "Innovation",
            "Cultural Employment",
            "Feature Films",
            "Cultural Trade",
            "SDG 11",
            "Demographic and Socio-economic Indicators",
        ],
        "code": ["SDG", "OPRI", "SCI", "INNO", "CLTE", "FILM", "CLTT", "SDG11", "DEM"],
        "category": [
            "Education",
            "Education",
            "Science",
            "Science",
            "Culture",
            "Culture",
            "Culture",
            "Culture",
            "External",
        ],
        "link": [
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/SDG.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/OPRI.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/SCI.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/INNO.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/CLTE.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/FILM.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/CLTT.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/SDG11.zip",
            "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/DEM.zip",
        ],
        "regional": [True, True, True, False, False, False, False, False, False],
    }

    return pd.DataFrame(dataset_dict)


def indicators(dataset_code: str) -> pd.DataFrame:
    """
    Metadata for available indicators in a UNESCO Institute of Statistics dataset

    Parameters
    ----------
    dataset_code : str
        Specify the UIS dataset code

    Returns
    -------
    pd.DataFrame
    """
    ds = datasets()
    if dataset_code not in list(ds.code):
        raise ValueError(f"{dataset_code} is not a valid code.")
    url = ds.loc[ds.code == dataset_code, "link"].values[0]
    df = read_zip(url, file_name=f"{dataset_code}_LABEL.csv")

    return df


def get_bulk(dataset_code: str, grouping: Optional[str] = "NATIONAL") -> pd.DataFrame:
    """
    Download data for all available indicators in a UNESCO Institute of Statistics dataset

    Parameters
    ----------
    dataset_code : str
        Specify the UNESCO dataset code
    grouping : str
        Specify the geography grouping option
        [NATIONAL] for country level grouping
        [REGIONAL] for region level grouping.
        The default is [NATIONAL].

    Returns
    -------
    pd.DataFrame
    """

    ds = datasets()

    # parameter error handling
    if dataset_code not in list(ds.code):
        raise ValueError(f"{dataset_code} is not a valid code.")
    if grouping not in ["NATIONAL", "REGIONAL"]:
        raise ValueError(f"{grouping} is not a valid grouping.")

    # if grouping is REGIONAL, check if it is available
    if (grouping == "REGIONAL") & (
        dataset_code not in list(ds.loc[ds.regional, "code"])
    ):
        raise ValueError(f"{dataset_code} does not have a REGIONAL option.")

    url = ds.loc[ds.code == dataset_code, "link"].values[0]
    df = read_zip(url, file_name=f"{dataset_code}_DATA_{grouping}.csv")

    return df


def get_indicator(
    indicator_code: str, dataset_code: str, grouping: Optional[str] = "NATIONAL"
) -> pd.DataFrame:
    """
    Download data for a specific UIS indicator

    Parameters
    ----------
    indicator_code : str
        Specify the UNESCO indicator code.
    dataset_code : str
        Specify the UNESCO dataset code .
    grouping : str
        Specify the geography grouping option
        [NATIONAL] for country level grouping
        [REGIONAL] for region level grouping.
        The default is [NATIONAL].

    Returns
    -------
    pd.DataFrame.

    """

    bulk = get_bulk(dataset_code, grouping)
    df = bulk[bulk["INDICATOR_ID"] == indicator_code].reset_index(drop=True)

    # error handling if no data is returned
    if len(df) == 0:
        raise ValueError(f"No data available for {indicator_code}")

    return df
