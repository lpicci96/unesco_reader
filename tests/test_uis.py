"""Tests for `uis` module."""

import pytest
from unesco_reader import uis
import pandas as pd
from numpy import nan
from zipfile import ZipFile
from unittest.mock import MagicMock, PropertyMock, patch
from unittest import TestCase


def test_get_dataset_code():
    """Test get_dataset_code"""

    assert uis.get_dataset_code("SDG") == "SDG"  # test when a code is provided
    # test when a name is provided
    assert uis.get_dataset_code("SDG Global and Thematic Indicators") == "SDG"
    # test invalid dataset name
    with pytest.raises(ValueError, match='Dataset not found'):
        uis.get_dataset_code("Non-existent dataset")


def test_available_datasets():
    """Test available_indicators"""

    assert isinstance(uis.available_datasets(), list)
    assert len(uis.available_datasets()) > 0

    assert len(uis.available_datasets()) == len(uis.available_datasets(as_names=True))
    assert uis.available_datasets() != uis.available_datasets(as_names=True)

    assert len(uis.available_datasets(category='education')) < len(uis.available_datasets())

    with pytest.raises(ValueError, match='Category not found'):
        uis.available_datasets(category='invalid category')


@pytest.fixture()
def mock_metadata():
    """Mock metadata dataframe

    The dataframe contains 2 countries US and CN. For US, there is only one indicator
    and one year. the TYPE type2 occurs twice, so in formatting will need to be merged
    together, separated by a |. For CN, there are 2 indicators and 2 years, and only one
    TYPE type1, so a formatted dataframe for CN should have 3 rows and NANs in the type2
    column.
    """

    return pd.DataFrame({
        'INDICATOR_ID': ['A', 'A', 'A', 'B', 'B', 'C'],
        'COUNTRY_ID': ['US', 'US', 'US', 'CN', 'CN', 'CN'],
        'YEAR': [2020, 2020, 2020, 2020, 2021, 2021],
        'TYPE': ['type1', 'type2', 'type2', 'type1', 'type1', 'type1'],
        'METADATA': ['data1', 'data2', 'data3', 'data4', 'data 5', 'data6']
    })


def test_format_metadata(mock_metadata):
    """Test format_metadata"""

    expected = pd.DataFrame({'INDICATOR_ID': ['A', 'B', 'B', 'C'],
                             'COUNTRY_ID': ['US', 'CN', 'CN', 'CN'],
                             'YEAR': [2020, 2020, 2021, 2021],
                             'type1': ['data1', 'data4', 'data 5', 'data6'],
                             'type2': ['data2 | data3', nan, nan, nan]})

    pd.testing.assert_frame_equal(uis.format_metadata(mock_metadata), expected,
                                  check_names=False)


@pytest.fixture()
def mock_national_data():
    """Mock national data dataframe"""

    return pd.DataFrame({
        'INDICATOR_ID': ['A', 'A', 'A', 'B', 'B', 'C'],
        'COUNTRY_ID': ['US', 'US', 'US', 'CN', 'CN', 'CN'],
        'YEAR': [2019, 2020, 2021, 2020, 2021, 2021],
        'VALUE': [0, 1, 2, 3, 4, 5]
    })


def test_format_national_data(mock_national_data):
    """Test format_national_data"""

    countries_dict = {'US': 'United States', 'CN': 'China'}
    indicators_dict = {'A': 'Indicator A', 'B': 'Indicator B', 'C': 'Indicator C'}

    expected = pd.DataFrame({'INDICATOR_ID': ['A', 'A', 'A', 'B', 'B', 'C'],
                             'COUNTRY_ID': ['US', 'US', 'US', 'CN', 'CN', 'CN'],
                             'YEAR': [2019, 2020, 2021, 2020, 2021, 2021],
                             'VALUE': [0, 1, 2, 3, 4, 5],
                             'COUNTRY_NAME': ['United States',
                                              'United States',
                                              'United States',
                                              'China',
                                              'China',
                                              'China'],
                             'INDICATOR_NAME': ['Indicator A',
                                                'Indicator A',
                                                'Indicator A',
                                                'Indicator B',
                                                'Indicator B',
                                                'Indicator C']})

    output = uis.format_national_data(mock_national_data, indicators_dict, countries_dict)

    pd.testing.assert_frame_equal(output, expected)
    assert len(output) == len(mock_national_data)


def test_format_national_data_with_metadata(mock_national_data):
    """ """

    countries_dict = {'US': 'United States', 'CN': 'China'}
    indicators_dict = {'A': 'Indicator A', 'B': 'Indicator B', 'C': 'Indicator C'}
    metadata = pd.DataFrame({'INDICATOR_ID': ['A', 'B', 'B', 'C'],
                             'COUNTRY_ID': ['US', 'CN', 'CN', 'CN'],
                             'YEAR': [2020, 2020, 2021, 2021],
                             'type1': ['data1', 'data4', 'data 5', 'data6'],
                             'type2': ['data2 | data3', nan, nan, nan]})

    expected = pd.DataFrame({'INDICATOR_ID': ['A', 'A', 'A', 'B', 'B', 'C'],
                             'COUNTRY_ID': ['US', 'US', 'US', 'CN', 'CN', 'CN'],
                             'YEAR': [2019, 2020, 2021, 2020, 2021, 2021],
                             'VALUE': [0, 1, 2, 3, 4, 5],
                             'COUNTRY_NAME': ['United States',
                                              'United States',
                                              'United States',
                                              'China',
                                              'China',
                                              'China'],
                             'INDICATOR_NAME': ['Indicator A',
                                                'Indicator A',
                                                'Indicator A',
                                                'Indicator B',
                                                'Indicator B',
                                                'Indicator C'],
                             'type1': [nan, 'data1', nan, 'data4', 'data 5', 'data6'],
                             'type2': [nan, 'data2 | data3', nan, nan, nan, nan]})

    output = uis.format_national_data(mock_national_data, indicators_dict, countries_dict, metadata)

    pd.testing.assert_frame_equal(output, expected, check_names=False)
    assert len(output) == len(mock_national_data)


def test_read_metadata_no_metadata():
    """Test read_metadata when no metadata is available"""

    mock_zip = MagicMock(spec=ZipFile)
    mock_zip.namelist.return_value = ["Dataset1_DATA_NATIONAL.csv"]

    result = uis.read_metadata(mock_zip, 'Dataset1')
    assert result is None


def test_read_regional_data_no_regional_data():
    """Test read_regional_data when no regional data is available"""

    mock_zip = MagicMock(spec=ZipFile)
    mock_zip.namelist.return_value = ["Dataset1_DATA_NATIONAL.csv"]

    result = uis.read_regional_data(mock_zip, 'Dataset1', {'A': 'Indicator A'})
    assert result == (None, None)


class TestUIS(TestCase):
    """Tests for the UIS class"""

    def test_check_if_loaded_no_data(self):
        """Test check_if_loaded when no data is loaded"""

        uis_obj = uis.UIS('SDG')
        with pytest.raises(ValueError, match='No data loaded'):
            uis_obj._check_if_loaded()

    def test_check_if_loaded_with_data(self):
        """Test check_if_loaded when data is loaded"""

        uis_obj = uis.UIS('SDG')
        uis_obj._data = {'national_data': 'some_data'}
        uis_obj._check_if_loaded()

    def test_get_data_invalid_grouping(self):
        """Test get_data with invalid grouping"""

        uis_obj = uis.UIS('SDG')
        uis_obj._data = {'national_data': 'some_data'}
        with pytest.raises(ValueError, match='Invalid grouping'):
            uis_obj.get_data('invalid_grouping')

    def test_get_data_regional_no_regional_data(self):
        """Test get_data with regional grouping when no regional data is loaded"""

        uis_obj = uis.UIS('SDG')
        uis_obj._data = {'national_data': 'some_data', 'regional_data': None}
        with pytest.raises(ValueError, match='No regional data available'):
            uis_obj.get_data('regional')

    def test_update_info(self):
        """Test update_info"""

        uis_obj = uis.UIS('SDG')

        # test with no regional data
        uis_obj._data = {'indicators': ['A', 'B', 'C'],
                         'countries': ['US', 'CN'],
                         'national_data': pd.DataFrame({'COUNTRY': ['US', 'US', 'CN', 'CN'],
                                                        'YEAR': [2020, 2021, 2020, 2021],
                                                        'VALUE': [1, 2, 3, 4]}),
                         'regions': None,
                         'regional_data': None
                         }

        uis_obj._update_info()
        assert uis_obj._info == {**uis_obj._info, **{'available indicators': 3,
                                                     'available countries': 2,
                                                     'time range': '2020 - 2021',
                                                     'available regions': 0}}

        # Test with regional data
        uis_obj._data.update({'regions': pd.DataFrame({'REGION_ID': ['R1', 'R2'],
                                                       'REGION': ['Region 1', 'Region 2']})
                              })
        uis_obj._update_info()
        assert uis_obj._info == {**uis_obj._info, **{'available indicators': 3,
                                                     'available countries': 2,
                                                     'time range': '2020 - 2021',
                                                     'available regions': 2}}

    def test_available_indicators(self):
        """Test available_indicators"""

        uis_obj = uis.UIS('SDG')
        uis_obj._data = {'indicators': {'A': 'Indicator A', 'B': 'Indicator B', 'C': 'Indicator C'}}
        assert uis_obj.available_indicators() == ['A', 'B', 'C']
        # test as_names
        assert uis_obj.available_indicators(as_names=True) == ['Indicator A', 'Indicator B', 'Indicator C']

    def test_available_countries(self):
        """Test available_countries"""

        uis_obj = uis.UIS('SDG')

        # test no region specified
        uis_obj._data = {'countries': {'US': 'United States', 'CN': 'China'},
                         'regions': None}
        assert uis_obj.available_countries() == ['US', 'CN']
        assert uis_obj.available_countries(as_names=True) == ['United States', 'China'] # test as_names

        # test with region specified and no regional data

        with pytest.raises(ValueError, match='No regional data available for this dataset'):
            uis_obj.available_countries(region='R1')

        # test with region specified and regional data
        uis_obj._data = {'countries': {'US': 'United States', 'MX': 'Mexico', 'CN': 'China'},
                         'regions': pd.DataFrame({'REGION_ID': ['R1', 'R1', 'R2'],
                                                  'COUNTRY_ID': ['US', 'MX', 'CN'],
                                                  'COUNTRY_NAME': ['United States', 'Mexico', 'China']
                                                  })
                         }

        assert uis_obj.available_countries(region='R1') == ['US', 'MX']
        assert uis_obj.available_countries(region='R1', as_names=True) == ['United States', 'Mexico']

        # test with invalid region
        with pytest.raises(ValueError, match='Invalid region'):
            uis_obj.available_countries(region='invalid_region')

    def test_available_regions(self):
        """Test available_regions"""

        uis_obj = uis.UIS('SDG')

        # test no regional data
        uis_obj._data = {'regions': None}
        with pytest.raises(ValueError, match='No regional data available'):
            uis_obj.available_regions()

        # test with regional data
        uis_obj._data = {'regions': pd.DataFrame({'REGION_ID': ['R1', 'R1', 'R2'],
                                                             'COUNTRY_ID': ['US', 'MX', 'CN'],
                                                             'COUNTRY_NAME': ['United States', 'Mexico', 'China']
                                                  })
                         }
        assert uis_obj.available_regions() == ['R1', 'R2']


