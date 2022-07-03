import os
import pandas as pd
from dataclasses import dataclass, field


class Paths:
    def __init__(self, project_dir):
        self.project_dir = project_dir

    @property
    def data(self):
        return os.path.join(self.project_dir,"unesco_reader", "data")

    @property
    def glossaries(self):
        return os.path.join(self.project_dir, "unesco_reader", "glossaries")


PATHS = Paths(os.path.dirname(os.path.dirname(__file__)))
BASE_URL = "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/"
DATASETS = (pd.read_csv(f'{PATHS.glossaries}/datasets.csv')
            .assign(link=lambda d: BASE_URL + d.code + '.zip'))


@dataclass
class Datasets:
    """ """

    names: tuple = tuple(DATASETS.dataset)
    codes: tuple = tuple(DATASETS.code)

    def get_info(self, dataset: str):
        """Get information on a dataset"""

        if dataset in self.codes:
            return DATASETS[DATASETS.code == dataset].reset_index(drop=True).loc[0].to_dict()

        elif dataset in self.names:
            return DATASETS[DATASETS.dataset == dataset].reset_index(drop=True).loc[0].to_dict()

        else:
            raise ValueError(f'Invalid dataset: {dataset}')


datasets = Datasets()


