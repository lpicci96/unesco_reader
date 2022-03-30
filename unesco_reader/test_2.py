import pandas as pd
from typing import Optional
from dataclasses import dataclass
import requests
import io
from zipfile import ZipFile
import warnings


def read_csv(folder, file_name: str) -> pd.DataFrame:
    if file_name not in list(folder.NameToInfo.keys()):
        raise ValueError(f"{file_name} is not found in the folder")
    return pd.read_csv(folder.open(file_name), low_memory=False)


datasets = pd.read_csv("datasets.csv")


@dataclass
class Fetcher:

    code: str = None
    grouping: str = 'NATIONAL'

    def __post_init__(self):
        if self.code not in list(datasets.codes):
            raise ValueError(f'{self.code} is not a valid dataset code')
        if self.grouping not in ['NATIONAL', 'REGIONAL']:
            raise ValueError(f'{self.grouping} is not a valid grouping')

        try:
            response = requests.get(self.url)
            self.folder = ZipFile(io.BytesIO(response.content))
        except ConnectionError:
            raise ConnectionError(f'Could not read {self.name}')

        self.df = read_csv(self.folder, f'{self.code}_DATA_{self.grouping}.csv')

    @property
    def name(self):
        return datasets.loc[datasets.codes == self.code, 'names'].values[0]

    @property
    def url(self):
        return datasets.loc[datasets.codes == self.code, 'urls'].values[0]

    @property
    def category(self):
        return datasets.loc[datasets.codes == self.code, 'categories'].values[0]

    @property
    def regions(self):
        if self.grouping == 'NATIONAL':
            return read_csv(self.folder, f'{self.code}_COUNTRY.csv')
        else:
            return read_csv(self.folder, f'{self.code}_REGION.csv')

    @property
    def metadata(self):
        return (read_csv(self.folder, f'{self.code}_METADATA.csv')
                .groupby(by=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR', 'TYPE'], as_index=False)['METADATA']
                .apply(' / '.join)
                .pivot(index=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'], columns='TYPE', values='METADATA')
                .reset_index())


@dataclass
class UIS(Fetcher):

    def __post_init__(self):
        super().__post_init__()

    def add_metadata(self):
        if self.grouping == 'NATIONAL':
            self.df = pd.merge(self.df, self.metadata,
                               on = ['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'],
                               how='left')
        else:
            warnings.warn('Metadata is not available for regional data')

    def convert_countries(self, to: Optional[str] = 'name'):
        if to not in ['name', 'code']:
            raise ValueError(f'self{to} is not valid')
        if self.grouping == 'REGIONAL':
            warnings.warn('Grouping is REGIONAL. No conversion available.')
        else:
            pass













