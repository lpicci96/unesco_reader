"""UNESCO Institute of Statistics (UIS) data reader."""

import pandas as pd
from unesco_reader.config import PATHS
from unesco_reader import common
from zipfile import ZipFile


def available_datasets() -> pd.DataFrame:
    """Return a dataframe with available datasets, and relevant information"""

    return (pd.read_csv(PATHS.DATASETS / 'uis_datasets.csv')
            .assign(link=lambda df: df.dataset_code.apply(lambda x: f"{PATHS.BASE_URL}{x}.zip")))


DATASETS = available_datasets()


def format_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
    """Format the metadata DataFrame

    Args:
        metadata_df: DataFrame containing metadata

    Returns:
        A metadata DataFrame pivoted so that metadata types are joined and stored in columns
    """

    return (metadata_df.groupby(by=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR', 'TYPE'], as_index=False)
            ['METADATA']
            .apply(' / '.join)
            .pivot(index=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'], columns='TYPE', values='METADATA')
            .reset_index()
            .rename_axis(None, axis=1)
            )


def map_dataset_name(name: str) -> str:
    """Map a dataset to its code. Raise an error if the dataset is not found.
    """

    if name in DATASETS.dataset_name.values:
        return DATASETS.loc[DATASETS.dataset_name == name, 'dataset_code'].values[0]
    elif name in DATASETS.dataset_code.values:
        return name
    else:
        raise ValueError(f"Dataset not found: {name}")


def transform_data(folder: ZipFile, dataset_code: str) -> pd.DataFrame:
    """Transform the data from the zip file into a DataFrame"""

    df = common.read_csv(folder, f"{dataset_code}_DATA_NATIONAL.csv")
    labels = common.read_csv(folder, f"{dataset_code}_LABEL.csv")
    countries = common.read_csv(folder, f"{dataset_code}_COUNTRY.csv")
    metadata = (common.read_csv(folder, f"{dataset_code}_METADATA.csv")
                .pipe(format_metadata)
                )

    return (df
            .assign(COUNTRY_NAME=lambda d: d.COUNTRY_ID.map(common.mapping_dict(countries)),
                    INDICATOR_NAME=lambda d: d.INDICATOR_ID.map(common.mapping_dict(labels)))
            .merge(metadata, on=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'], how='left')
            )


class UIS:
    """Object to read, store, and explore UIS data

    To use, create an instance of the class, and call the load_data() method. To get the data
    as a pandas DataFrame, call the get_data() method.

    Params:
        dataset: the name or code for a dataset

    Examples:
        >>> uis = UIS('SDG')
        >>> uis.load_data()
        >>> uis.get_data()
    """

    available_datasets = list(DATASETS.dataset_code.values)

    def __init__(self, dataset: str):
        self.dataset_code = map_dataset_name(dataset)
        self.dataset_name = DATASETS.loc[DATASETS.dataset_code == self.dataset_code, 'dataset_name'].values[0]
        self.url = DATASETS.loc[DATASETS.dataset_code == self.dataset_code, 'link'].values[0]
        self.category = DATASETS.loc[DATASETS.dataset_code == self.dataset_code, 'dataset_category'].values[
            0]

        self._folder = None
        self.data = None

    def load_data(self):  # add path: str = None later
        """Load data to the object"""

        self._folder = common.unzip_folder(self.url)
        self.data = transform_data(self._folder, self.dataset_code)

    def get_data(self):
        """Return data"""

        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first")
        return self.data
