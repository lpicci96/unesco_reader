"""Tests for the read module."""

from unesco_reader import read
import pytest
import requests
from unittest.mock import patch
from bs4 import BeautifulSoup
import zipfile
import io
import pandas as pd
import os

TEST_URL = "https://test.com"


def test_make_request():
    """Test that make_request returns a response object."""

    # test successful request
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        response = read.make_request(TEST_URL)
        assert response == mock_get.return_value

    # test failed request
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException
        with pytest.raises(ConnectionError, match="Could not connect to"):
            read.make_request(TEST_URL)


class TestUISInfoScraper:
    """Tests for the UISInfoScraper class."""
    def test_get_soup(self):
        """Test get_soup"""

        # test successful return
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"<html></html>"
            soup = read.UISInfoScraper.get_soup()
            assert str(soup) == "<html></html>"

        # test failed request
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            with pytest.raises(ConnectionError, match="Could not connect to"):
                read.UISInfoScraper.get_soup()

    def test_parse_link_section(self):
        """Test parse_link_section"""

        # test data link exists
        link_section = BeautifulSoup('<li><a href="test.zip">Test Data - last update: January 2022</a></li>', 'html.parser')
        result = read.UISInfoScraper.parse_link_section(link_section)
        expected = {'name': 'Test Data', 'latest_update': 'January 2022', 'href': 'test.zip'}
        assert result == expected

        # test no link exists
        link_section = BeautifulSoup('<li>No link here</li>', 'html.parser')
        result = read.UISInfoScraper.parse_link_section(link_section)
        assert result is None

    def test_parse_link_text(self):
        """Test parse_link_text"""

        # test with date in (last update: <date>) format
        link_text = "Test Data (last update: January 2024)"
        result = read.UISInfoScraper.parse_link_text(link_text)
        expected = ('Test Data', 'January 2024')
        assert result == expected

        # test with date in - <date> format
        link_text = "Test Data - February 2024"
        result = read.UISInfoScraper.parse_link_text(link_text)
        expected = ('Test Data', 'February 2024')
        assert result == expected

        # test with date in <date> format
        link_text = "Test Data March 2024"
        result = read.UISInfoScraper.parse_link_text(link_text)
        expected = ('Test Data', 'March 2024')
        assert result == expected

        # test with no date
        link_text = "Test Data"
        result = read.UISInfoScraper.parse_link_text(link_text)
        expected = ('Test Data', None)
        assert result == expected

        # test with "-" in name
        link_text = "Test - Data - April 2024"
        result = read.UISInfoScraper.parse_link_text(link_text)
        expected = ('Test - Data', "April 2024")
        assert result == expected

        # test with "()" in name
        link_text = "Test (Data) (last update: May 2024)"
        result = read.UISInfoScraper.parse_link_text(link_text)
        expected = ('Test (Data)', "May 2024")
        assert result == expected

    def test_get_links(self):
        """Test get_links"""
        with patch.object(read.UISInfoScraper, 'get_soup') as mock_get_soup:#, \
             #patch.object(read.LinkScraper.get_links, 'cache_clear') as mock_cache_clear:

            mock_get_soup.return_value = BeautifulSoup(
                ('<section> <h2>Education</h2><ul><li><strong>Test Data - last update: January 2022</strong><a '
                 'href="test.zip"><img></a></li></ul></section>'),
                'html.parser')

            # Test with refresh=False (default)
            result = read.UISInfoScraper.get_links()
            expected = [{'theme': 'Education', 'name': 'Test Data', 'latest_update': 'January 2022', 'href': 'test.zip'}]
            assert result == expected
            #mock_cache_clear.assert_not_called()

            # result = read.LinkScraper.get_links(refresh=True)
            # assert result == expected
            # mock_cache_clear.assert_called_once()


def test_get_zipfile():
    """Test get_zipfile function."""

    # Create a valid zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('test.txt', 'This is a test file')
    zip_content = zip_buffer.getvalue()

    # test successful request
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "application/zip"}
        mock_get.return_value.content = zip_content
        result = read.get_zipfile(TEST_URL)
        assert isinstance(result, zipfile.ZipFile)

    # test failed request (not a zip file)
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "text/html"}
        mock_get.return_value.content = b"<html></html>"
        with pytest.raises(ValueError, match="The file is not an accepted zip file"):
            read.get_zipfile(TEST_URL)


def test_read_csv(tmp_path):
    """Test the read_csv function."""

    # Create a DataFrame
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

    # Create a temporary CSV file
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False)

    # Create a temporary zip file and add the CSV file to it
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(csv_path, arcname=os.path.basename(csv_path))

    # Use the read_csv function to read the CSV file from the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        result = read.read_csv(zip_file, "test.csv")

    # Check that the result is a DataFrame with the correct data
    pd.testing.assert_frame_equal(result, df)

    # test file not found
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        with pytest.raises(FileNotFoundError, match="Could not find file: invalid.csv"):
            read.read_csv(zip_file, "invalid.csv")


def test_read_md(tmp_path):
    """Test the read_md function."""

    # Create a markdown string
    md_content = "# This is a test markdown file"

    # Create a temporary markdown file
    md_path = tmp_path / "test.md"
    with open(md_path, 'w') as f:
        f.write(md_content)

    # Create a temporary zip file and add the markdown file to it
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(md_path, arcname=os.path.basename(md_path))

    # Use the read_md function to read the markdown file from the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        result = read.read_md(zip_file, "test.md")

    # Check that the result is a string with the correct content
    assert result == md_content

    # test file not found
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        with pytest.raises(FileNotFoundError, match="Could not find file: invalid.md"):
            read.read_md(zip_file, "invalid.md")

