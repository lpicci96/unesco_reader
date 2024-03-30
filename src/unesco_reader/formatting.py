""" Format module """

from zipfile import ZipFile
import pandas as pd

from unesco_reader import read


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
        df.rename(columns=lambda x: x[:-3] if x.endswith('_en') else x, inplace=True)
        df.rename(columns=lambda x: x[:-3] if x.endswith('_EN') else x, inplace=True)
    else:
        return (df
                .rename(columns=lambda x: x[:-3] if x.endswith('_en') else x)
                .rename(columns=lambda x: x[:-3] if x.endswith('_EN') else x)
                )


def squash_duplicates(df: pd.DataFrame, index_cols: list[str], squashed_col: str) -> pd.DataFrame:
    """Squash duplicates in a DataFrame separating values by '/' in the squashed column.

    Args:
        df: The DataFrame to process.
        index_cols: The columns to group by.
        squashed_col: The column to squash.

    Returns:
        pd.DataFrame: The DataFrame with duplicates squashed.
    """
    return (df
            .groupby(index_cols)[squashed_col]
            .apply(" / ".join)
            .reset_index()
            )


class UISData:
    """Class to understand file name formats"""

    def __init__(self, folder: ZipFile):
        self.folder = folder
        self.dataset_code = self.get_dataset_code()
        self.file_names = self.get_file_names()

    @staticmethod
    def _format_col_names(df) -> None:
        """Format column names. Convert to lowercase and remove '_en' suffix."""

        cols_to_lower(df)
        remove_en_suffix(df)

    def add_variable_names(self, df: pd.DataFrame) -> None:
        """Add variable names to a dataframe using the variable concordance file"""
        if self.variable_concordance is not None:
            mapper = self.variable_concordance.set_index('indicator_id').loc[:, 'indicator_label'].to_dict()
            df['indicator_label'] = df['indicator_id'].map(mapper)

        # TODO: if no variable concordance file, log message

    def add_country_names(self, df: pd.DataFrame) -> None:
        """Add country names to a dataframe using the country concordance file"""
        if self.country_concordance is not None:
            mapper = self.country_concordance.set_index('country_id').loc[:, 'country_name'].to_dict()
            df['country_name'] = df['country_id'].map(mapper)

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
        d = {'COUNTRY_CONCORDANCE': 'COUNTRY.csv',
             'REGION_CONCORDANCE': 'REGION.csv',
             'COUNTRY_DATA': 'DATA_NATIONAL.csv',
             'REGION_DATA': 'DATA_REGIONAL.csv',
             'VARIABLE_CONCORDANCE': 'LABEL.csv',
             'METADATA': 'METADATA.csv',
             'README': 'README'
             }

        for k, v in d.items():
            for file in self.folder.namelist():
                if v in file:
                    files[k] = file
        return files

    @property
    def readme(self) -> str | None:
        """Read the readme file"""
        if self.file_names.get('README'):
            return read.read_md(self.folder, self.file_names['README'])
        return None

    @property
    def country_concordance(self) -> pd.DataFrame | None:
        """Read the country concordance file"""
        if self.file_names.get('COUNTRY_CONCORDANCE'):
            df = read.read_csv(self.folder, self.file_names['COUNTRY_CONCORDANCE'])
            self._format_col_names(df)
            return df
        return None

    @property
    def region_concordance(self) -> pd.DataFrame | None:
        """Read the region concordance file"""
        if self.file_names.get('REGION_CONCORDANCE'):
            df = read.read_csv(self.folder, self.file_names['REGION_CONCORDANCE'])
            self._format_col_names(df)
            # split the REGION_ID into grouping_entity and region_name
            df[['grouping_entity', 'region_name']] = df['region_id'].str.split(': ', n=1, expand=True)
            return df
        return None

    @property
    def variable_concordance(self) -> pd.DataFrame | None:
        """Read the variable concordance file"""
        if self.file_names.get('VARIABLE_CONCORDANCE'):
            df = read.read_csv(self.folder, self.file_names['VARIABLE_CONCORDANCE'])
            self._format_col_names(df)
            return df
        return None

    @property
    def metadata(self) -> pd.DataFrame | None:
        """Read the metadata file"""
        if self.file_names.get('METADATA'):
            df = read.read_csv(self.folder, self.file_names['METADATA'])
            self._format_col_names(df)
            df = squash_duplicates(df, ['indicator_id', 'country_id', 'year', 'type'], 'metadata')
            return df
        return None

    @property
    def country_data(self) -> pd.DataFrame | None:
        """Read the country data file"""
        if self.file_names.get('COUNTRY_DATA'):
            df = read.read_csv(self.folder, self.file_names['COUNTRY_DATA'])
            self._format_col_names(df)
            self.add_variable_names(df)  # add variable names
            self.add_country_names(df)  # add country names

            # add metadata
            if self.metadata is not None:
                meta_df = (self.metadata.pivot(index=['indicator_id', 'country_id', 'year'], columns='type',
                                               values='metadata')
                           .reset_index()
                           )
                df = df.merge(meta_df, how='left', on=['indicator_id', 'country_id', 'year'])

            return df
        return None

    @property
    def region_data(self) -> pd.DataFrame | None:
        """Read the region data file"""
        if self.file_names.get('REGION_DATA'):
            df = read.read_csv(self.folder, self.file_names['REGION_DATA'])
            self._format_col_names(df)
            self.add_variable_names(df)  # add variable names

            return df
        return None

