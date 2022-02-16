# -*- coding: utf-8 -*-
"""


This script extracts data from the UNESCO Bulk download services here: https://apiportal.uis.unesco.org/bdds


"""


import pandas as pd
from typing import Optional
from unesco.utils import read_zip


def datasets():
    """
    Metadata for available UNESCO datasets
    
    Returns
    -------
    pd.DataFrame
    """
    
    return pd.read_csv('datasets.csv')
    

def indicators(dataset_code: str) -> pd.DataFrame:
    """
    Metadata for available indecators in a UNESCO dataset

    Parameters
    ----------
    dataset_code : str
        Specify the UNESCO dataset code 

    Returns
    -------
    pd.DataFrame
    """
    ds = datasets()
    if dataset_code not in list(ds.code):
        raise ValueError(f"{dataset_code} is not a valid code. Available datasets are {list(ds['code'])}")
    url = ds.loc[ds.code == dataset_code, 'link'].values[0]
    df = read_zip(url, file_name = f'{dataset_code}_LABEL.csv')
    
    return df


def get_bulk(dataset_code:str, grouping: Optional[str] = 'NATIONAL') -> pd.DataFrame:
    """
    Download data for all available indicators in a UNESCO dataset

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
    
    #parameter error handling
    if dataset_code not in list(ds.code):
        raise ValueError(f'{dataset_code} is not a valid code')
    if grouping not in ['NATIONAL', 'REGIONAL']:
        raise ValueError(f'{grouping} is not a valid grouping')
        
    url = ds.loc[ds.code == dataset_code, 'link'].values[0]
    df = read_zip(url, file_name=f'{dataset_code}_DATA_{grouping}.csv')
    
    return df


def get_indicator(indicator_code: str, dataset_code: str, grouping: Optional[str] = 'NATIONAL') -> pd.DataFrame:
    """
    Download data for a specific UNESCO indicator
    
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
    df = bulk[bulk['INDICATOR_ID'] == indicator_code].reset_index(drop=True)
    
    #error handling if no data is returned
    if len(df) == 0:
        raise ValueError(f'No data available for {indicator_code}')
        
    return df




















    
    