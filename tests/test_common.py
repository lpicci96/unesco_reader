"""Tests for `common` module."""

from unesco_reader import common
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from zipfile import ZipFile
import tempfile
import os
import io


def test_mapping_dict():
    """Test mapping_dict"""

    test_df = pd.DataFrame({"left": [1, 2, 3], "right": ["a", "b", "c"]})

    # test default
    result = common.mapping_dict(test_df)
    expected = {1: "a", 2: "b", 3: "c"}
    assert result == expected

    # test key_col = "right"
    result = common.mapping_dict(test_df, key_col="right")
    expected = {"a": 1, "b": 2, "c": 3}
    assert result == expected

    # test key_col is not left or right
    with pytest.raises(ValueError, match="Invalid key_col. Please choose from"):
        common.mapping_dict(test_df, key_col="invalid_key_col")

    # test df has more than 2 columns
    invalid_df = pd.DataFrame(
        {"left": [1, 2, 3], "right": ["a", "b", "c"], "additional": [True, False, True]}
    )
    with pytest.raises(ValueError, match="df can only contain 2 columns"):
        common.mapping_dict(invalid_df)


@pytest.fixture
def mock_request(status_code, headers):
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = status_code
        mock_get.return_value.headers = headers
        yield mock_get


@pytest.mark.parametrize(
    "status_code, headers", [(200, {"content-type": "application/x-zip-compressed"})]
)
def test_make_request(mock_request, status_code, headers):
    """Test make_request"""

    assert common.make_request("http://test.com") == mock_request.return_value


@pytest.mark.parametrize(
    "status_code, headers", [(404, {"content-type": "application/x-zip-compressed"})]
)
def test_make_request_bad_status(mock_request, status_code, headers):
    """Test make_request when the response status is not 200"""

    with pytest.raises(ConnectionError, match="Could not connect to http://test.com"):
        common.make_request("http://test.com")


@pytest.mark.parametrize(
    "status_code, headers", [(200, {"content-type": "application/pdf"})]
)
def test_make_request_not_zip(mock_request, status_code, headers):
    """Test make_request when the response is not a zip file"""

    with pytest.raises(ValueError, match="The file is not a zip file"):
        common.make_request("http://test.com")


def test_unzip():
    """Test unzip with a valid file-like object"""

    # create a mock file-like object
    mock_zip = io.BytesIO()
    with ZipFile(mock_zip, "w") as zf:
        zf.writestr("test.txt", "This is a test file")

    assert isinstance(common.unzip(mock_zip), ZipFile)


def test_unzip_exceptions():
    """Test unzip exceptions"""

    # test file not found
    with pytest.raises(FileNotFoundError, match="Could not find file"):
        common.unzip("non_existent_file.zip")

    # test bad zip file
    mock_zip = io.BytesIO(b"invalid zip data")
    with pytest.raises(ValueError, match="The file could not be unzipped"):
        common.unzip(mock_zip)


def test_unzip_valid_path():
    """Test unzip when the path is valid"""

    # create a temporary zipfile
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp:
        with ZipFile(temp.name, "w") as zf:
            zf.writestr("test.txt", "This is a test file")
        temp.close()
        # pass the path of the zipfile to the unzip function
        assert isinstance(common.unzip(temp.name), ZipFile)
    # remove the tempfile after the test
    os.remove(temp.name)


@pytest.fixture
def mock_zip_file():
    """Create a mock zipfile from which to read a csv"""

    mock_zip = MagicMock()
    mock_zip.namelist.return_value = ["file1.csv"]
    mock_file = io.StringIO("col1,col2,col3\n1,2,3\n4,5,6")
    mock_zip.open.return_value = mock_file

    return mock_zip


def test_read_csv(mock_zip_file):
    """Test read_csv"""

    expected_df = pd.DataFrame({"col1": [1, 4], "col2": [2, 5], "col3": [3, 6]})

    # Run the function and save the output
    df = common.read_csv(mock_zip_file, "file1.csv")

    # Test that the output is as expected
    pd.testing.assert_frame_equal(df, expected_df)


def test_read_csv_file_not_found(mock_zip_file):
    """Test read_csv when the file is not found"""

    with pytest.raises(FileNotFoundError, match="Could not find file: file2.csv"):
        common.read_csv(mock_zip_file, "file2.csv")
