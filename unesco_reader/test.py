"""

"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd
from typing import Optional


class Data(ABC):

    @abstractmethod
    def df(self):
        pass

    @abstractmethod
    def info(self):
        pass


@dataclass
class Datasets(Data):
    """
    """

    @property
    def df(self):
        return pd.read_csv("./datasets.csv")

    def __post_init__(self):
        self.names = list(self.df['names'])
        self.urls = list(self.df['urls'])
        self.codes = list(self.df['codes'])

    def info(self, dataset: Optional[str] = None):
        if dataset is None:
            return self.df
        elif dataset in self.codes:
            code = dataset
            name = self.df.loc[self.df.codes == dataset, 'names'].values[0]
            category = self.df.loc[self.df.codes == dataset, 'categories'].values[0]
            if self.df.loc[self.df.codes == dataset, 'regional'].values[0]:
                groupings = 'national, regional'
            else:
                groupings = 'national'
        elif dataset in self.names:
            name = dataset
            code = self.df.loc[self.df.names == dataset, 'codes'].values[0]
            category = self.df.loc[self.df.names == dataset, 'categories'].values[0]
            if self.df.loc[self.df.names == dataset, 'regional'].values[0]:
                groupings = 'national, regional'
            else:
                groupings = 'national'
        else:
            raise ValueError("{dataset} is not a valid dataset")

        print(f"code:\t\t{code}\n"
              f"name:\t\t{name}\n"
              f"category:\t{category}")

    def __repr__(self):
        return repr(list(self.codes))


@dataclass
class UIS(Data):
    """

    """

    dataset: str
    indicator: str = None
    start_year = int
    end_year = int

    def __post_init__(self):
        pass

    @property
    def __df(self):
        pass





    @property
    def df:
        pass
    def info(self):
        pass

