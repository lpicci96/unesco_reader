"""Tests for `uis` module."""

import pytest
from unesco_reader import uis
from unesco_reader.config import PATHS
import pandas as pd


def test_format_metadata():
    """Test format_metadata"""

    expected_df = pd.read_csv(
        PATHS.TEST_FILES / "formatted_metadata.csv", low_memory=False
    )
    metadata = pd.read_csv(PATHS.TEST_FILES / "unformatted_metadata.csv")
    result_df = uis.format_metadata(metadata)

    pd.testing.assert_frame_equal(result_df, expected_df)
