"""
Utility functions
=================
Includes functions to extract data from a zipped csv without a local download
"""

import pandas as pd
import io
from zipfile import ZipFile
import requests


def get_zip_from_web(url: str) -> ZipFile:
    """ """
    print(url)
    try:
        response = requests.get(url)
        folder = ZipFile(io.BytesIO(response.content))
        return folder

    except ConnectionError:
        raise ConnectionError('Could not retrieve zip file')


def read_zip(folder: ZipFile, path: str) -> pd.DataFrame:
    """ """

    if path not in list(folder.NameToInfo.keys()):
        raise ValueError(f'Invalid path: {path}')

    return pd.read_csv(folder.open(path), low_memory=False)

