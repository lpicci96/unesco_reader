"""Tests for `common` module."""

import pytest
from unesco_reader import common
import pandas as pd
from unesco_reader.config import PATHS
from zipfile import ZipFile


def test_mapping_dict():
    """Test mapping_dict function."""

    mock_df = pd.DataFrame({'COUNTRY_ID': {0: 'AFG',
                                           1: 'ALB',
                                           2: 'DZA',
                                           3: 'ASM',
                                           4: 'AND',
                                           5: 'AGO',
                                           6: 'AIA',
                                           7: 'ATG',
                                           8: 'ARG',
                                           9: 'ARM'},
                            'COUNTRY_NAME_EN': {0: 'Afghanistan',
                                                1: 'Albania',
                                                2: 'Algeria',
                                                3: 'American Samoa',
                                                4: 'Andorra',
                                                5: 'Angola',
                                                6: 'Anguilla',
                                                7: 'Antigua and Barbuda',
                                                8: 'Argentina',
                                                9: 'Armenia'}})

    result_dict = common.mapping_dict(mock_df)
    assert result_dict == {'AFG': 'Afghanistan',
                           'ALB': 'Albania',
                           'DZA': 'Algeria',
                           'ASM': 'American Samoa',
                           'AND': 'Andorra',
                           'AGO': 'Angola',
                           'AIA': 'Anguilla',
                           'ATG': 'Antigua and Barbuda',
                           'ARG': 'Argentina',
                           'ARM': 'Armenia'}
    result_dict_rev = common.mapping_dict(mock_df, key_col='right')
    assert result_dict_rev == {'Afghanistan': 'AFG',
                               'Albania': 'ALB',
                               'Algeria': 'DZA',
                               'American Samoa': 'ASM',
                               'Andorra': 'AND',
                               'Angola': 'AGO',
                               'Anguilla': 'AIA',
                               'Antigua and Barbuda': 'ATG',
                               'Argentina': 'ARG',
                               'Armenia': 'ARM'}

    with pytest.raises(ValueError) as err:
        common.mapping_dict(mock_df, 'invalid_key_col')
    assert str(err.value) == 'Invalid key_col. Please choose from ["left", "right"]'

    with pytest.raises(ValueError) as err:
        common.mapping_dict(mock_df.assign(new_col = 'invalid column value'))
    assert str(err.value) == 'df can only contain 2 columns'


def test_read_csv():
    """test read_csv"""

    folder = ZipFile(f'{PATHS.TEST_FILES}/test_SDG.zip')

    df = common.read_csv(folder, 'SDG_COUNTRY.csv')
    assert isinstance(df, pd.DataFrame)

    with pytest.raises(FileNotFoundError) as err:
        common.read_csv(folder, 'invalid_file.csv')

    assert str(err.value) == "Could not find file: invalid_file.csv"



