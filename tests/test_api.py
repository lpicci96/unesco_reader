"""tests for api.py"""


import pytest
from unesco_reader import api
import pandas as pd


test_dataset = 'SDR'
test_indicator = ''
errors = {'dataset_code': 'not_a_dataset',
          'indicator_code': 'not_an_indicator',
          'grouping': 'not_a_grouping'}

def __loop_datasets(func, *args, **kwargs):
    """
    Loops all datasets through a function 
    and checks that the output is not None and >0 
    """
    
    ds = api.datasets()
    if 'REGIONAL' in kwargs.values():
        ds = ds[ds.regional]
    
    dataset_list = list(ds.code)
    for code in dataset_list:
        result = func(dataset_code=code, *args, **kwargs)
        assert result is not None
        assert len(result)>0
    


def test_datasets():
    ds = api.datasets()
    assert isinstance(ds, pd.core.frame.DataFrame)
    assert ds is not None
    assert len(ds)>0


def test_indicators():
    
    not_a_dataset = 'not_a_real_dataset'
    __loop_datasets(func = api.indicators)
    
    
    with pytest.raises(ValueError):
        indicator_df = api.indicators(not_a_dataset)
        

def test_get_bulk():
    
    
    #__loop_datasets(func=api.get_bulk)
    __loop_datasets(func=api.get_bulk, grouping='REGIONAL')
    
    
    
    
    
    
    
    
    
    
    
    
    