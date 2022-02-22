"""tests for api.py"""


import pytest
from unesco_reader import api
import pandas as pd


test_dataset = "SDG"  # SDG dataset
test_indicator = "LR.AG15T99"  # adult literacy
errors = {
    "dataset_code": "invalid_dataset",
    "indicator_code": "invalid_indicator",
    "grouping": "invalid_grouping",
}


def __loop_datasets(func, *args, **kwargs):
    """
    Loops all datasets through a function
    and checks that the output is not None and >0
    """

    ds = api.datasets()
    if "REGIONAL" in kwargs.values():
        ds = ds[ds.regional]

    dataset_list = list(ds.code)
    for code in dataset_list:
        result = func(dataset_code=code, *args, **kwargs)
        assert result is not None
        assert len(result) > 0


def test_datasets():
    ds = api.datasets()
    assert isinstance(ds, pd.core.frame.DataFrame)
    assert ds is not None
    assert len(ds) > 0


def test_indicators():
    __loop_datasets(func=api.indicators)

    with pytest.raises(ValueError) as exception_info:
        api.indicators(errors["dataset_code"])
        assert exception_info.match(f"{errors['dataset_code']} is not a valid code.")


def test_get_bulk():
    __loop_datasets(func=api.get_bulk)
    __loop_datasets(func=api.get_bulk, grouping="REGIONAL")

    with pytest.raises(ValueError) as exception_info:
        api.get_bulk(dataset_code=errors["dataset_code"])  # invalid dataset code
        assert exception_info.match(f"{errors['dataset_code']} is not a valid code.")
    with pytest.raises(ValueError) as exception_info:
        api.get_bulk(
            dataset_code=test_dataset, grouping=errors["grouping"]
        )  # invalid grouping
        assert exception_info.match(f"{errors['grouping']} is not a valid grouping.")


def test_get_indicator():
    df = api.get_indicator(test_indicator, test_dataset)
    assert len(df) > 0
