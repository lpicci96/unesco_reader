""" """

from dataclasses import dataclass
import pandas as pd
import os

from unesco_reader.config import PATHS
from unesco_reader import utils


BASE_URL = "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/"

DATASETS = pd.read_csv(f'{PATHS.glossaries}/datasets.csv')
DATASETS['link'] = BASE_URL + DATASETS.code + '.zip'


@dataclass
class Datasets:
    """ """

    names: tuple = tuple(DATASETS.dataset)
    codes: tuple = tuple(DATASETS.code)

    def get_info(self, dataset: str):
        """Get information on a dataset

        dataset (str): dataset name or code
        """

        if dataset in self.codes:
            return DATASETS[DATASETS.code == dataset].reset_index(drop=True).loc[0].to_dict()

        elif dataset in self.names:
            return DATASETS[DATASETS.dataset == dataset].reset_index(drop=True).loc[0].to_dict()

        else:
            raise ValueError(f'Invalid dataset: {dataset}')


datasets = Datasets()


@dataclass
class UIS:
    """
    An object to help extract data from UNESCO Institute
    of Statistics (UIS) Bulk Download Services"""

    dataset: str  # either dataset name or code
    include_metadata: bool = False
    update: bool = False  # update directly from UIS bulk download services

    def __post_init__(self):

        # check that dataset it valid
        if self.dataset in list(DATASETS.code):
            _ = DATASETS[DATASETS.code == self.dataset]
        elif self.dataset in list(DATASETS.dataset):
            _ = DATASETS[DATASETS.dataset == self.dataset]
        else:
            raise ValueError(f'Invalid dataset: {self.dataset}')

        # set dataset info
        self.code = _.code[0]
        self.dataset = _.dataset[0]
        self.category = _.category[0]
        self.link = _.link[0]

        # file_names (dict)
        self._file_names = {'data': f'{self.code}_DATA_NATIONAL.csv',
                            'countries': f'{self.code}_COUNTRY.csv',
                            'labels': f'{self.code}_LABEL.csv',
                            'metadata': f'{self.code}_METADATA.csv'}

        # get the data
        if self.update:
            self.update_data()

        # if update is not True, then check if the folder exists in the data folder
        elif os.path.exists(f'{PATHS.data}/{self._file_names["data"]}'):
            self.__load_data()

        else:
            self.update_data()

    def update_data(self) -> None:
        """ """

        folder = utils.get_zip_from_web(self.link)

        for file in self._file_names.values():
            utils.read_zip(folder, file).to_csv(f'{PATHS.data}/{file}')

        self.__load_data()

        print('Data successfully updated')

    def __load_data(self):
        """ """

        self.labels = pd.read_csv(f'{PATHS.data}/{self._file_names["labels"]}')
        self.countries = pd.read_csv(f'{PATHS.data}/{self._file_names["countries"]}')
        self.metadata = pd.read_csv(f'{PATHS.data}/{self._file_names["metadata"]}')
        self.info = {'dataset': self.dataset,
                     'code': self.code,
                     'category': self.category,
                     'available_indicators': len(self.labels),
                     'available_countries': len(self.countries)}

        self.data = pd.read_csv(f'{PATHS.data}/{self._file_names["data"]}')

    def add_metadata(self):
        """ """
        pass

    def add_country_names(self):
        pass
