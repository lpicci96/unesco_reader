
import pandas as pd
from dataclasses import dataclass
import requests
from zipfile import ZipFile
import io
from typing import Optional, Union


def read_csv(folder, file_name: str) -> pd.DataFrame:
    """Reads a csv file from a folder"""
    if file_name not in list(folder.NameToInfo.keys()):
        raise ValueError(f"{file_name} is not found in the folder")
    return pd.read_csv(folder.open(file_name), low_memory=False)

def filter_df(filter_value:Union[str, list], df:pd.DataFrame, column:str)-> pd.DataFrame:
    """filters a dataframe using a string or list"""
    if isinstance(filter_value, str):
        if filter_value not in df[column]:
            raise ValueError(f'{filter_value} not found')
        else:
            return df[df[column] == filter_value]

    elif isinstance(filter_value, list):
        if filter_value not in df[column]:
            raise Warning(f'{filter_value} not found')
        return df[df[column] == filter_value]


@dataclass
class Fetcher:

    dataset: str = None
    grouping: str = None #NATIONAL, REGIONAL, ALL

    def __post_init__(self):

        # check that dataset is valid
        __datasets = pd.read_csv(r"C:\Users\LucaPicci\Documents\GitHub\unesco_reader\unesco_reader\datasets.csv") # reformat
        if self.dataset in list(__datasets.codes):
            self.dataset_info = __datasets[__datasets.codes == self.dataset]
        else:
            raise ValueError(f'{self.dataset} is not a valid dataset code')

        # download data folder
        try:
            response = requests.get(self.dataset_info.urls.values[0])
            self.folder = ZipFile(io.BytesIO(response.content))
        except ConnectionError:
            raise ConnectionError(f'Could not read {self.dataset}')

        # check if grouping is valid
        if self.grouping not in ['NATIONAL', 'REGIONAL']:
            raise ValueError('Invalid grouping. Use "NATIONAL" or "REGIONAL"')
        elif f"{self.dataset}_DATA_{self.grouping}.csv" not in self.folder.NameToInfo.keys()
            raise ValueError(f'{self.grouping} is not valid for this dataset')
        else:
            pass


        #read data

    @property
    def df(self):
        return read_csv(self.folder, f"{self.dataset}_DATA_{self.grouping}.csv")

    @property
    def indicators(self):
        return read_csv(self.folder, f'{self.dataset}_LABEL.csv')

    @property
    def regions(self):
        if self.grouping == "NATIONAL":
            return read_csv(self.folder, f'{self.dataset}_COUNTRY.csv')
        else:
            return read_csv(self.folder, f'{self.dataset}_REGION.csv')

    @property
    def metadata(self):
        return (read_csv(self.folder, f'{self.dataset}_METADATA.csv')
                .groupby(by=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR', 'TYPE'], as_index=False)['METADATA']
                .apply(' / '.join)
                .pivot(index=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'], columns='TYPE', values='METADATA')
                .reset_index())

@dataclass
class UIS(Fetcher):

    indicator_code:Union[str, list] = None
    region:Union[str, list] = None
    start_year:int = None
    end_year:int = None

    include_metadata: Optional[bool] = False
    as_region_name:Optional[bool] = False
    as_indicator_name:Optional[bool] = False


    def __post_init__(self):
        #filter indicator
        if self.indicator_code is not None:
            self.df = filter_df(self.indicator_code, self.df, 'INDICATOR_ID')

        #filter region
        if self.region is not None:
            if self.grouping == 'NATIONAL':
                self.df = filter_df(self.region, self.df, "COUNTRY_ID")
            else:
                self.df = filter_df(self.region, self.df, "REGION_ID")

        #filter years
        if (self.start_year is not None)&(self.end_year is not None):
            if self.start_year > self.end_year:
                raise ValueError('Start year is earlier than end year')

        if self.start_year is not None:
            if self.start_year < self.df['YEAR'].min():
                raise Warning(f'Earliest year available is {self.df["YEAR"].min()}')
            else:
                self.df = self.df[self.df['YEAR']>= self.start_year]

        if self.end_year is not None:
            if self.end_year > self.df['YEAR'].max():
                raise Warning(f'Latest year available is {self.df["YEAR"].max()}')
            else:
                self.df = self.df[self.df['YEAR']<= self.end_year]

        if self.include_metadata:
            if self.grouping == 'NATIONAL':
                self.df = pd.merge(self.df, self.metadata,
                                   on = ['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'],
                                   how='left')
            else:
                raise Warning('Not metadata is available for regional data')

        if self.as_region_name:
            pass
        








