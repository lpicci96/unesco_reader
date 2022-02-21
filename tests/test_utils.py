"""tests for utils.py"""


import pytest
from unesco_reader import utils, api


#valid codes
code = api.datasets()['code'].values[0]
url = api.datasets()['link'].values[0]
file_name = f"{code}_LABEL.csv"

#invalid codes
invalid_url = 'invalid_url'
invalid_file_name = 'invalid_file_name'


def test_read_zip():
    df = utils.read_zip(url, file_name)
    assert len(df)>0
    
    #test correct url with wrong file name
    with pytest.raises(ValueError) as exception_info:
        utils.read_zip(url, invalid_file_name)
        assert exception_info.match(f"{invalid_file_name} is not found in the zipped folder")
        
   