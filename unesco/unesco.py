# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 16:34:11 2022

@author: lpicc


This script extracts data from the UNESCO Bulk download services here: https://apiportal.uis.unesco.org/bdds

Functions:
    read_zip - reads a csv from a zipped folder on the web without saving the file locally
    datasets - returns available datasets to query
    indicator_list - returns available indicators for a specific dataset
    get_bulk - returns data for all indicators in a dataset
    get_indicator - returns data for an indicator in a dataset
"""

import requests
import pandas as pd
import io
from zipfile import ZipFile
from typing import Optional


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


def datasets() -> pd.DataFrame:
    """
    Returns a dataframe of available UNESCO datasets to query
    along with a downloadable link for the bulk data
    """
    
    base_url = 'https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/'
    unesco_dict = {'dataset':['SDG Global and Thematic Indicators', 'Other Policy Relevant Indicators (OPRI)', 
                              'Research and Development (R&D)', ' Innovation',
                              'Cultural Employment', 'Feature Films', 'Cultural Trade', 'SDG 11',
                              'Demographic and Socio-economic Indicators'],
                   'code':['SDG', 'OPRI', 
                           'SCI', 'INNO',
                           'CLTE', 'FILM', 'CLTT', 'SDG11',
                           'DEM'],
                   'category':['Education', 'Education', 
                               'Science', 'Science', 
                               'Culture', 'Culture', 'Culture', 'Culture',
                               'External']
                   }
    
    unesco_dict['link'] = [base_url + code + '.zip' for code in unesco_dict['code']]
    
    return pd.DataFrame(unesco_dict)


def indicator_list(dataset_code: str) -> pd.DataFrame:
    """
    Returns a dataframe with available indicators for a dataset
    
     Parameters
    ----------
    dataset_code : str
        Specify the code for the dataset. Call datasets() to see a dataframe of available datasets
    """
    
    ds = datasets()
    if dataset_code not in list(ds.code):
        raise ValueError(f'{dataset_code} is not a valid code')
    url = ds.loc[ds.code == dataset_code, 'link'].values[0]
    df = read_zip(url, file_name = f'{dataset_code}_LABEL.csv')
    
    return df


def get_bulk(dataset_code: str, *, grouping: Optional[str] = 'NATIONAL') -> pd.DataFrame:
    """
    Downloads data for all indicators in a dataset
    
     Parameters
    ----------
    dataset_code : str
        Specify the code for the dataset. run datasets() to see a dataframe of available datasets
    
    grouping: Optional[str]
        specify the grouping level:
            NATIONAL - country level grouping
            REGIONAL - region level grouping
    """
    
    ds = datasets()
    
    #parameter error handling
    if dataset_code not in list(ds.code):
        raise ValueError(f'{dataset_code} is not a valid code')
    if grouping not in ['NATIONAL', 'REGIONAL']:
        raise ValueError(f'{grouping} is not a valid grouping')
        
    url = ds.loc[ds.code == dataset_code, 'link'].values[0]
    df = read_zip(url, file_name=f'{dataset_code}_DATA_{grouping}.csv')
    df = df.iloc[:, :4]
    df.columns = ['code', 'country', 'year', 'value']
    
    return df


def get_indicator(indicator_code:str, dataset_code: str, *, grouping: Optional[str] = 'NATIONAL') -> pd.DataFrame:
    """
    Downloads an indicator from a UNESCO dataset
    
    Parameters
    ----------
    indicator_code: str
        specify the code for the indicator. Call indicator_list() for a list of available indicators and codes
    
    dataset_code : str
        Specify the code for the dataset. run datasets() to see a dataframe of available datasets
    
    grouping: Optional[str]
        specify the grouping level:
            NATIONAL - country level grouping
            REGIONAL - region level grouping
    """
    
    df = get_bulk(dataset_code, grouping = grouping)
    if len(df[df.code == indicator_code]) > 0:
        df = df[df.code == indicator_code]
        df = df.drop(columns='code')

        return df

    else:
        raise ValueError(f'{indicator_code} is invalid')


















    
    