""" Formatting module

This module contains functions to clean and format UIS data
The main class UISData is used to process UIS data from a zipped folder
The data is processed at the time of instantiation and stored in class attributes

"""

from zipfile import ZipFile
import pandas as pd

from unesco_reader.bulk import read
from unesco_reader.config import logger


def order_columns(df: pd.DataFrame, priority_cols: list[str]) -> None | pd.DataFrame:
    """Order columns in a DataFrame based on priority columns

    Args:
        df: dataframe to reorder
        priority_cols: list of priority columns in the desired order. If a column is not in the dataframe, it is removed

    Returns:
        pd.DataFrame: dataframe with columns in the desired order
    """

    # if a column in priority_cols is not in the dataframe, remove it from the list
    priority_cols = [col for col in priority_cols if col in df.columns]

    return df[priority_cols + [col for col in df.columns if col not in priority_cols]]


def cols_to_lower(df: pd.DataFrame, inplace: bool = True) -> pd.DataFrame | None:
    """Convert column names to lowercase

    Args:
        df: dataframe to convert
        inplace: whether to convert in place or return a new dataframe

    Returns: pd.DataFrame | None: dataframe with lowercase column names or None if inplace=True but the dataframe is
    modified in place
    """
    if inplace:
        df.columns = [col.lower() for col in df.columns]
    else:
        return df.rename(columns={col: col.lower() for col in df.columns})


def remove_en_suffix(df, inplace=True) -> pd.DataFrame | None:
    """Removes '_en' or '_EN' suffix from DataFrame column names.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        inplace (bool): If True, modifies the DataFrame in place. Otherwise, returns a new DataFrame.

    Returns:
        pd.DataFrame | None: The DataFrame with column names modified. If inplace=True, returns None but modifies the
        DataFrame in place.
    """

    if inplace:
        df.rename(columns=lambda x: x[:-3] if x.endswith("_en") else x, inplace=True)
        df.rename(columns=lambda x: x[:-3] if x.endswith("_EN") else x, inplace=True)
    else:
        return df.rename(columns=lambda x: x[:-3] if x.endswith("_en") else x).rename(
            columns=lambda x: x[:-3] if x.endswith("_EN") else x
        )


def squash_duplicates(
    df: pd.DataFrame, index_cols: list[str], squashed_col: str
) -> pd.DataFrame:
    """Squash duplicates in a DataFrame separating values by '/' in the squashed column.

    To optimize efficiency, the squashing operation is only performed on the duplicated rows. The squashed rows are
    then appended to the original DataFrame excluding the duplicated rows.

    Args:
        df: The DataFrame to process.
        index_cols: The columns to group by.
        squashed_col: The column to squash.

    Returns:
        pd.DataFrame: The DataFrame with duplicates squashed.
    """

    # find duplicates
    duplicates = df.duplicated(subset=index_cols, keep=False)

    # if no duplicates, return the original dataframe
    if not duplicates.any():
        return df

    # squashed duplicates
    squashed_df = (
        df[duplicates]
        .groupby(index_cols, as_index=False)
        .agg({squashed_col: " / ".join})
    )

    # Remove duplicates from the original DataFrame and append the squashed duplicates
    unique_df = df.drop(df[duplicates].index)
    return pd.concat([unique_df, squashed_df], ignore_index=True)


class UISData:
    """Class to process UIS data from a zipped folder

    This class reads and formats UIS data stored in a zipped file. The data is processed at the time of instantiation
    and stored in class attributes.

    Attributes:
        folder: zipped folder containing the UIS data extracted from the UIS Bulk Download website

        dataset_code: the dataset code extracted from file names in the zipped folder. Naming convention for filed
                    is 'DATASET_CODE_...'. The dataset code is the first part of the file name. If multiple dataset
                    codes are found, an error is raised. This may be a result of an error in the folder structure from UIS
                    or a change in the naming convention. If this error is raised the folder structure should be checked
                    and the code updated to handle the new structure.

        file_names: dictionary of file names in the folder. All the possible files
                    contained in the folder are COUNTRY.csv (country concordance file), REGION.csv (regional
                    concordance file), DATA_NATIONAL.csv (national data), DATA_REGIONAL.csv (regional data), LABEL.csv
                    (variable concordance file), METADATA.csv (metadata file), README (documentation readme file).

        All other attributes are the dataframes read from the files in the folder, and a string for the readme file.
        If a file is not found in the folder, the attribute is set to None.
    """

    def __init__(self, folder: ZipFile):
        self.folder: ZipFile = folder
        self.dataset_code = self.get_dataset_code()
        self.file_names = self.get_file_names()

        # data
        self.readme: str | None = self.get_readme()
        self.country_concordance: pd.DataFrame | None = self.get_country_concordance()
        self.region_concordance: pd.DataFrame | None = self.get_region_concordance()
        self.variable_concordance: pd.DataFrame | None = self.get_variable_concordance()
        self.metadata: pd.DataFrame | None = self.get_metadata()
        self.country_data: pd.DataFrame | None = self.get_country_data()
        self.region_data: pd.DataFrame | None = self.get_region_data()

        logger.debug("UIS data processed successfully")

    @staticmethod
    def _format_col_names(df) -> None:
        """Format column names in a dataframe in place. Convert to lowercase and remove '_en' suffix."""

        cols_to_lower(df)
        remove_en_suffix(df)

    def add_variable_names(self, df: pd.DataFrame) -> None:
        """Add variable names to a dataframe in place using the variable concordance file"""
        if self.variable_concordance is not None:
            mapper = (
                self.variable_concordance.set_index("indicator_id")
                .loc[:, "indicator_label"]
                .to_dict()
            )
            df["indicator_label"] = df["indicator_id"].map(mapper)

        else:
            logger.debug("No variable concordance file found")

    def add_country_names(self, df: pd.DataFrame) -> None:
        """Add country names to a dataframe using the country concordance file"""
        if self.country_concordance is not None:
            mapper = (
                self.country_concordance.set_index("country_id")
                .loc[:, "country_name"]
                .to_dict()
            )
            df["country_name"] = df["country_id"].map(mapper)
        else:
            logger.debug("No country concordance file found")

    def get_dataset_code(self) -> str:
        """Get the dataset code from the folder name"""
        codes = []
        for file in self.folder.namelist():
            codes.append(file.split("_")[0])

        # check that all codes are the same
        if len(set(codes)) > 1:
            raise ValueError("Multiple dataset codes in folder")

        return codes[0]

    def get_file_names(self) -> dict[str, str]:
        """Get a dictionary of file names in the folder which match to expected names"""

        files = {}
        d = {
            "COUNTRY_CONCORDANCE": "COUNTRY.csv",
            "REGION_CONCORDANCE": "REGION.csv",
            "COUNTRY_DATA": "DATA_NATIONAL.csv",
            "REGION_DATA": "DATA_REGIONAL.csv",
            "VARIABLE_CONCORDANCE": "LABEL.csv",
            "METADATA": "METADATA.csv",
            "README": "README",
        }

        for k, v in d.items():
            for file_name in self.folder.namelist():
                if v in file_name:
                    files[k] = file_name

        # if there are no files raise an error
        if not files:
            raise FileNotFoundError("No files found in folder")

        return files

    def get_readme(self) -> str | None:
        """Read the readme file"""
        if self.file_names.get("README"):
            return read.read_md(self.folder, self.file_names["README"])

        logger.debug("No readme file found")
        return None

    def get_country_concordance(self) -> pd.DataFrame | None:
        """Read the country concordance file"""
        if self.file_names.get("COUNTRY_CONCORDANCE"):
            df = read.read_csv(self.folder, self.file_names["COUNTRY_CONCORDANCE"])
            self._format_col_names(df)
            return df

        logger.debug("No country concordance file found")
        return None

    def get_region_concordance(self) -> pd.DataFrame | None:
        """Read the region concordance file"""
        if self.file_names.get("REGION_CONCORDANCE"):
            df = read.read_csv(self.folder, self.file_names["REGION_CONCORDANCE"])
            self._format_col_names(df)
            # split the REGION_ID into grouping_entity and region_name
            df[["grouping_entity", "region_name"]] = df["region_id"].str.split(
                ": ", n=1, expand=True
            )
            return df

        logger.debug("No region concordance file found")
        return None

    def get_variable_concordance(self) -> pd.DataFrame | None:
        """Read the variable concordance file"""
        if self.file_names.get("VARIABLE_CONCORDANCE"):
            df = read.read_csv(self.folder, self.file_names["VARIABLE_CONCORDANCE"])
            self._format_col_names(df)
            return df

        logger.debug("No variable concordance file found")
        return None

    def get_metadata(self) -> pd.DataFrame | None:
        """Read the metadata file"""
        if self.file_names.get("METADATA"):
            df = read.read_csv(self.folder, self.file_names["METADATA"])
            self._format_col_names(df)
            df = squash_duplicates(
                df, ["indicator_id", "country_id", "year", "type"], "metadata"
            )
            self.add_variable_names(df)  # add variable names
            self.add_country_names(df)

            # order columns
            order = [
                "country_id",
                "country_name",
                "indicator_id",
                "indicator_label",
                "year",
            ]
            df = order_columns(df, order)

            return df

        logger.debug("No metadata file found")
        return None

    def get_country_data(self) -> pd.DataFrame | None:
        """Read the country data file"""
        if self.file_names.get("COUNTRY_DATA"):
            df = read.read_csv(self.folder, self.file_names["COUNTRY_DATA"])
            self._format_col_names(df)
            self.add_variable_names(df)  # add variable names
            self.add_country_names(df)  # add country names

            # add metadata
            if self.metadata is not None:
                meta_df = self.metadata.pivot(
                    index=["indicator_id", "country_id", "year"],
                    columns="type",
                    values="metadata",
                ).reset_index()
                df = df.merge(
                    meta_df, how="left", on=["indicator_id", "country_id", "year"]
                )

            # order columns
            order = [
                "country_id",
                "country_name",
                "indicator_id",
                "indicator_label",
                "year",
                "value",
            ]
            df = order_columns(df, order)

            return df

        logger.debug("No country data file found")
        return None

    def get_region_data(self) -> pd.DataFrame | None:
        """Read the region data file"""
        if self.file_names.get("REGION_DATA"):
            df = read.read_csv(self.folder, self.file_names["REGION_DATA"])
            self._format_col_names(df)
            self.add_variable_names(df)  # add variable names

            # order columns
            order = ["region_id", "indicator_id", "indicator_label", "year", "value"]
            df = order_columns(df, order)

            return df
        return None
