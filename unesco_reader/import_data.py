""" """

from dataclasses import dataclass
import pandas as pd
import os

from unesco_reader.config import PATHS, DATASETS
from unesco_reader import utils


@dataclass
class UIS:
    """
    An object to help extract data from UNESCO Institute
    of Statistics (UIS) Bulk Download Services"""

    dataset: str  # either dataset name or code
    metadata: bool = False
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
        self.link = _.link

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
            self.update_data()

        else:
            self.__update_info()

    def update_data(self) -> None:
        """ """

        folder = utils.get_zip_from_web(self.link)

        for file in self._file_names.keys():
            utils.read_zip(folder, file).to_csv(f'{PATHS.data}/{file}')

        self.__update_info()

        print('Data successfully updated')

    def __update_info(self):
        """ """

        self.data = pd.read_csv(f'{PATHS.data}/{self._file_names["data"]}')
        self.labels = pd.read_csv(f'{PATHS.data}/{self._file_names["labels"]}')
        self.countries = pd.read_csv(f'{PATHS.data}/{self._file_names["countries"]}')
        self.metadata = pd.read_csv(f'{PATHS.data}/{self._file_names["metadata"]}')

        self.info = {'dataset': self.dataset,
                     'code': self.code,
                     'category': self.category,
                     'available_indicators': len(self.labels),
                     'available_countries': len(self.countries)}


    def add_metadata(self):
        """ """
        pass

    def add_country_names(self):
