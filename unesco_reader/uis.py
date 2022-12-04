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
    formatted = (metadata_df[metadata_df.duplicated(subset=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR', 'TYPE'],
                                                    keep=False)]
                 .groupby(by=["INDICATOR_ID", "COUNTRY_ID", "YEAR", "TYPE"]
                          )
                 ['METADATA']
                 .apply(' | '.join)
                 .reset_index()
                 )

    return (pd.concat([metadata_df[~metadata_df.duplicated(subset=
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


def _read_national_data(folder: ZipFile, dataset_code: str, country_dict: dict, label_dict: dict) -> pd.DataFrame:
    """ """

    df = common.read_csv(folder, f"{dataset_code}_DATA_NATIONAL.csv")
    df = df.assign(
        COUNTRY_NAME=lambda d: d.COUNTRY_ID.map(country_dict),
        INDICATOR_NAME=lambda d: d.INDICATOR_ID.map(label_dict),
    )

    # add metadata
    if f"{dataset_code}_METADATA.csv" in folder.namelist():
        metadata = common.read_csv(folder, f"{dataset_code}_METADATA.csv").pipe(
            format_metadata
        )
        return df.merge(metadata, on=["INDICATOR_ID", "COUNTRY_ID", "YEAR"], how="left")

    else:
        logger.debug(f"No metadata found for {dataset_code}")
        return df


def _read_regional_data(folder: ZipFile, dataset_code: str) -> dict[str: pd.DataFrame]:
    """Read regional data from folder

    Args:
        folder: ZipFile object containing the data
        dataset_code: Code of the dataset

    Returns:
        dict: dictionary with dataframe for regional data and region codes/names
    """

    if f"{dataset_code}_DATA_REGIONAL.csv" in folder.namelist():
        return {'regional_data': common.read_csv(folder, f"{dataset_code}_DATA_REGIONAL.csv"),
                'regions': (common.read_csv(folder, f"{dataset_code}_REGION.csv")
                            .rename(columns={'COUNTRY_NAME_EN': 'COUNTRY_NAME'})
                            )
                }
    else:
        logger.debug(f"No metadata found for {dataset_code}")
        return {'regional_data': None, 'regions': None}


def read_data(folder: ZipFile, dataset_code: str) -> dict:
    """Read national data from a zip file

    Args:
        folder: ZipFile object containing the data
        dataset_code: Code of the dataset to be read

    Returns:
        A DataFrame with the data
    """

    data = {}

    # read labels and countries
    data.update({'indicators': (common.read_csv(folder, f"{dataset_code}_LABEL.csv")
                                .pipe(common.mapping_dict)),
                 'countries': (common.read_csv(folder, f"{dataset_code}_COUNTRY.csv")
                               .pipe(common.mapping_dict))
                 })

    # add national data
    data.update({'national_data': _read_national_data(folder, dataset_code, data['countries'], data['indicators'])})

    # add regional data
    data.update(_read_regional_data(folder, dataset_code))

    return data


class UIS:
    """Object to read, store, and explore UIS data

    To use, create an instance of the class, and call the load_data() method. To get the data
    as a pandas DataFrame, call the get_data() method.

    Params:
        dataset: the name or code for a dataset
    """

    available_datasets = list(DATASETS.dataset_code.values)

    def __init__(self, dataset: str):
        """Initialize the object

        Args:
            dataset: Name or code of the dataset
        """

        self._code = get_dataset_code(dataset)
        self._info = {"code": self._code,
                      "name": DATASETS.loc[DATASETS.dataset_code == self._code, "dataset_name"].values[0],
                      "url": DATASETS.loc[DATASETS.dataset_code == self._code, "link"].values[0],
                      "category": DATASETS.loc[DATASETS.dataset_code == self._code, "dataset_category"].values[0]
                      }
        self._data = {}
        self._descr = {}
        self._regional_data = False

    def __check_if_loaded(self) -> None:
        """Check if data has been loaded"""

        if len(self._data) == 0:
            raise ValueError("No data loaded. Call `load_data()` method first")

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._info['name']

    @property
    def url(self):
        return self._info['url']

    @property
    def category(self):
        return self._info['category']

    @property
    def info(self):
        return self._info

    def available_indicators(self, names: bool = False) -> list:
        """List available indicators

        Args:
            names: False by default to return indicator codes. Set to True, to return indicator names

        Returns:
            list of indicators
        """

        self.__check_if_loaded()

        if names:
            return list(self._data['indicators'].values())
        else:
            return list(self._data['indicators'])

    def available_countries(self, names: bool = False, regions: str | list = None) -> list:
        """List available countries

        Args:
            names: False by default to return country codes. Set to True, to return country names
            regions: Select only countries that belong to specific region(s). None by default

        Returns:
            list of countries
        """

        self.__check_if_loaded()

        if regions is not None:
            if self._regional_data:
                if isinstance(regions, str):
                    regions = [regions]
                return (self
                        ._data['regions']
                        .loc[lambda d: d['REGION_ID'].isin(regions),
                             "COUNTRY_NAME" if names else "COUNTRY_ID"]
                        .unique()
                        )
            else:
                raise ValueError(f"No regional data available for {self._code}")

        else:
            return list(self._data['countries'].values()) if names else list(self._data['countries'])

    def available_regions(self):
        """ """

        self.__check_if_loaded()

        if self._regional_data:
            return self._data['regions']['REGION_ID'].unique()
        else:
            raise ValueError(f"No regional data available for {self._code}")

    def __update_info(self) -> None:
        """Updated the dataset description dictionary"""

        self.__check_if_loaded()

        info = {'available indicators': len(self._data['indicators']),
                'available countries': len(self._data['countries']),
                'time range': f"{self._data['national_data']['YEAR'].min()} - {self._data['national_data']['YEAR'].max()}"
                }

        if self._regional_data is True:
            info.update({
                'available regions': len(self._data['regions']['REGION_ID'].unique())
            })
        else:
            info.update({'available regions': None})

        self._info.update(info)

    def load_data(self, local_path: str = None) -> 'UIS':
        """Load data to the object

        Args:
            local_path: Optional local path to the downloaded zip file.
            If no path is provided, the data will be read from the web

        Returns:
            UIS: same object to allow chaining
        """

        if local_path is None:
            folder = common.unzip_folder_from_web(self._info["url"])
        else:
            folder = common.unzip_folder_from_disk(local_path)

        self._data.update(read_data(folder, self._code))

        # flag is regional data is available
        if self._data['regional_data'] is not None:
            self._regional_data = True

        # update dataset info
        self.__update_info()

        logger.info(f"Data loaded for dataset: {self._code}")
        return self

    def get_data(self, grouping: str = "national", include_metadata: bool = False) -> pd.DataFrame:
        """Return data

        Args:
            grouping: geographical grouping, either 'national' or 'regional'. Default is 'national'.
            include_metadata: include metadata in the dataframe. Default is False

        Returns:
            pd.DataFrame: dataframe containing the data
        """

        if len(self._data) == 0:
            raise ValueError("No data loaded. Call `load_data()` method first")

        if grouping == "national":
            if include_metadata:
                return self._data["national_data"]
            else:
                return (self._data["national_data"]
                            .loc[:, ["INDICATOR_ID", "INDICATOR_NAME", "COUNTRY_ID", "COUNTRY_NAME", "YEAR", "VALUE"]]
                        )

        elif grouping == "regional":
            if self._regional_data:
                if include_metadata:
                    return self._data["regional_data"]
                else:
                    return (self._data["regional_data"]
                                .loc[:, ["INDICATOR_ID", "INDICATOR_NAME", "REGION_ID", "YEAR", "VALUE"]]
                                )

            else:
                raise ValueError(f"No regional data available for {self._code}")

        else:
            raise ValueError(f'Invalid grouping: {grouping}')
