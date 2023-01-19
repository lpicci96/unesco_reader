"""Tests for `common` module."""


from unesco_reader.common import *
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from zipfile import ZipFile



def test_mapping_dict():
    """Test mapping_dict"""

    test_df = pd.DataFrame({"left": [1, 2, 3], "right": ["a", "b", "c"]})

    # test default
    result = mapping_dict(test_df)
    expected = {1: "a", 2: "b", 3: "c"}
    assert result == expected

    # test key_col = "right"
    result = mapping_dict(test_df, key_col="right")
    expected = {"a": 1, "b": 2, "c": 3}
    assert result == expected

    # test key_col is not left or right
    with pytest.raises(ValueError, match="Invalid key_col. Please choose from"):
        mapping_dict(test_df, key_col="invalid_key_col")

    # test df has more than 2 columns
    invalid_df = pd.DataFrame({"left": [1, 2, 3],
                               "right": ["a", "b", "c"],
                               "additional": [True, False, True]})
    with pytest.raises(ValueError, match="df can only contain 2 columns"):
        mapping_dict(invalid_df)


def test_make_request():
    """Test make_request"""

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {'content-type': 'application/x-zip-compressed'}
        assert make_request('http://test.com') == mock_get.return_value


def test_make_request_bad_status():
    """Test make_request when the response status is not 200"""

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        with pytest.raises(ConnectionError, match='Could not connect to http://test.com'):
            make_request('http://test.com')


def test_make_request_not_zip():
    """Test make_request when the response is not a zip file"""

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {'content-type': 'application/pdf'}
        with pytest.raises(ValueError, match='The file is not a zip file'):
            make_request('http://test.com')


def test_unzip():
    """ """

    # create a mock file-like object
    mock_zip = io.BytesIO()
    with ZipFile(mock_zip, 'w') as zf:
        zf.writestr('test.txt', 'This is a test file')

    assert isinstance(unzip(mock_zip), ZipFile)


def test_unzip_exceptions():
    """Test unzip exceptions"""

    # test file not found
    with pytest.raises(FileNotFoundError, match='Could not find file'):
        unzip('non_existent_file.zip')

    # test bad zip file
    mock_zip = io.BytesIO(b'invalid zip data')
    with pytest.raises(ValueError, match='The file could not be unzipped'):
        unzip(mock_zip)


def test_read_csv():
    """Test read_csv"""

    expected_df = pd.DataFrame({'col1': [1, 4], 'col2': [2, 5], 'col3': [3, 6]})

    # create a mock file-like object
    mock_zip = MagicMock()
    mock_zip.namelist.return_value = ['file1.csv']
    mock_file = io.StringIO("col1,col2,col3\n1,2,3\n4,5,6")
    mock_zip.open.return_value = mock_file

    # Run the function and save the output
    df = read_csv(mock_zip, 'file1.csv')

    # Test that the output is as expected
    pd.testing.assert_frame_equal(df, expected_df)

def test_read_csv_file_not_found():
    """Test read_csv when the file is not found"""

    mock_zip = MagicMock()
    mock_zip.namelist.return_value = ['file1.csv']

    with pytest.raises(FileNotFoundError, match='Could not find file: file2.csv'):
        read_csv(mock_zip, 'file2.csv')








