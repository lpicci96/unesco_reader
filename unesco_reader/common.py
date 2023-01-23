"""Common functions and objects for the unesco_reader package."""

import requests
import io
from zipfile import ZipFile, BadZipFile
import pandas as pd
from typing import Union


def mapping_dict(df: pd.DataFrame, key_col: str = "left") -> dict:
    """Create a mapping dictionary from a dataframe with 2 columns

    Args:
        df: dataframe with two columns, left and right
        key_col: column to use as keys in the dictionary. Choose from 'left' or 'right'. Default is 'left'

    Returns:
        A dictionary with the values from the left column as keys,
        and the values from the right column as values
    """

    if len(df.columns) != 2:
        raise ValueError("df can only contain 2 columns")
    if key_col not in ["left", "right"]:
        raise ValueError('Invalid key_col. Please choose from ["left", "right"]')

    if key_col == "left":
        k, v = 0, 1
    else:
        k, v = 1, 0
    return df.set_index(df.iloc[:, k]).iloc[:, v].to_dict()


def make_request(url: str) -> requests.models.Response:
    """Make a request to a url.

    Args:
        url: url to make request to

    Returns:
        requests.models.Response: response object
    """

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Could not connect to {url}")

        if not response.headers["content-type"] == "application/x-zip-compressed":
            raise ValueError("The file is not a zip file")

        return response

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not read file from url: {url}. Error : {str(e)}")


def unzip(file: Union[str, io.BytesIO]) -> ZipFile:
    """Unzip a file

    Create a ZipFile object from a file on disk or a file-like object from a requests
    response.

    Args:
        file: path to zipfile or file-like object. If zipfile is extracted from a url,
        the file like object can be obtained by calling `io.BytesIO(response.content)`

    Returns:
        ZipFile: object containing unzipped folder
    """

    try:
        return ZipFile(file)
    except BadZipFile as e:
        raise ValueError(f"The file could not be unzipped. Error : {str(e)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find file: {file}")


def read_csv(folder: ZipFile, path: str) -> pd.DataFrame:
    """Read a CSV file from a ZipFile object.

    Args:
        folder: ZipFile object containing the CSV file
        path: path to the CVS in the zipped folder

    Returns:
        pd.DataFrame: dataframe containing the data from the CSV
    """

    if path not in folder.namelist():
        raise FileNotFoundError(f"Could not find file: {path}")

    return pd.read_csv(folder.open(path), low_memory=False)
