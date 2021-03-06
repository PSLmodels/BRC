"""
Test Policy class.
"""
import os
import numpy
import pandas
import pytest
import taxcalc as itax
from biztax import Policy, Data, START_YEAR, END_YEAR, NUM_YEARS


def test_policy_json_content():
    """
    Test contents of policy_current_law.json file
    """
    policy = Policy()
    start_year = policy.start_year
    assert start_year == START_YEAR
    policy_vals = getattr(policy, '_vals')
    for _, data in policy_vals.items():
        value_yrs = data.get('value_yrs')
        assert isinstance(value_yrs, list)
        value = data.get('value')
        expected_value_yrs = [(start_year + i) for i in range(len(value))]
        if value_yrs != expected_value_yrs:
            msg = 'name,value_yrs,expected_value_yrs: {}\n{}\n{}'
            raise ValueError(msg.format(data.get('name')), value_yrs,
                             expected_value_yrs)


def test_implement_reform():
    """
    Test (in)correct use of implement_reform method
    """
    policy = Policy()
    # incorrect uses of implement_reform
    with pytest.raises(ValueError):
        policy.implement_reform(list())
    with pytest.raises(ValueError):
        policy.implement_reform({'tau_c': {2099: 0.20}})
    policy.set_year(2019)
    with pytest.raises(ValueError):
        policy.implement_reform({'tau_c': {2018: 0.20}})
    with pytest.raises(ValueError):
        policy.implement_reform({'tau_c': {2020: -0.2}})
    with pytest.raises(ValueError):
        policy.implement_reform({'inventory_method': {2020: 'XIFO'}})
    del policy
    # correct use of implement_reform
    policy = Policy()
    reform = {
        'tau_c': {2021: 0.20},
        'inventory_method': {2021: 'FIFO'},
        'newIntPaid_corp_hcyear': {2021: 2018}
    }
    policy.implement_reform(reform)
    policy.set_year(2020)
    assert policy.tau_c > 0.20
    assert policy.inventory_method == 'Mix'
    assert policy.newIntPaid_corp_hcyear == 0
    policy.set_year(2021)
    assert policy.tau_c == 0.20
    assert policy.inventory_method == 'FIFO'
    assert policy.newIntPaid_corp_hcyear == 2018
    policy.set_year(2022)
    assert policy.tau_c == 0.20
    assert policy.inventory_method == 'FIFO'
    assert policy.newIntPaid_corp_hcyear == 2018


def test_parameters_dataframe():
    """
    Test parameters_dataframe() method
    """
    policy = Policy()
    ppdf = policy.parameters_dataframe()
    assert isinstance(ppdf, pandas.DataFrame)
    assert len(ppdf.index) == NUM_YEARS
    assert ppdf['year'][0] == START_YEAR
    assert ppdf['year'][NUM_YEARS - 1] == END_YEAR
    assert ppdf['tau_c'][START_YEAR - START_YEAR] == 0.347
    with pytest.raises(KeyError):
        ppdf['tau_c'][-1]
    with pytest.raises(KeyError):
        ppdf['tau_c'][END_YEAR - START_YEAR + 1]
    with pytest.raises(KeyError):
        ppdf['tau_c'][START_YEAR]
    with pytest.raises(KeyError):
        ppdf['unknown_parameter'][0]
