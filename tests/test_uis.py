"""Tests for ui module"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from zipfile import ZipFile
import io


from unesco_reader import uis
from unesco_reader.formatting import UISData
from unesco_reader.config import NoDataError


def test_fetch_info():
    """Test the fetch_info function."""
    # Mock the UISInfoScraper.get_links() method
    with patch("unesco_reader.uis.UISInfoScraper.get_links") as mock_get_links:

        # basic functionality
        mock_get_links.return_value = [
            {
                "theme": "Education",
                "name": "Test Data",
                "latest_update": "January 2022",
                "href": "test.zip",
            }
        ]
        expected = [
            {
                "theme": "Education",
                "name": "Test Data",
                "latest_update": "January 2022",
                "href": "test.zip",
            }
        ]
        assert uis.fetch_info() == expected

        # Test caching
        assert uis.fetch_info() == expected
        assert mock_get_links.call_count == 1

        # Test cache refresh and new data
        mock_get_links.return_value = [
            {
                "theme": "Science",
                "name": "New Data",
                "latest_update": "February 2022",
                "href": "new_test.zip",
            }
        ]
        new_expected = [
            {
                "theme": "Science",
                "name": "New Data",
                "latest_update": "February 2022",
                "href": "new_test.zip",
            }
        ]
        assert uis.fetch_info(refresh=True) == new_expected
        assert mock_get_links.call_count == 2


def test_fetch_data():
    """Test the basic functionality of the fetch_data function"""

    # Mock the get_zipfile function
    with patch("unesco_reader.uis.get_zipfile") as mock_get_zipfile:
        # Mock the ZipFile object
        mock_zipfile = MagicMock(spec=ZipFile)
        mock_zipfile.namelist.return_value = ["test_DATA_NATIONAL.csv"]

        # Create a CSV string
        csv_str = (
            "indicator_id,country_id,year,value,magnitude,qualifier\nind1,1,2020,10,,"
        )
        # Convert the CSV string to bytes and create a BytesIO object
        csv_bytes = io.BytesIO(csv_str.encode())

        # Mock the open method to return the BytesIO object
        mock_zipfile.open.return_value = csv_bytes
        mock_get_zipfile.return_value = mock_zipfile

        # Test the function
        result = uis.fetch_data("https://www.test.zip")
        assert isinstance(result, UISData)
        assert result.dataset_code == "test"
        assert result.country_data["indicator_id"][0] == "ind1"

        # Test caching
        assert uis.fetch_data("https://www.test.zip") == result
        assert mock_get_zipfile.call_count == 1

        # Test cache refresh and new data
        new_csv_str = (
            "indicator_id,country_id,year,value,magnitude,qualifier\nind2,2,2021,20,,"
        )
        new_csv_bytes = io.BytesIO(new_csv_str.encode())
        mock_zipfile.open.return_value = new_csv_bytes

        # Test the function with refresh=True
        result2 = uis.fetch_data("https://www.test.zip", refresh=True)
        assert isinstance(result2, UISData)
        assert result2.dataset_code == "test"
        assert result2.country_data["indicator_id"][0] == "ind2"

        # check that when a different url is passed, the cache is not used and the new data is fetched
        new_csv_str = (
            "indicator_id,country_id,year,value,magnitude,qualifier\nind3,3,2022,30,,"
        )
        new_csv_bytes = io.BytesIO(new_csv_str.encode())
        mock_zipfile.namelist.return_value = ["test2_DATA_NATIONAL.csv"]
        mock_zipfile.open.return_value = new_csv_bytes

        # Test the function with a new URL
        result3 = uis.fetch_data("https://www.different_test.zip")
        assert isinstance(result3, UISData)
        assert result3.dataset_code == "test2"
        assert result3.country_data["indicator_id"][0] == "ind3"
        assert mock_get_zipfile.call_count == 3


def test_fetch_dataset_info():
    """test the fetch_dataset_info function"""

    with patch("unesco_reader.uis.fetch_info") as mock_fetch_info:
        # Mock the fetch_info function
        mock_fetch_info.return_value = [
            {
                "theme": "Education",
                "name": "dataset_1",
                "latest_update": "January 2022",
                "href": "test.zip",
            },
            {
                "theme": "Science",
                "name": "dataset_2",
                "latest_update": "February 2022",
                "href": "new_test.zip",
            },
        ]

        # Test with a dataset that exists
        result = uis.fetch_dataset_info("dataset_1")
        assert result == {
            "theme": "Education",
            "name": "dataset_1",
            "latest_update": "January 2022",
            "href": "test.zip",
        }

        # Test with a dataset that does not exist
        with pytest.raises(
            ValueError,
            match="Dataset not found: invalid dataset name. \nPlease select from the following datasets:\n dataset_1, dataset_2",
        ):
            uis.fetch_dataset_info("invalid dataset name")

        # test with mixed cases and white spaces
        result = uis.fetch_dataset_info(" Dataset_1 ")
        assert result == {
            "theme": "Education",
            "name": "dataset_1",
            "latest_update": "January 2022",
            "href": "test.zip",
        }


def test_clear_all_caches():
    """Test the clear_all_caches function."""

    with patch("unesco_reader.uis.fetch_info") as mock_fetch_info, patch(
        "unesco_reader.uis.fetch_data"
    ) as mock_fetch_data:

        # Call the clear_all_caches function
        uis.clear_all_caches()

        # Check that the caches for fetch_info and fetch_data have been cleared
        mock_fetch_info.cache_clear.assert_called_once()
        mock_fetch_data.cache_clear.assert_called_once()


def test_info(capsys):
    """Test the info function."""

    # Mock the fetch_info function
    with patch("unesco_reader.uis.fetch_info") as mock_fetch_info:
        # Define the return value for the mock
        mock_fetch_info.return_value = [
            {
                "theme": "Education",
                "name": "Test Data",
                "latest_update": "January 2022",
                "href": "test.zip",
            }
        ]

        # Call the function
        uis.info()

        # Check the output
        captured = capsys.readouterr()
        expected_output = (
            "theme      name       latest_update\n"
            "---------  ---------  ---------------\n"
            "Education  Test Data  January 2022\n"
        )
        assert captured.out == expected_output

        # Check that fetch_info was called once
        mock_fetch_info.assert_called_once()


def test_available_datasets():
    """Test the available_datasets function."""

    with patch("unesco_reader.uis.fetch_info") as mock_fetch_info:
        # Define the return value for the mock
        mock_fetch_info.return_value = [
            {
                "theme": "Education",
                "name": "A Data",
                "latest_update": "January 2022",
                "href": "test.zip",
            },
            {
                "theme": "Education",
                "name": "B Data",
                "latest_update": "March 2022",
                "href": "test.zip",
            },
            {
                "theme": "Science",
                "name": "C Data",
                "latest_update": "February 2022",
                "href": "new_test.zip",
            },
        ]

        # basic functionality
        result = uis.available_datasets()
        assert result == ["A Data", "B Data", "C Data"]

        # specify theme
        result = uis.available_datasets(theme="Education")
        assert result == ["A Data", "B Data"]

        # test error when theme is not found
        with pytest.raises(ValueError, match="^Theme not found: invalid theme."):
            uis.available_datasets(theme="invalid theme")

        # test mixed cases and white spaces
        result = uis.available_datasets(theme=" EDUCATION ")
        assert result == ["A Data", "B Data"]


class TestUIS:
    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_init(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the __init__ method of the UIS class."""

        # Mock the return values of the fetch_dataset_info and fetch_data functions
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_fetch_data.return_value = mock_uis_data

        # Initialize the UIS class
        obj = uis.UIS("Test Data")

        # Assert that the fetch_dataset_info and fetch_data functions were called with the correct arguments
        mock_fetch_dataset_info.assert_called_once_with("Test Data")
        mock_fetch_data.assert_called_once_with("test.zip")

        # Assert that the _dataset_info and _data attributes were set correctly
        assert obj._dataset_info == {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        assert obj._data == mock_uis_data

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_refresh(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the refresh method of the UIS class."""

        # Mock the return values of the fetch_dataset_info and fetch_data functions
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_fetch_data.return_value = mock_uis_data

        # Initialize the UIS class
        obj = uis.UIS("Test Data")

        # Reset the mock objects
        mock_fetch_dataset_info.reset_mock()
        mock_fetch_data.reset_mock()

        # Mock the return values of the fetch_dataset_info and fetch_data functions for the refresh method
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "February 2022",
            "href": "test.zip",
        }
        mock_uis_data_refreshed = MagicMock(spec=UISData)
        mock_fetch_data.return_value = mock_uis_data_refreshed

        # Call the refresh method
        obj.refresh()

        # Assert that the fetch_dataset_info and fetch_data functions were called with the correct arguments
        mock_fetch_dataset_info.assert_called_once_with("Test Data", refresh=True)
        mock_fetch_data.assert_called_once_with("test.zip", refresh=True)

        # Assert that the _dataset_info and _data attributes were updated correctly
        assert obj._dataset_info == {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "February 2022",
            "href": "test.zip",
        }
        assert obj._data == mock_uis_data_refreshed

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_info(self, mock_fetch_data, mock_fetch_dataset_info, capsys):
        """Test the info method of the UIS class."""

        # Mock the return values of the fetch_dataset_info and fetch_data functions
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_fetch_data.return_value = mock_uis_data

        # Initialize the UIS class
        obj = uis.UIS("Test Data")

        # Call the info method
        obj.info()

        # Check the output
        captured = capsys.readouterr()
        expected_output = (
            "-------------  ------------\n"
            "theme          Education\n"
            "name           Test Data\n"
            "latest update  January 2022\n"
            "-------------  ------------\n"
        )
        assert captured.out == expected_output

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_properties(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the name, theme, and latest_update properties of the UIS class."""

        # Mock the return values of the fetch_dataset_info and fetch_data functions
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_fetch_data.return_value = mock_uis_data

        # Initialize the UIS class
        obj = uis.UIS("Test Data")

        # Assert that the properties return the correct values
        assert obj.name == "Test Data"
        assert obj.theme == "Education"
        assert obj.latest_update == "January 2022"

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_get_country_data(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the get_country_data method of the UIS class."""

        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }

        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.country_data = pd.DataFrame(
            {
                "country_id": ["1", "2"],
                "country_name": ["Country1", "Country2"],
                "indicator_id": ["ind1", "ind2"],
                "indicator_label": ["Indicator1", "Indicator2"],
                "year": ["2020", "2021"],
                "value": ["10", "20"],
                "some_metadata_column": ["", ""],
            }
        )
        mock_uis_data.region_concordance = pd.DataFrame(
            {
                "country_id": ["1", "2"],
                "region_id": ["A", "B"],
            }
        )
        mock_fetch_data.return_value = mock_uis_data

        obj = uis.UIS("Test Data")  # Initialize the UIS class

        # test basic functionality
        result = obj.get_country_data()
        assert isinstance(result, pd.DataFrame)

        # check that metadata columns are removed when include_metadata is False
        assert "some_metadata_column" not in result.columns

        # check that metadata columns are included when include_metadata is True
        result_with_metadata = obj.get_country_data(include_metadata=True)
        assert "some_metadata_column" in result_with_metadata.columns

        # check that data is filtered by region
        result = obj.get_country_data(region="A")
        assert result["country_id"].tolist() == ["1"]

        # check that error is raised when no region concordance is available
        with pytest.raises(ValueError, match="Region ID not found: invalid region"):
            obj.get_country_data(region="invalid region")

        # check error is raised when no region concordance is available
        mock_uis_data.region_concordance = None
        with pytest.raises(
            ValueError, match="Regional data is not available for this dataset."
        ):
            obj.get_country_data(region="A")

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_get_metadata(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the get_region_data method of the UIS class."""

        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.metadata = pd.DataFrame(
            {
                "indicator_id": ["ind1", "ind2"],
                "indicator_label": ["Indicator1", "Indicator2"],
                "metadata": ["Description1", "Description2"],
            }
        )
        mock_fetch_data.return_value = mock_uis_data

        # test basic functionality
        obj = uis.UIS("Test Data")
        assert isinstance(obj.get_metadata(), pd.DataFrame)

        # check error raised when metadata is not available
        mock_uis_data.metadata = None
        obj = uis.UIS("Test Data")
        with pytest.raises(
            NoDataError, match="Metadata is not available for this dataset."
        ):
            obj.get_metadata()

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_get_region_data(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the get_region_data method of the UIS class."""

        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.region_data = pd.DataFrame(
            {
                "region_id": ["A", "B"],
                "indicator_id": ["ind1", "ind2"],
                "indicator_label": ["Indicator1", "Indicator2"],
                "year": ["2020", "2021"],
                "value": ["10", "20"],
                "some_metadata_column": ["", ""],
            }
        )
        mock_fetch_data.return_value = mock_uis_data

        obj = uis.UIS("Test Data")  # Initialize the UIS class

        # test basic functionality
        result = obj.get_region_data()
        assert isinstance(result, pd.DataFrame)

        # check that metadata columns are removed when include_metadata is False
        assert "some_metadata_column" not in result.columns

        # check that metadata columns are included when include_metadata is True
        result_with_metadata = obj.get_region_data(include_metadata=True)
        assert "some_metadata_column" in result_with_metadata.columns

        # test when region data is not available
        mock_uis_data.region_data = None
        with pytest.raises(
            NoDataError, match="Regional data is not available for this dataset."
        ):
            obj.get_region_data()

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_get_countries(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the get_countries method of the UIS class."""

        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.country_concordance = pd.DataFrame(
            {
                "country_id": ["1", "2"],
                "country_name": ["Country1", "Country2"],
            }
        )
        mock_fetch_data.return_value = mock_uis_data

        obj = uis.UIS("Test Data")

        # test basic functionality
        result = obj.get_countries()
        assert isinstance(result, pd.DataFrame)

        # test when country concordance is not available
        mock_uis_data.country_concordance = None
        with pytest.raises(
                NoDataError,
            match="Information about countries is not available for this dataset.",
        ):
            obj.get_countries()

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_get_regions(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test get_regions method of the UIS class."""

        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.region_concordance = pd.DataFrame(
            {
                "country_id": ["1", "2"],
                "region_id": ["A", "B"],
            }
        )
        mock_fetch_data.return_value = mock_uis_data

        obj = uis.UIS("Test Data")

        # test basic functionality
        result = obj.get_regions()
        assert isinstance(result, pd.DataFrame)

        # test when region concordance is not available
        mock_uis_data.region_concordance = None
        with pytest.raises(
                NoDataError,
            match="Information about regions is not available for this dataset.",
        ):
            obj.get_regions()

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_get_variables(self, mock_fetch_data, mock_fetch_dataset_info):
        """test the get_variables method of the UIS class"""

        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.variable_concordance = pd.DataFrame(
            {
                "indicator_id": ["ind1", "ind2"],
                "indicator_label": ["Indicator1", "Indicator2"],
            }
        )
        mock_fetch_data.return_value = mock_uis_data

        obj = uis.UIS("Test Data")

        # test basic functionality
        result = obj.get_variables()
        assert isinstance(result, pd.DataFrame)

        # test when variables are not available
        mock_uis_data.variable_concordance = None
        with pytest.raises(
                NoDataError,
            match="Information about variables is not available for this dataset.",
        ):
            obj.get_variables()

    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_readme(self, mock_fetch_data, mock_fetch_dataset_info):
        """Test the readme property of the UIS class."""

        # Mock the fetch_dataset_info function
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }

        # Mock the UISData object
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.readme = "This is the readme file."
        mock_fetch_data.return_value = mock_uis_data

        # Initialize the UIS class
        obj = uis.UIS("Test Data")

        # Test the readme property
        assert obj.readme == "This is the readme file."

        # Test when the readme file is not available
        mock_uis_data.readme = None
        with pytest.raises(
                NoDataError, match="Readme file is not available for this dataset."
        ):
            _ = obj.readme

    # test display_readme
    @patch("unesco_reader.uis.fetch_dataset_info")
    @patch("unesco_reader.uis.fetch_data")
    def test_display_readme(self, mock_fetch_data, mock_fetch_dataset_info, capsys):
        """Test the display_readme method of the UIS class."""

        # Mock the fetch_dataset_info function
        mock_fetch_dataset_info.return_value = {
            "theme": "Education",
            "name": "Test Data",
            "latest_update": "January 2022",
            "href": "test.zip",
        }

        # Mock the UISData object
        mock_uis_data = MagicMock(spec=UISData)
        mock_uis_data.readme = "This is the readme file."
        mock_fetch_data.return_value = mock_uis_data

        # Initialize the UIS class
        obj = uis.UIS("Test Data")

        # Call the display_readme method
        obj.display_readme()

        # Check the output
        captured = capsys.readouterr()
        assert captured.out == "This is the readme file.\n"
