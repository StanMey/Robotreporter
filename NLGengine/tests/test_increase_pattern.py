import pandas as pd
import pytest

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
                     datetime(year=2020, month=9, day=26)]}
    df_data = pd.DataFrame(data)

    d1 = datetime(year=2020, month=9, day=24)
    d2 = datetime(year=2020, month=9, day=25)

    increase = Increase(df_data, d1, d2)

    assert increase.period_begin == d1
    assert increase.period_end == d2

    # check if error is thrown when df_data is not of type Dataframe
    with pytest.raises(AssertionError):
        increase = Increase(data, d1, d2)


def test_increase_only_x_increase():
    """Tests Increase.only_x_increase()."""

    d1 = datetime(year=2020, month=9, day=24)
    d2 = datetime(year=2020, month=9, day=25)

    # check when there is only one increasing stock
    df_data = pd.DataFrame({'component': ['A'],
                            'indexx': ['I'],
                            'close': [1],
                            'perc_delta': [1],
                            'date': [datetime(year=2020, month=9, day=25)]})
    increase = Increase(df_data, d1, d2)
    increase.only_x_increase()
    # check if observation is being saved
    assert isinstance(increase.observations[0], Observation)
    # check if there is only one increasing stock
    observ = Observation('A', d1, d2, 'stijging', "A, dat profiteert van de onrust op de beurzen, is de enige stijger.", 9)
    assert increase.observations[0].serie == observ.serie
    assert increase.observations[0].period_begin == observ.period_begin
    assert increase.observations[0].period_end == observ.period_end
    assert increase.observations[0].pattern == observ.pattern
    assert increase.observations[0].observation == observ.observation
    assert increase.observations[0].relevance == observ.relevance


def test_increase_x_largest_increase():
    """Tests Increase.x_largest_increase()."""
    pass


def test_increase_prep_data():
    """Tests Increase.prep_data()."""
    pass
