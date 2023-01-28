"""UNESCO Institute of Statistics (UIS) data reader.

This package provides functions to read data from the UNESCO Institute of Statistics
(UIS) bulk data download service. The data is available at
https://apiportal.uis.unesco.org/bdds
"""

import pandas as pd
from zipfile import ZipFile
from tabulate import tabulate
from typing import Tuple
import io

from unesco_reader.config import PATHS, logger
from unesco_reader import common

BASE_URL = (
    "https://apimgmtstzgjpfeq2u763lag.blob.core.windows.net/content/MediaLibrary/bdds/"
)

DATASETS = pd.read_csv(PATHS.DATASETS / "uis_datasets.csv").assign(
    link=lambda df: df.dataset_code.apply(lambda x: f"{BASE_URL}{x}.zip")
)


def get_dataset_code(dataset: str) -> str:
    """Return the dataset code from either a code or name

    Args:
        dataset: Name of the dataset, either the code or the name

    Returns:
        The dataset code

    Raises:
        ValueError: If the dataset is not found
    """

    if dataset in DATASETS.dataset_name.values:
        return DATASETS.loc[DATASETS.dataset_name == dataset, "dataset_code"].values[0]
    elif dataset in DATASETS.dataset_code.values:
        return dataset
    else:
        raise ValueError(f"Dataset not found: {dataset}")


def available_datasets(as_names: bool = False, category: str = None) -> list:
    """Return a list of available datasets

    Args:
        as_names: Return the list of datasets as names instead of codes
        category: Return only datasets from a specific category.
            Available catagories are ['education', 'science', 'culture', 'external']

    Returns:
        A list of available datasets

    Raises:
        ValueError: If the category is not found
    """

    datasets = DATASETS.copy()
    if category is not None:
        if category not in datasets.dataset_category.unique():
            raise ValueError(f"Category not found: {category}")
        datasets = datasets.loc[datasets.dataset_category == category, :]

    if as_names:
        return datasets.dataset_name.values.tolist()

    return datasets.dataset_code.values.tolist()


def dataset_info(dataset: str) -> None:
    """Return information about a dataset

    Args:
        dataset: Name of the dataset, either the code or the name

    Returns:
        Information about the dataset
    """

    dataset_code = get_dataset_code(dataset)
    print(tabulate(DATASETS.loc[DATASETS.dataset_code == dataset_code, :].T))


def format_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
    """Format the metadata DataFrame

    This function is used to format the metadata DataFrame, by merging duplicates
    into a single row, separating the metadata by a ` | ` as suggested by the UIS
    tutorial, And pivoted so that each metadata type is its own column.

    Args:
        metadata_df: DataFrame containing metadata

    Returns:
        A metadata DataFrame pivoted so that metadata types are joined and stored in columns
    """

    # filter for the rows that need to be joined together
    formatted = (
        metadata_df[
            metadata_df.duplicated(
                subset=["INDICATOR_ID", "COUNTRY_ID", "YEAR", "TYPE"], keep=False
            )
        ]
        .groupby(by=["INDICATOR_ID", "COUNTRY_ID", "YEAR", "TYPE"], group_keys=False)[
            "METADATA"
        ]
        .apply(" | ".join)
        .reset_index()
    )

    return (
        pd.concat(
            [
                metadata_df[
                    ~metadata_df.duplicated(
                        subset=["INDICATOR_ID", "COUNTRY_ID", "YEAR", "TYPE"],
                        keep=False,
                    )
                ],
                formatted,
            ]
        )
        .pivot(
            index=["INDICATOR_ID", "COUNTRY_ID", "YEAR"],
            columns="TYPE",
            values="METADATA",
        )
        .reset_index()
    )


def format_national_data(
    national_data: pd.DataFrame,
    indicators_dict: dict,
    countries_dict: dict,
    metadata: pd.DataFrame = None,
) -> pd.DataFrame:
    """Format the national data DataFrame

    This function is used to format the national data DataFrame, by assigning a COUNTRY_NAME
    and INDICATOR_NAME column using countries_dict and indicators_dict dictionaries as mappers,
    and merging the metadata DataFrame if provided.

    Args:
        national_data: DataFrame containing national data
        indicators_dict: Dictionary containing the mapping of INDICATOR_ID to INDICATOR_NAME
        countries_dict: Dictionary containing the mapping of COUNTRY_ID to COUNTRY_NAME
        metadata: DataFrame containing metadata

    Returns:
        A formatted national data DataFrame
    """

    national_data = national_data.assign(
        COUNTRY_NAME=lambda d: d.COUNTRY_ID.map(countries_dict),
        INDICATOR_NAME=lambda d: d.INDICATOR_ID.map(indicators_dict),
    )

    if metadata is not None:
        return national_data.merge(
            metadata, on=["INDICATOR_ID", "COUNTRY_ID", "YEAR"], how="left"
        )

    return national_data


def read_metadata(folder: ZipFile, dataset_code: str) -> pd.DataFrame | None:
    """Read metadata from a zipped folder

    Args:
        folder: ZipFile object containing the data
        dataset_code: Code of the dataset

    Returns:
        A DataFrame containing the metadata or None if no metadata is found

    Logs:
        - a message if no metadata is found
    """

    if f"{dataset_code}_METADATA.csv" in folder.namelist():
        return common.read_csv(folder, f"{dataset_code}_METADATA.csv").pipe(
            format_metadata
        )
    else:
        logger.info(f"No metadata found for {dataset_code}")
        return None


def read_regional_data(
    folder: ZipFile, dataset_code: str, indicators_dict: dict
) -> Tuple[pd.DataFrame, pd.DataFrame] | Tuple[None, None]:
    """Read regional data from a zipped folder

    Args:
        folder: ZipFile object containing the data
        dataset_code: Code of the dataset
        indicators_dict: Dictionary containing the mapping of INDICATOR_ID to INDICATOR_NAME

    Returns:
        A tuple with 2 dataframes, the first containing the regional data and the second
        containing the regions or None if no regional data is found

    Logs:
        - a message if no regional data is found
    """

    if (
        f"{dataset_code}_DATA_REGIONAL.csv" in folder.namelist()
        and f"{dataset_code}_REGION.csv" in folder.namelist()
    ):
        regional_data = common.read_csv(
            folder, f"{dataset_code}_DATA_REGIONAL.csv"
        ).assign(INDICATOR_NAME=lambda d: d.INDICATOR_ID.map(indicators_dict))

        regions = common.read_csv(folder, f"{dataset_code}_REGION.csv").rename(
            columns={"COUNTRY_NAME_EN": "COUNTRY_NAME"}
        )

        return regional_data, regions

    else:
        logger.info(f"No regional data found for {dataset_code}")
        return None, None


def read_data(folder: ZipFile, dataset_code: str) -> dict:
    """Read data from folder

    Args:
        folder: ZipFile object containing the data
        dataset_code: Code of the dataset

    Returns:
        A dictionary containing the data including dictionaries for indicators and countries,
        and dataframes for national and regional data
    """

    indicators_dict = common.read_csv(folder, f"{dataset_code}_LABEL.csv").pipe(
        common.mapping_dict
    )
    countries_dict = common.read_csv(folder, f"{dataset_code}_COUNTRY.csv").pipe(
        common.mapping_dict
    )
    metadata = read_metadata(folder, dataset_code)
    national_data = common.read_csv(folder, f"{dataset_code}_DATA_NATIONAL.csv").pipe(
        format_national_data, indicators_dict, countries_dict, metadata
    )
    regional_data, regions = read_regional_data(folder, dataset_code, indicators_dict)

    return {
        "indicators": indicators_dict,
        "countries": countries_dict,
        "national_data": national_data,
        "regional_data": regional_data,
        "regions": regions,
    }


class UIS:
    """An object to extract, store and explore a UNESCO Institute of Statistics (UIS) dataset

    Basic usage:

    - Create an instance of the class, passing a dataset code or name as an argument.
    The dataset code can be found using the `available_datasets` function.
    - Load data to the object calling the `load_data()` Optionally, you can pass a path
    to a zipped folder for the dataset downloaded from the UIS website. If no path is passed,
    the data will be extracted directly from the UIS website.
    - Get the data, use the `get_data` method. This will return a dataframe containing the data.

    For more information on the available functionalities, see the
    full [documentation](https://unesco-reader.readthedocs.io/en/latest/)

    Attributes:
        dataset: The dataset name or code. Call `available_datasets()`
            to get a list of available datasets.
    """

    def __init__(self, dataset: str):

        code = get_dataset_code(dataset)  # get dataset code

        # pass the dataset info to the object
        self._info = (
            DATASETS.loc[DATASETS.dataset_code == code, :]
            .T.reset_index()
            .pipe(common.mapping_dict)
        )
        self._data = {}  # initialize data dictionary

        # set attribute for items in info
        for key in self._info:
            setattr(self, key, self._info[key])

    def _check_if_loaded(self) -> None:
        """Check if data is loaded to the object

        Raises:
            ValueError: If no data is loaded
        """

        if len(self._data) == 0:
            raise ValueError("No data loaded. Call `load_data()` method first")

    def _update_info(self) -> None:
        """Update the dataset info dictionary using loaded data

        This methods adds some info using the loaded data inclusing
        the number of indicators, countries, regions, and time range.
        """

        self._check_if_loaded()  # check if data is loaded

        # get new info
        info = {
            "available indicators": len(
                self._data["indicators"]
            ),  # number of indicators
            "available countries": len(self._data["countries"]),  # number of countries
            "time range": (
                f"{self._data['national_data']['YEAR'].min()} "
                f"-"
                f" {self._data['national_data']['YEAR'].max()}"
            ),  # time range
        }

        # add regional info if available
        if self._data["regions"] is not None:
            info.update(
                {"available regions": len(self._data["regions"]["REGION_ID"].unique())}
            )
        else:
            info.update({"available regions": 0})

        # update the info dictionary
        self._info.update(info)

    def load_data(self, local_path: str = None) -> "UIS":
        """Load data to the object

        Args:
            local_path: Optional local path to the downloaded zip file.
                If no path is provided, the data will be read from the
                [UIS Bulk Download website](https://apiportal.uis.unesco.org/bdds)

        Returns:
            UIS: same object to allow chaining

        Logs:
            - a message indicating that the data was successfully loaded
        """

        if local_path is None:
            response = common.make_request(self._info["link"])
            folder = common.unzip(io.BytesIO(response.content))
        else:
            folder = common.unzip(local_path)

        self._data = read_data(folder, self._info["dataset_code"])
        self._update_info()  # update info using the loaded data
        logger.info(f"Data loaded for dataset: {self._info['dataset_code']}")

        return self

    def get_data(
        self, grouping: str = "national", include_metadata: bool = False
    ) -> pd.DataFrame:
        """Return data

        Args:
            grouping: geographical grouping, either 'national' or 'regional'. Default is 'national'.
            include_metadata: include metadata in the dataframe. Default is False

        Returns:
            pd.DataFrame: dataframe containing the data

        Raises:
            ValueError: if regional data is requested and no regional data
                is available for the dataset, or if an invalid grouping is passed
        """

        self._check_if_loaded()  # check if data is loaded

        # get national data
        if grouping == "national":
            if include_metadata:
                df = self._data["national_data"]
            else:
                df = self._data["national_data"].loc[
                    :,
                    [
                        "INDICATOR_ID",
                        "INDICATOR_NAME",
                        "COUNTRY_ID",
                        "COUNTRY_NAME",
                        "YEAR",
                        "VALUE",
                    ],
                ]

        # get regional data
        elif grouping == "regional":
            if self._data["regional_data"] is None:
                raise ValueError("No regional data available for this dataset")

            if include_metadata:
                df = self._data["regional_data"]
            else:
                df = self._data["regional_data"].loc[
                    :, ["INDICATOR_ID", "INDICATOR_NAME", "REGION_ID", "YEAR", "VALUE"]
                ]

        # raise error if grouping is not valid
        else:
            raise ValueError(f"Invalid grouping: {grouping}")

        return df

    def available_indicators(self, as_names: bool = False) -> list:
        """List available indicators

        Args:
            as_names: Return a list of indicator names instead of codes.
                False by default to return indicator codes.
                Set to True, to return indicator names

        Returns:
            list of indicators
        """

        self._check_if_loaded()  # check if data is loaded

        if as_names:
            return list(self._data["indicators"].values())
        else:
            return list(self._data["indicators"])

    def available_countries(self, as_names: bool = False, region: str = None) -> list:
        """List available countries

        Args:
            as_names: False by default to return country codes. Set to True, to return country names
            region: Select only countries that belong to specific region. None by default

        Returns:
            list of countries

        Raises:
            ValueError: if a specific region is requested and no regional data is available
                or the region is not valid
        """

        self._check_if_loaded()  # check if data is loaded

        if region is not None:  # if user specified regions
            # check if regional data is available
            if self._data["regions"] is None:
                raise ValueError(
                    "No regional data available for this dataset. "
                    "Call `available_countries()` without `regions` argument"
                )

            # check if region is valid
            if region in self._data["regions"]["REGION_ID"].unique():
                # filter countries for the specified region
                return list(
                    self._data["regions"]
                    .loc[
                        lambda d: d["REGION_ID"] == region,
                        "COUNTRY_NAME" if as_names else "COUNTRY_ID",
                    ]
                    .unique()
                )
            # raise error if region is not valid
            else:
                raise ValueError(f"Invalid region: {region}")

        # return all countries
        return (
            list(self._data["countries"].values())
            if as_names
            else list(self._data["countries"])
        )

    def available_regions(self) -> list:
        """List available regions

        Returns:
            list: available regions

        Raises:
            ValueError: if no regional data is available
        """

        self._check_if_loaded()  # check if data is loaded

        if self._data["regions"] is None:
            raise ValueError("No regional data available for this dataset")

        return list(self._data["regions"]["REGION_ID"].unique())

    def info(self) -> None:
        """Print information about the dataset"""

        print(tabulate([[i, j] for i, j in self._info.items()]))
