"""Tests for the scraper module."""

from unesco_reader import scraper
import pytest
import requests
from unittest.mock import patch
from bs4 import BeautifulSoup
import zipfile
import io

TEST_URL = "https://test.com"


def test_make_request():
    """Test that make_request returns a response object."""

    # test successful request
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        response = scraper.make_request(TEST_URL)
        assert response == mock_get.return_value

    # test failed request
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException
        with pytest.raises(ConnectionError, match="Could not connect to"):
            scraper.make_request(TEST_URL)


class TestLinkScraper:
    """Tests for the LinkScraper class."""
    def test_get_soup(self):
        """Test get_soup"""

        # test successful return
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"<html></html>"
            soup = scraper.LinkScraper.get_soup()
            assert str(soup) == "<html></html>"

        # test failed request
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            with pytest.raises(ConnectionError, match="Could not connect to"):
                scraper.LinkScraper.get_soup()

    def test_parse_link_section(self):
        """Test parse_link_section"""

        # test data link exists
        link_section = BeautifulSoup('<li><a href="test.zip">Test Data - last update: January 2022</a></li>', 'html.parser')
        result = scraper.LinkScraper.parse_link_section(link_section)
        expected = {'name': 'Test Data', 'latest_update': 'January 2022', 'href': 'test.zip'}
        assert result == expected

        # test no link exists
        link_section = BeautifulSoup('<li>No link here</li>', 'html.parser')
        result = scraper.LinkScraper.parse_link_section(link_section)
        assert result is None

    def test_parse_link_text(self):
        """Test parse_link_text"""

        # test with date in (last update: <date>) format
        link_text = "Test Data (last update: January 2024)"
        result = scraper.LinkScraper.parse_link_text(link_text)
        expected = ('Test Data', 'January 2024')
        assert result == expected

        # test with date in - <date> format
        link_text = "Test Data - February 2024"
        result = scraper.LinkScraper.parse_link_text(link_text)
        expected = ('Test Data', 'February 2024')
        assert result == expected

        # test with date in <date> format
        link_text = "Test Data March 2024"
        result = scraper.LinkScraper.parse_link_text(link_text)
        expected = ('Test Data', 'March 2024')
        assert result == expected

        # test with no date
        link_text = "Test Data"
        result = scraper.LinkScraper.parse_link_text(link_text)
        expected = ('Test Data', None)
        assert result == expected

        # test with "-" in name
        link_text = "Test - Data - April 2024"
        result = scraper.LinkScraper.parse_link_text(link_text)
        expected = ('Test - Data', "April 2024")
        assert result == expected

        # test with "()" in name
        link_text = "Test (Data) (last update: May 2024)"
        result = scraper.LinkScraper.parse_link_text(link_text)
        expected = ('Test (Data)', "May 2024")
        assert result == expected

    def test_get_links(self):
        """Test get_links"""
        with patch.object(scraper.LinkScraper, 'get_soup') as mock_get_soup:
            mock_get_soup.return_value = BeautifulSoup(
                ('<section> <h2>Education</h2><ul><li><strong>Test Data - last update: January 2022</strong><a '
                 'href="test.zip"><img></a></li></ul></section>'),
                'html.parser')
            result = scraper.LinkScraper.get_links()
            expected = [{'theme': 'Education', 'name': 'Test Data', 'latest_update': 'January 2022', 'href': 'test.zip'}]
            assert result == expected


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
        result = scraper.get_zipfile(TEST_URL)
        assert isinstance(result, zipfile.ZipFile)

    # test failed request (not a zip file)
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "text/html"}
        mock_get.return_value.content = b"<html></html>"
        with pytest.raises(ValueError, match="The file is not an accepted zip file"):
            scraper.get_zipfile(TEST_URL)


