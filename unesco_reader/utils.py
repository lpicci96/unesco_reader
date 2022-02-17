"""
Utility functions
=================
Includes functions to extract data from a zipped csv without a local download
"""


import requests
import pandas as pd
import io
from zipfile import ZipFile


def read_zip(url:str, file_name:str) -> pd.DataFrame:
    """
    Reads a csv from the web contained in a zip folder
    
    Parameters
    ----------
    url : str
        Zip folder url
    file_name: str
        CSV file name written as 'file_name.csv'
        
    Returns
    -------
    pandas dataframe object
    """
    
    try:
        response = requests.get(url)
        file = ZipFile(io.BytesIO(response.content))
        if file_name not in list(file.NameToInfo.keys()):
            raise ValueError(f'{file_name} is not found in the zipped folder')
        df = pd.read_csv(file.open(file_name), low_memory=False)
        
        return df
    
    except ConnectionError:
        raise ConnectionError('Could not read file')
        
        
        