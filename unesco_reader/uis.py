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





