"""Common functions and objects for the unesco_reader package."""

import requests
import io
from zipfile import ZipFile
import pandas as pd


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
        k, v = 0, 1
    else:
        k, v = 1, 0
    return (df
            .set_index(df.iloc[:, k])
            .iloc[:, v]
            .to_dict()
            )


def unzip_folder(url: str) -> ZipFile:
    """unzip a folder from a url."""

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ZipFile(io.BytesIO(response.content))
        else:
            raise ConnectionError(f"Could not read file from url: {url}")

    except ConnectionError:
        raise ConnectionError(f"Could not read file from url: {url}")


def read_csv(folder: ZipFile, path: str) -> pd.DataFrame:
    """Read a csv file from a folder."""

    if path not in folder.namelist():
        raise FileNotFoundError(f"Could not find file: {path}")

    return pd.read_csv(folder.open(path), low_memory=False)





