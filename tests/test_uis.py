"""Tests for `uis` module."""

import pytest
from unesco_reader import uis
import pandas as pd


def test_mapping_dict():
    """Test mapping_dict function."""

    mock_df = pd.DataFrame({'COUNTRY_ID': {0: 'AFG',
                                           1: 'ALB',
                                           2: 'DZA',
                                           3: 'ASM',
                                           4: 'AND',
                                           5: 'AGO',
                                           6: 'AIA',
                                           7: 'ATG',
                                           8: 'ARG',
                                           9: 'ARM'},
                            'COUNTRY_NAME_EN': {0: 'Afghanistan',
                                                1: 'Albania',
                                                2: 'Algeria',
                                                3: 'American Samoa',
                                                4: 'Andorra',
                                                5: 'Angola',
                                                6: 'Anguilla',
                                                7: 'Antigua and Barbuda',
                                                8: 'Argentina',
                                                9: 'Armenia'}})

    result_dict = uis.mapping_dict(mock_df)
    assert result_dict == {'AFG': 'Afghanistan',
                           'ALB': 'Albania',
                           'DZA': 'Algeria',
                           'ASM': 'American Samoa',
                           'AND': 'Andorra',
                           'AGO': 'Angola',
                           'AIA': 'Anguilla',
                           'ATG': 'Antigua and Barbuda',
                           'ARG': 'Argentina',
                           'ARM': 'Armenia'}
    result_dict_rev = uis.mapping_dict(mock_df, key_col='right')
    assert result_dict_rev == {'Afghanistan': 'AFG',
                               'Albania': 'ALB',
                               'Algeria': 'DZA',
                               'American Samoa': 'ASM',
                               'Andorra': 'AND',
                               'Angola': 'AGO',
                               'Anguilla': 'AIA',
                               'Antigua and Barbuda': 'ATG',
                               'Argentina': 'ARG',
                               'Armenia': 'ARM'}

    with pytest.raises(ValueError) as err:
        uis.mapping_dict(mock_df, 'invalid_key_col')
    assert str(err.value) == 'Invalid key_col. Please choose from ["left", "right"]'

    with pytest.raises(ValueError) as err:
        uis.mapping_dict(mock_df.assign(new_col = 'invalid column value'))
    assert str(err.value) == 'df can only contain 2 columns'



def test_format_metadata():
    """Test format_metadata"""

    test_df = pd.DataFrame.from_records([{'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2015,
                                          'TYPE': 'Source',
                                          'METADATA': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/budget_citoyen_2015.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/depenses_du_budget_general_volume_1.pdf,Access date:05/21/2021;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2017,
                                          'TYPE': 'Source',
                                          'METADATA': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc-fr-2017.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/tome1_fr.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2018,
                                          'TYPE': 'Source',
                                          'METADATA': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc_2018-fr-loi.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/tome1_fr_1.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2019,
                                          'TYPE': 'Source',
                                          'METADATA': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc_vfr_lf_2019_0.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/morasse_fr_tome110042019.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2020,
                                          'TYPE': 'Source',
                                          'METADATA': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc-fr.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/tome1_fr_0.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2008,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2009,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2010,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2011,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2012,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2013,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2014,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2015,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2016,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2017,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2018,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'},
                                         {'INDICATOR_ID': 'XGDP.FSGOV',
                                          'COUNTRY_ID': 'MAR',
                                          'YEAR': 2019,
                                          'TYPE': 'Source',
                                          'METADATA': 'IMF'}])


    formatted_metadata = uis.format_metadata(test_df)

    expected_df = pd.DataFrame.from_records([{'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2008,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2009,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2010,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2011,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2012,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2013,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2014,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2015,
                                              'Source': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/budget_citoyen_2015.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/depenses_du_budget_general_volume_1.pdf,Access date:05/21/2021;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know / IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2016,
                                              'Source': 'IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2017,
                                              'Source': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc-fr-2017.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/tome1_fr.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know / IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2018,
                                              'Source': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc_2018-fr-loi.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/tome1_fr_1.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know / IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2019,
                                              'Source': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc_vfr_lf_2019_0.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/morasse_fr_tome110042019.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know / IMF'},
                                             {'INDICATOR_ID': 'XGDP.FSGOV',
                                              'COUNTRY_ID': 'MAR',
                                              'YEAR': 2020,
                                              'Source': 'Type of data:Revised estimates / Budget;Source.1:Citizen Budget,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/bc-fr.pdf,Access date:05/21/2021;Source.2:Finance Law for the Budget Year,Ministry of Economy and Finance,http://lof.finances.gov.ma/sites/default/files/budget/files/tome1_fr_0.pdf,Access date:05/21/2021;GovExp.IncludeDebt:Yes;GovExpEd.CoverCentral:Yes;GovExpEd.CoverRegional:Do not know;GovExpEd.CoverLocal:Do not know;GovExpEd.CoverPub&Priv:Do not know'}])

    pd.testing.assert_frame_equal(formatted_metadata, expected_df)




