""" UIS User interface module

This module provides a user interface to access data from the UIS database. The UIS class extracts data from the UIS
database and provides methods to access the data in a structured format. The UIS class also provides methods to access
metadata, readme files, and information about countries, regions, and variables.

Other functions in this module provide information about the datasets available in the UIS database and the themes
associated with the datasets. Functionality also exists to clear the cache and refresh the data from the UIS website.

"""

from unesco_reader.bulk.formatting import UISData
from unesco_reader.bulk.read import UISInfoScraper, get_zipfile
from tabulate import tabulate
import pandas as pd
from functools import lru_cache
from unesco_reader.config import logger, NoDataError


@lru_cache
def fetch_info(refresh: bool = False) -> list[dict]:
    """Fetch information about the datasets available in the UIS database."""

    # Clear the cache if refresh is True
    if refresh:
        fetch_info.cache_clear()

    return UISInfoScraper.get_links()


def fetch_dataset_info(dataset_name: str, refresh: bool = False) -> dict:
    """Fetch information about a specific dataset."""

    # get dataset information
    datasets = fetch_info(refresh)
    for dataset in datasets:
        if dataset_name.lower().strip() == dataset["name"].lower().strip():
            return dataset
    else:
        raise ValueError(
            f"Dataset not found: {dataset_name}. \nPlease select from the following datasets:\n "
            f"{', '.join([name['name'] for name in datasets])}"
        )


@lru_cache
def fetch_data(href, refresh: bool = False) -> UISData:
    """Fetch data from a url"""

    # Clear the cache if refresh is True
    if refresh:
        fetch_data.cache_clear()

    return UISData(get_zipfile(href))


def clear_all_caches() -> None:
    """Clear all caches.

    This function will clear all caches used. Any subsequent calls to the functions
    that use caching will fetch the data from the website.

    NOTE: any UIS objects already created will still have the old data. You will need to
    run the `refresh()` method get the latest data.
    """

    fetch_info.cache_clear()
    fetch_data.cache_clear()
    logger.info("All caches cleared.")


def info(refresh: bool = False) -> None:
    """Display information about the data available in the UIS database.

    This function will print dataset names, themes, and date of the last update
    from the UIS website. NOTE: cache is used to store the data and prevent multiple
    requests to the UIS website. If you want to refresh the cache and get the latest data, set refresh=True.

    Args:
        refresh: if True, refresh the cache and fetch the links from the website

    """

    _info = fetch_info(refresh)
    headers = [key for key in _info[0].keys() if key != "href"]
    rows = [{k: v for k, v in item.items() if k != "href"} for item in _info]
    rows_list = [list(row.values()) for row in rows]
    print(tabulate(rows_list, headers=headers, tablefmt="simple"))


def available_datasets(theme: str = None, refresh=True) -> list[str]:
    """Return a list of available datasets in the UIS database.

    Args:
        theme: if specified, return only datasets in the specified theme. run info() to get more information
        refresh: if True, refresh the cache and fetch the links from the website

    Returns: list of dataset names
    """

    datasets = fetch_info(refresh)

    if theme is not None:
        # check if theme is valid
        if theme.lower().strip() not in [
            dataset["theme"].lower().strip() for dataset in datasets
        ]:
            raise ValueError(
                f"Theme not found: {theme}. \nPlease select from the following themes:\n "
                f"{', '.join(theme_name for theme_name in list(set([dataset['theme'] for dataset in datasets])))}"
            )

        return [
            dataset["name"]
            for dataset in fetch_info(refresh)
            if dataset["theme"].lower().strip() == theme.lower().strip()
        ]

    return [dataset["name"] for dataset in fetch_info(refresh)]


class UIS:
    """A class to access UIS data for a specific dataset.

    This class will retrieve information and data from the UIS database for a specific dataset. The data will be cleaned
    and processed to be retrievable in a structured and expected format as pandas dataframes. The data than be accessed
    is country data, regional data, metadata, countries, regions, and variables. However, not all datasets may have all
    types of data available. For example some datasets might not have regional data or metadata. In those cases
    calling the respective methods will raise an error. Additional information is also
    accessible though class attributes and methods, such as dataset name, theme, latest update, and displaying the full
    dataset documentation.

    By default, the data is cached to prevent multiple requests to the UIS website. Additional instantiations of the
    UIS class for the same dataset will use the cached data. Data can be refreshed by calling the refresh() method.
    Outside the UIS class, caches can be cleared by calling the clear_all_caches() function.

    # Usage:

    To instantiate the class, provide the name of the dataset as a string. Available datasets can be found by calling
    the available_datasets() function or by calling the info() function to display additional information about all
    datasets.
        >>> sdg = UIS('SDG Global and Thematic Indicators')

    To display information about the dataset, call the info() method.
        >>> sdg.info()

    Information is also available through class attributes:
        >>> sdg.name
        >>> sdg.theme
        >>> sdg.latest_update
        >>> sdg.readme

    You can display the readme documentation by calling the display_readme() method.
        >>> sdg.display_readme()

    Various methods exist to access the data in different formats:
        To access the country:
        >>> sdg.get_country_data()

        By default, the `get_country_data()` method will return the country data as a pandas DataFrame with only the
        necessary columns. To include metadata columns, set `include_metadata=True`. To filter the data by region, set
        the region parameter to the region id. To get information about available regions, call the `get_regions()`
        method.
        >>> sdg.get_country_data(include_metadata=True, region='WB:World')

        To access the regional data:
        >>> sdg.get_region_data()
        By default, the `get_region_data()` method will return the regional data as a pandas DataFrame with only the
        necessary columns. To include metadata columns, set `include_metadata=True`.

        To access the metadata:
        >>> sdg.get_metadata()

        To access the available countries, regions, and variables:
        >>> sdg.get_countries()
        >>> sdg.get_regions()
        >>> sdg.get_variables()

        To refresh the data, call the refresh() method.
        >>> sdg.refresh()

        # NOTE:
        This package is designed to scrape data from the UIS Bulk Download page since no API is available. As a result
        this approach may cause slow performance in areas of low speed internet connection for larger datasets.
        Additionally unexpected errors may arise if the UIS website structure changes or the structure of the data files
        changes. Please report any issues encountered on the package repository: https://github.com/lpicci96/unesco_reader
    """

    def __init__(self, dataset_name: str):
        self._dataset_info = fetch_dataset_info(dataset_name)  # get dataset information
        self._data = fetch_data(self._dataset_info["href"])  # get the data
        logger.info(f"Dataset loaded successfully.")

    def __str__(self):
        return f"UIS dataset: {self._dataset_info['name']}"

    def __repr__(self):
        return f"UIS dataset: {self._dataset_info['name']}"

    def refresh(self) -> None:
        """Refresh the data by fetching the latest data from the UIS website."""

        self._dataset_info = fetch_dataset_info(
            self._dataset_info["name"], refresh=True
        )
        self._data = fetch_data(self._dataset_info["href"], refresh=True)
        logger.info(f"Data refreshed successfully.")

    def info(self) -> None:
        """Display information about the dataset."""

        _info = [
            ["latest update" if key == "latest_update" else key, value]
            for key, value in self._dataset_info.items()
            if key != "href"
        ]

        # Use tabulate to format this list, specifying no headers and a plain format
        print(tabulate(_info, tablefmt="simple"))

    @property
    def name(self) -> str:
        """Return the name of the dataset."""
        return self._dataset_info["name"]

    @property
    def theme(self) -> str:
        """Return the theme of the dataset."""
        return self._dataset_info["theme"]

    @property
    def latest_update(self) -> str:
        """Return the date of the last update of the dataset."""
        return self._dataset_info["latest_update"]

    def get_country_data(
        self, include_metadata: bool = False, region: str | None = None
    ) -> pd.DataFrame:
        """Return the data as a pandas DataFrame.

        Args:
            include_metadata: if True, include metadata columns in the DataFrame.
            region: the region id to filter the data by. This will keep only countries in the specified region.
                    If None (default), all countries are returned. Run get_regions() to get information about available regions.

        Returns:
            country data as a pandas DataFrame
        """
        df = self._data.country_data

        # remove metadata columns if include_metadata is False
        if not include_metadata:
            df = df[
                [
                    "country_id",
                    "country_name",
                    "indicator_id",
                    "indicator_label",
                    "year",
                    "value",
                ]
            ]

        if region is not None:  # if a region is specified, try filter the data
            if (
                self._data.region_concordance is None
            ):  # if regional data is not available, raise an error
                raise ValueError("Regional data is not available for this dataset.")

            if (
                region not in self._data.region_concordance["region_id"].unique()
            ):  # if no region found, raise an error
                raise ValueError(f"Region ID not found: {region}")

            countries_in_region = self._data.region_concordance.loc[
                self._data.region_concordance["region_id"] == region, "country_id"
            ]
            df = df[df["country_id"].isin(countries_in_region)]

        return df.reset_index(drop=True)

    def get_metadata(self) -> pd.DataFrame:
        """Return the metadata as a pandas DataFrame."""

        if self._data.metadata is None:
            raise NoDataError("Metadata is not available for this dataset.")

        return self._data.metadata

    def get_region_data(self, include_metadata: bool = False) -> pd.DataFrame:
        """Return the regional data as a pandas DataFrame.

        Args:
            include_metadata: if True, include metadata columns in the DataFrame

        Returns:
            regional data as a pandas DataFrame
        """

        if self._data.region_data is None:
            raise NoDataError("Regional data is not available for this dataset.")

        df = self._data.region_data

        if not include_metadata:
            df = df[["region_id", "indicator_id", "indicator_label", "year", "value"]]

        return df

    def get_countries(self) -> pd.DataFrame:
        """Return the available countries and their information as a pandas DataFrame.

        The returned dataframe will contain county IDs as ISO3 codes and country names.
        """

        if self._data.country_concordance is None:
            raise NoDataError(
                "Information about countries is not available for this dataset."
            )

        return self._data.country_concordance

    def get_regions(self) -> pd.DataFrame:
        """Return the available regions and their information as a pandas DataFrame.

        The returned dataframe will contain region IDs, country id and name that belong to the region,
        the entity that groups countries (e.g. WB for World Bank regions), and the region name.
        """

        if self._data.region_concordance is None:
            raise NoDataError(
                "Information about regions is not available for this dataset."
            )

        return self._data.region_concordance

    def get_variables(self) -> pd.DataFrame:
        """Return the available variables and their information as a pandas DataFrame.

        The returned dataframe will contain variable IDs, variable names, and descriptions.
        """

        if self._data.variable_concordance is None:
            raise NoDataError(
                "Information about variables is not available for this dataset."
            )

        return self._data.variable_concordance

    @property
    def readme(self) -> str:
        """Return the readme file as a string."""
        if self._data.readme is None:
            raise NoDataError("Readme file is not available for this dataset.")
        return self._data.readme

    def display_readme(self) -> None:
        """Display the readme file."""

        print(self.readme)
