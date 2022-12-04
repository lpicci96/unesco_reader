"""UNESCO Institute of Statistics (UIS) data reader."""

import pandas as pd
from zipfile import ZipFile

from unesco_reader.config import PATHS, logger
from unesco_reader import common


def available_datasets() -> pd.DataFrame:
    """Return a dataframe with available datasets, and relevant information"""

    return pd.read_csv(PATHS.DATASETS / "uis_datasets.csv").assign(
        link=lambda df: df.dataset_code.apply(lambda x: f"{PATHS.BASE_URL}{x}.zip")
    )


DATASETS = available_datasets()


def format_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
    """Format the metadata DataFrame

    Args:
        metadata_df: DataFrame containing metadata

    Returns:
        A metadata DataFrame pivoted so that metadata types are joined and stored in columns
    """

    # filter for the rows that need to be joined together
    formatted = (metadata_df[metadata_df.duplicated(subset = ['INDICATOR_ID', 'COUNTRY_ID', 'YEAR', 'TYPE'],
                                                    keep=False)]
                 .groupby(by=["INDICATOR_ID", "COUNTRY_ID", "YEAR", "TYPE"]
                          )
                 ['METADATA']
                 .apply(' | '.join)
                 .reset_index()
                 )

    return (pd.concat([metadata_df[~metadata_df.duplicated(subset =
                                                           ['INDICATOR_ID', 'COUNTRY_ID', 'YEAR', 'TYPE'],
                                                           keep=False)],
                       formatted
                       ])
            .pivot(index=["INDICATOR_ID", "COUNTRY_ID", "YEAR"],
                   columns="TYPE",
                   values="METADATA")
            .reset_index()
            )


def get_dataset_code(dataset: str) -> str:
    """Return the dataset code from either a code or name. Raise an error if the dataset is not found.

    Args:
        dataset: Name of the dataset, either the code or the name

    Returns:
        The dataset code
    """

    if dataset in DATASETS.dataset_name.values:
        return DATASETS.loc[DATASETS.dataset_name == dataset, "dataset_code"].values[0]
    elif dataset in DATASETS.dataset_code.values:
        return dataset
    else:
        raise ValueError(f"Dataset not found: {dataset}")


def read_national_data(folder: ZipFile, dataset_code: str) -> pd.DataFrame:
    """Read national data from a zip file

    Args:
        folder: ZipFile object containing the data
        dataset_code: Code of the dataset to be read

    Returns:
        A DataFrame with the data
    """

    df = common.read_csv(folder, f"{dataset_code}_DATA_NATIONAL.csv")
    labels = common.read_csv(folder, f"{dataset_code}_LABEL.csv").pipe(
        common.mapping_dict
    )
    countries = common.read_csv(folder, f"{dataset_code}_COUNTRY.csv").pipe(
        common.mapping_dict
    )

    df = df.assign(
        COUNTRY_NAME=lambda d: d.COUNTRY_ID.map(countries),
        INDICATOR_NAME=lambda d: d.INDICATOR_ID.map(labels),
    )

    if f"{dataset_code}_METADATA.csv" in folder.namelist():

        metadata = common.read_csv(folder, f"{dataset_code}_METADATA.csv").pipe(
            format_metadata
        )
        return df.merge(metadata, on=["INDICATOR_ID", "COUNTRY_ID", "YEAR"], how="left")

    else:
        logger.debug(f"No metadata found for {dataset_code}")
        return df


class UIS:
    """Object to read, store, and explore UIS data

    To use, create an instance of the class, and call the load_data() method. To get the data
    as a pandas DataFrame, call the get_data() method.

    Params:
        dataset: the name or code for a dataset
    """

    available_datasets = list(DATASETS.dataset_code.values)

    def __init__(self, dataset: str, *, regional_data: bool = True):
        """Initialize the object

        Args:
            dataset: Name or code of the dataset
            regional_data: Whether to load regional data

        """

        self._regional_data = regional_data

        self._code = get_dataset_code(dataset)
        name = DATASETS.loc[DATASETS.dataset_code == self._code, "dataset_name"].values[
            0
        ]

        url = DATASETS.loc[DATASETS.dataset_code == self._code, "link"].values[0]

        category = DATASETS.loc[
            DATASETS.dataset_code == self._code, "dataset_category"
        ].values[0]

        self._info: dict = {
            "code": self._code,
            "name": name,
            "url": url,
            "category": category,
        }
        self._data: dict = {}

    @property
    def info(self):
        return self._info

    def load_data(self, path: str = None) -> 'UIS':  # add path: str = None later
        """Load data to the object"""

        if path is None:

            folder = common.unzip_folder_from_web(self._info["url"])
        else:
            folder = common.unzip_folder_from_disk(path)

        self._data["national_data"] = read_national_data(folder, self._code)

        if self._regional_data:
            if f"{self._code}_DATA_REGIONAL.csv" in folder.namelist():
                self._data["regional_data"] = pd.read_csv(
                    folder.open(f"{self._code}_DATA_REGIONAL.csv")
                )
                self._data["regions"] = pd.read_csv(
                    folder.open(f"{self._code}_REGION.csv")
                )

            else:
                logger.debug(f"No regional data available for {self._code}")
                self._regional_data = False

        logger.info(f"Data loaded for {self._code}")
        return self

    def get_data(self, grouping: str = "national") -> pd.DataFrame:
        """Return data"""

        if len(self._data) == 0:
            raise ValueError("No data loaded. Call load_data() first")

        if grouping == "national":
            return self._data["national_data"]
        elif grouping == "regional":
            if self._regional_data:
                return self._data["regional_data"]
            else:
                raise ValueError(f"No regional data available for {self._code}")
