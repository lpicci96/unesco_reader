"""UNESCO Institute of Statistics (UIS) data reader."""

import requests
import io
from zipfile import ZipFile
import pandas as pd

DATASETS = {'SDG': "SDG Global and Thematic Indicators",
            'OPRI': "Other Policy Relevant Indicators (OPRI)"}

BASE_URL = "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/"


def unzip_folder(url: str) -> ZipFile:
    """Unzip a folder from a url."""

    try:
        response = requests.get(url)
        folder = ZipFile(io.BytesIO(response.content))
        return folder

    except ConnectionError:
        raise ConnectionError(f"Could not read file from url: {url}")


def read_csv(folder: ZipFile, path: str) -> pd.DataFrame:
    """Read a csv file from a folder."""

    if path not in folder.namelist():
        raise FileNotFoundError(f"Could not find file: {path}")

    return pd.read_csv(folder.open(path), low_memory=False)


def available_datasets() -> pd.DataFrame:
    """Return a dataframe with available datasets, and relevant information"""

    return (pd.DataFrame({'code': DATASETS.keys(), 'name': DATASETS.values()})
            .assign(link = lambda df: df.code.apply(lambda x: f"{BASE_URL}{x}.zip")))


def read_dataset(code: str) -> pd.DataFrame:
    """Read a dataset from the UIS website"""

    if code not in DATASETS.keys():
        raise ValueError(f"Dataset code not found: {code}")

    url = f"{BASE_URL}{code}.zip"
    folder = unzip_folder(url)

    return read_csv(folder, f"{code}_DATA_NATIONAL.csv")


def mapping_dict(df: pd.DataFrame, key_col: str = 'left') -> dict:
    """Create a mapping dictionary from a dataframe

    Args:
        df: dataframe with two columns, left and right
        key_col: column to use as keys in the dictionary. Choose from 'left' or 'right'. Default is 'left'

    Returns:
        A dictionary with the values from the left column as keys,
        and the values from the right column as values
    """

    if len(df.columns) != 2:
        raise ValueError('df can only contain 2 columns')
    if key_col not in ['left', 'right']:
        raise ValueError('Invalid key_col. Please choose from ["left", "right"]')

    if key_col == 'left':
        k, v= 0, 1
    else:
        k, v = 1, 0
    return (df
            .set_index(df.iloc[:, k])
            .iloc[:, v]
            .to_dict()
            )


