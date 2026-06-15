import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from preprocessing.missing_value_handler import MissingValueHandler

@pytest.mark.UT_missing_value_handler
def test_impute_numerical():
    """
    Tag: UT_missing_value_handler
    Purpose: Verify numeric imputation strategies (mean, median).
    """
    df = pd.DataFrame({'age': [20, np.nan, 40]})
    handler = MissingValueHandler(df)
    
    res_mean = handler.impute_numerical(strategy='mean')
    assert res_mean['age'][1] == 30.0

    handler2 = MissingValueHandler(df)
    res_median = handler2.impute_numerical(strategy='median')
    assert res_median['age'][1] == 30.0

@pytest.mark.UT_missing_value_handler
def test_impute_time_series():
    """
    Tag: UT_missing_value_handler
    Purpose: Verify forward fill time series imputation.
    """
    df = pd.DataFrame({'stock': [100, np.nan, np.nan, 200]})
    handler = MissingValueHandler(df)
    res = handler.impute_time_series(strategy='ffill')
    assert res['stock'][1] == 100
    assert res['stock'][2] == 100
