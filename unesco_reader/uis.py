"""UNESCO Institute of Statistics (UIS) data reader."""

import pandas as pd

from unesco_reader.config import PATHS
from unesco_reader import common


def available_datasets() -> pd.DataFrame:
    """Return a dataframe with available datasets, and relevant information"""

    return (pd.read_csv(PATHS.DATASETS / 'uis_datasets.csv')
            .assign(link=lambda df: df.dataset_code.apply(lambda x: f"{PATHS.BASE_URL}{x}.zip")))

datasets = available_datasets()


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


def read_dataset(code: str, metadata: bool = False) -> pd.DataFrame:
    """Read a dataset from the UIS website

    Extract country level data from the UIS website for a specific dataset.
    This function joins the data stored in different files into a single DataFrame.

    Args:
        code: dataset code. To see available datasets, use available_datasets()
        metadata: whether to include metadata in the output. Default is False

    Returns:
        A DataFrame with the data for the specified dataset including country names, indicator
        names, and metadata if specified.

    """

    if code not in datasets.dataset_code.values:
        raise ValueError(f"Dataset code not found: {code}")

    url = datasets.loc[datasets.dataset_code == code, 'link'].values[0]
    folder = common.unzip_folder(url)

    df = common.read_csv(folder, f"{code}_DATA_NATIONAL.csv")
    labels = common.read_csv(folder, f"{code}_LABEL.csv")
    countries = common.read_csv(folder, f"{code}_COUNTRY.csv")

    df = (df
          .assign(COUNTRY_NAME = lambda d: d.COUNTRY_ID.map(common.mapping_dict(countries)),
                  INDICATOR_NAME = lambda d: d.INDICATOR_ID.map(common.mapping_dict(labels)))
          )
    if metadata:
        metadata = common.read_csv(folder, f"{code}_METADATA.csv")
        metadata = format_metadata(metadata)
        df = df.merge(metadata, on=['INDICATOR_ID', 'COUNTRY_ID', 'YEAR'], how='left')

    return df

