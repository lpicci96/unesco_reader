"""Tests for formatting module."""

import pandas as pd
import numpy as np
import zipfile
import pytest
import io

from unesco_reader import formatting


TEST_DATASET_CODE = "SDG"


def test_cols_to_lower():
    """Test cols_to_lower"""

    # Test with all caps
    test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    formatting.cols_to_lower(test_df)
    assert list(test_df.columns) == ["a", "b"]

    # Test with mixed case
    test_df = pd.DataFrame({"A": [1, 2, 3], "b": [4, 5, 6]})
    formatting.cols_to_lower(test_df)
    assert list(test_df.columns) == ["a", "b"]

    # Test with all lowercase
    test_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    formatting.cols_to_lower(test_df)
    assert list(test_df.columns) == ["a", "b"]

    # test with inplace=False
    test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    result_df = formatting.cols_to_lower(test_df, inplace=False)
    assert list(test_df.columns) == ["A", "B"]
    assert list(result_df.columns) == ["a", "b"]


def test_remove_en_suffix():
    """Test remove_en_suffix"""

    # Test with one column
    test_df = pd.DataFrame({"a_en": [1, 2, 3]})
    formatting.remove_en_suffix(test_df)
    assert list(test_df.columns) == ["a"]

    # Test with mixed columns
    test_df = pd.DataFrame({"b_en": [1, 2, 3], "c": [4, 5, 6]})
    formatting.remove_en_suffix(test_df)
    assert list(test_df.columns) == ["b", "c"]

    # Test with mixed case
    test_df = pd.DataFrame({"D_EN": [1, 2, 3], "e_en": [4, 5, 6]})
    formatting.remove_en_suffix(test_df)
    assert list(test_df.columns) == ["D", "e"]

    # Test with inplace=False
    test_df = pd.DataFrame({"f_en": [1, 2, 3]})
    result_df = formatting.remove_en_suffix(test_df, inplace=False)
    assert list(test_df.columns) == ["f_en"]
    assert list(result_df.columns) == ["f"]

    # Test when _en is not at the end
    test_df = pd.DataFrame({"g_en_f": [1, 2, 3]})
    formatting.remove_en_suffix(test_df)
    assert list(test_df.columns) == ["g_en_f"]


def test_squash_duplicates():
    """"""

    df = pd.DataFrame(
        {
            "country": ["AFG", "AFG", "AFG", "IND"],
            "type": ["source", "source", "value type", "source"],
            "metadata": ["UIS", "WB", "estimate", "UIS"],
        }
    )
    result_df = formatting.squash_duplicates(df, ["country", "type"], "metadata")

    expected_df = pd.DataFrame(
        {
            "country": ["AFG", "IND", "AFG"],
            "type": ["value type", "source", "source"],
            "metadata": ["estimate", "UIS", "UIS / WB"],
        }
    )

    pd.testing.assert_frame_equal(result_df, expected_df)


class TestUISData:
    """Tests for the UISData class"""

    @pytest.fixture
    def uis_data(self):
        # Simulate a zip file in memory
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr(
                f"{TEST_DATASET_CODE}_COUNTRY.csv",
                "country_id,country_name\n1,Test Country",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_README_SOME_RELEASE.md",
                "#This is a test README file.",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_REGION.csv",
                "region_id,country_id,country_name_en\nWB:Test Region (code: 1),1,Test Country",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_DATA_NATIONAL.csv",
                "indicator_id,country_id,year,value,magnitude,qualifier\nind1,1,2020,10,,",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_DATA_REGIONAL.csv",
                "indicator_id,region_id,year,value,magnitude,qualifier\nind1,WB:Test Region (code: 1),2020,10,,",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_LABEL.csv",
                "indicator_id,indicator_label_en\nind1,Test Indicator",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_METADATA.csv",
                "indicator_id,country_id,year,type,metadata\nind1,1,2020,Source,UIS\nind1,1,2020,Source,WB\nind1,1,2020,value type,estimate\nind1,2,2020,Source,UIS",
            )

        in_memory_zip.seek(0)  # Reset file pointer to the beginning
        folder = zipfile.ZipFile(in_memory_zip, "r")
        return formatting.UISData(folder)

    @pytest.fixture
    def uis_data_no_region(self):
        # Simulate a zip file in memory
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr(
                f"{TEST_DATASET_CODE}_COUNTRY.csv",
                "COUNTRY_ID,country_name\n1,Test Country",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_README_SOME_RELEASE.md",
                "#This is a test README file.",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_DATA_NATIONAL.csv",
                "INDICATOR_ID,country_id,year,value,magnitude,qualifier\nind1,1,2020,10,,",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_LABEL.csv",
                "INDICATOR_ID,INDICATOR_LABEL_EN\nind1,Test Indicator",
            )
            zf.writestr(
                f"{TEST_DATASET_CODE}_METADATA.csv",
                "INDICATOR_ID,country_id,year,type,metadata\nind1,1,2020,Source,This is test metadata",
            )

        in_memory_zip.seek(0)  # Reset file pointer to the beginning
        folder = zipfile.ZipFile(in_memory_zip, "r")
        return formatting.UISData(folder)

    @pytest.fixture
    def uis_data_missing_files(self):
        """Simulate a situation where all expected files are missing in the zip file"""

        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr(f"{TEST_DATASET_CODE}_UNEXPECTED.txt", "Unexpected file")

        in_memory_zip.seek(0)  # Reset file pointer to the beginning
        folder = zipfile.ZipFile(in_memory_zip, "r")
        return folder

    @pytest.fixture
    def uis_data_missing_only_readme_present(self):
        """Simulate a situation where only the readme is present in the zip file
        Intended to test that some attributes will be None rather than causing an error to be raised.
        """

        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr(
                f"{TEST_DATASET_CODE}_README_SOME_RELEASE.md",
                "#This is a test README file.",
            )

        in_memory_zip.seek(0)  # Reset file pointer to the beginning
        folder = zipfile.ZipFile(in_memory_zip, "r")
        return formatting.UISData(folder)

    @pytest.fixture
    def uis_data_missing_only_country_data_present(self):
        """Simulate a situation where only the country data is present in the zip file
        Intended to test that some attributes will be None rather than causing an error to be raised.
        """

        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr(
                f"{TEST_DATASET_CODE}_COUNTRY.csv",
                "COUNTRY_ID,country_name\n1,Test Country",
            )

        in_memory_zip.seek(0)
        in_memory_zip.seek(0)  # Reset file pointer to the beginning
        folder = zipfile.ZipFile(in_memory_zip, "r")
        return formatting.UISData(folder)

    @pytest.fixture
    def uis_data_multiple_codes(self):
        """Simulate a situation in which UIS made mistakes packaging the zip file
        by including files from multiple datasets in the same zip file.
        """
        # Simulate a zip file in memory
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr(f"{TEST_DATASET_CODE}_UNEXPECTED.txt", "Unexpected file")
            zf.writestr(f"INVALIDCODE_Other_file.txt", "File with invalid code")

        in_memory_zip.seek(0)  # Reset file pointer to the beginning
        folder = zipfile.ZipFile(in_memory_zip, "r")
        return folder

    def test_add_variable_names(self, uis_data):
        """Test add_variable_names"""

        df = pd.DataFrame(
            {"indicator_id": ["ind1"], "indicator_label": ["Test Indicator"]}
        )
        test_df = pd.DataFrame({"indicator_id": ["ind1"]})
        uis_data.add_variable_names(test_df)
        pd.testing.assert_frame_equal(test_df, df)

    def test_add_country_names(self, uis_data):
        """Test add_country_names"""

        df = pd.DataFrame({"country_id": [1], "country_name": ["Test Country"]})
        test_df = pd.DataFrame({"country_id": [1]})
        uis_data.add_country_names(test_df)
        pd.testing.assert_frame_equal(test_df, df)

    def test_get_dataset_code(self, uis_data):
        """Test get_dataset_code"""
        expected_code = TEST_DATASET_CODE
        assert uis_data.get_dataset_code() == expected_code

    def test_get_dataset_code_multiple_codes(self, uis_data_multiple_codes):
        """Test get_dataset_code when there are multiple codes"""
        try:
            uis_data = formatting.UISData(uis_data_multiple_codes)
        except ValueError as e:
            assert str(e) == "Multiple dataset codes in folder"

    def test_get_file_names(self, uis_data):
        """Test get_file_names when all files are present"""
        expected_files = {
            "COUNTRY_CONCORDANCE": f"{TEST_DATASET_CODE}_COUNTRY.csv",
            "REGION_CONCORDANCE": f"{TEST_DATASET_CODE}_REGION.csv",
            "COUNTRY_DATA": f"{TEST_DATASET_CODE}_DATA_NATIONAL.csv",
            "REGION_DATA": f"{TEST_DATASET_CODE}_DATA_REGIONAL.csv",
            "VARIABLE_CONCORDANCE": f"{TEST_DATASET_CODE}_LABEL.csv",
            "METADATA": f"{TEST_DATASET_CODE}_METADATA.csv",
            "README": f"{TEST_DATASET_CODE}_README_SOME_RELEASE.md",
        }
        assert uis_data.get_file_names() == expected_files

    def test_get_file_names_missing_files(self, uis_data_missing_files):
        """Test get_file_names when all files are missing raises an error"""

        with pytest.raises(FileNotFoundError):
            obj = formatting.UISData(uis_data_missing_files)

    def test_get_file_names_no_region(self, uis_data_no_region):
        """Test get_file_names when the regional data is not present"""

        expected_files = {
            "COUNTRY_CONCORDANCE": f"{TEST_DATASET_CODE}_COUNTRY.csv",
            "COUNTRY_DATA": f"{TEST_DATASET_CODE}_DATA_NATIONAL.csv",
            "VARIABLE_CONCORDANCE": f"{TEST_DATASET_CODE}_LABEL.csv",
            "METADATA": f"{TEST_DATASET_CODE}_METADATA.csv",
            "README": f"{TEST_DATASET_CODE}_README_SOME_RELEASE.md",
        }
        assert uis_data_no_region.get_file_names() == expected_files

    def test_readme(self, uis_data):
        """Test the readme property when the file is present"""

        expected_readme = "#This is a test README file."
        assert uis_data.readme == expected_readme

    def test_readme_missing_file(self, uis_data_missing_only_country_data_present):
        """Test the readme property when the file is missing"""
        assert uis_data_missing_only_country_data_present.readme is None

    def test_country_concordance(self, uis_data):
        """Test the country_concordance property when the file is present"""

        expected_df = pd.DataFrame(
            {"country_id": [1], "country_name": ["Test Country"]}
        )
        assert uis_data.country_concordance.equals(expected_df)

    def test_country_concordance_missing_file(
        self, uis_data_missing_only_readme_present
    ):
        """Test the country_concordance property when the file is missing"""
        assert uis_data_missing_only_readme_present.country_concordance is None

    def test_region_concordance(self, uis_data):
        """Test the region_concordance property when the file is present"""

        expected_df = pd.DataFrame(
            {
                "region_id": ["WB:Test Region (code: 1)"],
                "country_id": [1],
                "country_name": ["Test Country"],
            }
        )
        expected_df[["grouping_entity", "region_name"]] = expected_df[
            "region_id"
        ].str.split(": ", n=1, expand=True)

        pd.testing.assert_frame_equal(
            uis_data.region_concordance, expected_df, check_dtype=False
        )

    def test_region_concordance_missing_file(
        self, uis_data_missing_only_readme_present
    ):
        """Test the region_concordance property when the file is missing"""
        assert uis_data_missing_only_readme_present.region_concordance is None

    def test_variable_concordance(self, uis_data):
        """Test the variable_concordance property when the file is present"""

        expected_df = pd.DataFrame(
            {"indicator_id": ["ind1"], "indicator_label": ["Test Indicator"]}
        )
        assert uis_data.variable_concordance.equals(expected_df)

    def test_variable_concordance_missing_file(
        self, uis_data_missing_only_readme_present
    ):
        """Test the variable_concordance property when the file is missing"""
        assert uis_data_missing_only_readme_present.variable_concordance is None

    def test_metadata(self, uis_data):
        """Test the metadata property when the file is present"""

        expected_df = pd.DataFrame(
            {
                "indicator_id": ["ind1", "ind1", "ind1"],
                "country_id": [1, 2, 1],
                "year": [2020, 2020, 2020],
                "type": ["value type", "Source", "Source"],
                "metadata": ["estimate", "UIS", "UIS / WB"],
                "indicator_label": [
                    "Test Indicator",
                    "Test Indicator",
                    "Test Indicator",
                ],
                "country_name": ["Test Country", np.nan, "Test Country"],
            }
        )
        assert uis_data.metadata.equals(expected_df)

    def test_metadata_missing_file(self, uis_data_missing_only_readme_present):
        """Test the metadata property when the file is missing"""
        assert uis_data_missing_only_readme_present.metadata is None

    def test_country_data(self, uis_data):
        """Test the country_data property when the file is present"""

        expected_df = pd.DataFrame(
            {
                "indicator_id": ["ind1"],
                "country_id": [1],
                "year": [2020],
                "value": [10],
                "magnitude": [np.nan],
                "qualifier": [np.nan],
                "indicator_label": ["Test Indicator"],
                "country_name": ["Test Country"],
                "Source": ["UIS / WB"],
                "value type": ["estimate"],
            }
        )
        pd.testing.assert_frame_equal(uis_data.country_data, expected_df)

    def test_country_data_missing_file(self, uis_data_missing_only_readme_present):
        """Test the country_data property when the file is missing"""
        assert uis_data_missing_only_readme_present.country_data is None

    def test_region_data(self, uis_data):
        """Test the region_data property when the file is present"""

        expected_df = pd.DataFrame(
            {
                "indicator_id": ["ind1"],
                "region_id": ["WB:Test Region (code: 1)"],
                "year": [2020],
                "value": [10],
                "magnitude": [np.nan],
                "qualifier": [np.nan],
                "indicator_label": ["Test Indicator"],
            }
        )
        pd.testing.assert_frame_equal(uis_data.region_data, expected_df)

    def test_region_data_missing_file(self, uis_data_missing_only_readme_present):
        """Test the region_data property when the file is missing"""
        assert uis_data_missing_only_readme_present.region_data is None
