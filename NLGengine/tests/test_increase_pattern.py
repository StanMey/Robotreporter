import pandas as pd
import pytest
import copy

from datetime import datetime
from NLGengine.observation import Observation
from NLGengine.patterns.increase_pattern import Increase


def test_class_increase():
    """Tests the class Increase."""
    data = {'component': [1, 2, 3],
            'indexx': [1, 2, 3],
            'close': [1, 2, 3],
            'date': [datetime(year=2020, month=9, day=24),
                     datetime(year=2020, month=9, day=25),
                     datetime(year=2020, month=9, day=26)],
            'sector': ['A', 'B', 'C']}
    df_data = pd.DataFrame(data)

    d1 = datetime(year=2020, month=9, day=24)
    d2 = datetime(year=2020, month=9, day=25)

    increase = Increase(df_data, d1, d2)

    assert increase.period_begin == d1
    assert increase.period_end == d2

    # check if error is thrown when df_data is not of type Dataframe
    with pytest.raises(AssertionError):
        increase = Increase(data, d1, d2)

    # check if error is thrown when df_data misses a required column
    data2 = copy.deepcopy(data)
    del data2['sector']
    with pytest.raises(AssertionError):
        increase = Increase(pd.DataFrame(data2), d1, d2)


def test_increase_only_x_increase():
    """[summary]
    """
    pass


def test_increase_x_largest_increase():
    """Tests Increase.x_largest_increase().
    """
    pass


def test_increase_prep_data():
    """Tests Increase.prep_data().
    """
    pass
