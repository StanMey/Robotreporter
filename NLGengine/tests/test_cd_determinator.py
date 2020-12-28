import pytest
import numpy as np

from datetime import datetime
from NLGengine.observation import Observation
from NLGengine.content_determination.determinator import check_pattern, check_period, check_component, has_overlap, \
    is_focus_sector, generate_smoothing_mean

# new_date = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)


def test_check_pattern():
    """Tests the check_pattern function
    """
    date1 = datetime.now()
    date2 = datetime.now()

    # test for 2 the same patterns
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    assert check_pattern(observ1, observ2) == 0

    # test for 2 similar patterns
    observ1 = Observation("AMX", date1, date2, "combi-daling", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "individu-daling", None, None, None, None, "", 5, dict())
    assert check_pattern(observ1, observ2) == 1

    observ1 = Observation("AMX", date1, date2, "individu-stijging", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "combi-stijging", None, None, None, None, "", 5, dict())
    assert check_pattern(observ1, observ2) == 1

    # test for 2 different patterns
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "trend", None, None, None, None, "", 5, dict())
    assert check_pattern(observ1, observ2) == 2


def test_check_period():
    """Tests the check_period function
    """
    # check for identical periods for two observations
    date1 = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)

    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())

    assert check_period(observ1, observ2) == 0

    # check for overlapping periods for two observations
    date1 = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=10, day=10).replace(hour=00, minute=00, second=00, microsecond=0)
    date3 = datetime(year=2020, month=8, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date4 = datetime(year=2020, month=10, day=3).replace(hour=00, minute=00, second=00, microsecond=0)

    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date3, date4, "week", None, None, None, None, "", 5, dict())

    assert check_period(observ1, observ2) == 1

    # check for two observations that are next to each other regards periods
    # two observations directly after each other
    date1 = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=10, day=8).replace(hour=00, minute=00, second=00, microsecond=0)
    date3 = datetime(year=2020, month=10, day=9).replace(hour=00, minute=00, second=00, microsecond=0)
    date4 = datetime(year=2020, month=10, day=13).replace(hour=00, minute=00, second=00, microsecond=0)

    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date3, date4, "week", None, None, None, None, "", 5, dict())

    assert check_period(observ1, observ2) == 2

    # two observations directly after each other with weekend in between
    date5 = datetime(year=2020, month=11, day=16).replace(hour=00, minute=00, second=00, microsecond=0)
    date6 = datetime(year=2020, month=12, day=24).replace(hour=00, minute=00, second=00, microsecond=0)
    date7 = datetime(year=2020, month=11, day=10).replace(hour=00, minute=00, second=00, microsecond=0)
    date8 = datetime(year=2020, month=11, day=13).replace(hour=00, minute=00, second=00, microsecond=0)

    observ3 = Observation("AMX", date5, date6, "week", None, None, None, None, "", 5, dict())
    observ4 = Observation("AMX", date7, date8, "week", None, None, None, None, "", 5, dict())

    assert check_period(observ3, observ4) == 2

    # check for different periods for two observations
    date1 = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=10, day=8).replace(hour=00, minute=00, second=00, microsecond=0)
    date3 = datetime(year=2020, month=10, day=17).replace(hour=00, minute=00, second=00, microsecond=0)
    date4 = datetime(year=2020, month=11, day=4).replace(hour=00, minute=00, second=00, microsecond=0)

    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date3, date4, "week", None, None, None, None, "", 5, dict())

    assert check_period(observ1, observ2) == 3


def test_check_component():
    """Tests the check_component function
    """
    date1 = datetime.now()
    date2 = datetime.now()

    # 2 COMBI PATTERNS
    # 2 combi patterns with overlapping components
    comps1 = {
        "components": ["A", "B"],
        "sectors": ["S1", "S2"]
    }
    comps2 = {
        "components": ["B", "C"],
        "sectors": ["S3", "S4"]
    }
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps1)
    observ2 = Observation("A", date1, date2, "week", None, None, None, None, "", 5, comps2)

    assert check_component(observ1, observ2) == 0

    # 2 combi patterns with similar components
    comps1 = {
        "components": ["A", "B"],
        "sectors": ["S1", "S2"]
    }
    comps2 = {
        "components": ["C", "D"],
        "sectors": ["S3", "S2"]
    }
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps1)
    observ2 = Observation("A", date1, date2, "week", None, None, None, None, "", 5, comps2)

    assert check_component(observ1, observ2) == 1

    # 2 combi patterns with no similar or overlapping components
    comps1 = {
        "components": ["A", "B"],
        "sectors": ["S1", "S2"]
    }
    comps2 = {
        "components": ["C", "D"],
        "sectors": ["S3", "S4"]
    }
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps1)
    observ2 = Observation("A", date1, date2, "week", None, None, None, None, "", 5, comps2)

    assert check_component(observ1, observ2) == 2

    # ONLY OBSERVATION 1 COMBI PATTERN
    # observation 1 combi with overlapping components
    comps = {
        "components": ["A", "B"],
        "sectors": ["S1", "S2"]
    }
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps)
    observ2 = Observation("A", date1, date2, "week", None, None, None, None, "", 5, dict())

    assert check_component(observ1, observ2) == 0

    # observation 1 combi with similar components
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps)
    observ2 = Observation("D", date1, date2, "week", "S1", None, None, None, "", 5, dict())

    assert check_component(observ1, observ2) == 1

    # observation 1 combi with no similar or overlapping components
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps)
    observ2 = Observation("AMX", date1, date2, "week", "D", None, None, None, "", 5, dict())

    assert check_component(observ1, observ2) == 2

    # ONLY OBSERVATION 2 COMBI PATTERN
    # observation 2 combi with overlapping components
    comps = {
        "components": ["A", "B"],
        "sectors": ["S1", "S2"]
    }
    observ1 = Observation("A", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps)

    assert check_component(observ1, observ2) == 0

    # observation 2 combi with similar components
    observ1 = Observation("D", date1, date2, "week", "S1", None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps)

    assert check_component(observ1, observ2) == 1

    # observation 2 combi with no similar or overlapping components
    observ1 = Observation("AMX", date1, date2, "week", "D", None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, comps)

    assert check_component(observ1, observ2) == 2

    # NO COMBI PATTERN
    # no combi observation, with overlapping components
    observ1 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())
    observ2 = Observation("AMX", date1, date2, "week", None, None, None, None, "", 5, dict())

    assert check_component(observ1, observ2) == 0

    # no combi observation, with similar components
    observ1 = Observation("B", date1, date2, "week", "A", None, None, None, "", 5, dict())
    observ2 = Observation("C", date1, date2, "week", "A", None, None, None, "", 5, dict())

    assert check_component(observ1, observ2) == 1

    # no combi observation, with no similar or overlapping components
    observ1 = Observation("A", date1, date2, "week", "C", None, None, None, "", 5, dict())
    observ2 = Observation("B", date1, date2, "week", "D", None, None, None, "", 5, dict())

    assert check_component(observ1, observ2) == 2


def test_has_overlap():
    """Tests the has_overlap function
    """
    # check for assertion error
    date1 = datetime(year=2020, month=9, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=9, day=29).replace(hour=00, minute=00, second=00, microsecond=0)

    with pytest.raises(AssertionError):
        has_overlap(date2, date1, date1, date2)

    with pytest.raises(AssertionError):
        has_overlap(date1, date2, date2, date1)

    # check when there is overlap
    date1 = datetime(year=2020, month=8, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=9, day=10).replace(hour=00, minute=00, second=00, microsecond=0)
    date3 = datetime(year=2020, month=9, day=8).replace(hour=00, minute=00, second=00, microsecond=0)
    date4 = datetime(year=2020, month=9, day=20).replace(hour=00, minute=00, second=00, microsecond=0)

    assert has_overlap(date1, date2, date3, date4)

    date5 = datetime(year=2020, month=9, day=5).replace(hour=00, minute=00, second=00, microsecond=0)
    date6 = datetime(year=2020, month=9, day=10).replace(hour=00, minute=00, second=00, microsecond=0)

    assert has_overlap(date3, date4, date5, date6)

    # check when no overlap
    date1 = datetime(year=2020, month=8, day=30).replace(hour=00, minute=00, second=00, microsecond=0)
    date2 = datetime(year=2020, month=9, day=5).replace(hour=00, minute=00, second=00, microsecond=0)
    date3 = datetime(year=2020, month=9, day=12).replace(hour=00, minute=00, second=00, microsecond=0)
    date4 = datetime(year=2020, month=9, day=20).replace(hour=00, minute=00, second=00, microsecond=0)

    assert not has_overlap(date1, date2, date3, date4)

    date5 = datetime(year=2020, month=9, day=25).replace(hour=00, minute=00, second=00, microsecond=0)
    date6 = datetime(year=2020, month=10, day=10).replace(hour=00, minute=00, second=00, microsecond=0)

    assert not has_overlap(date3, date4, date5, date6)


def test_is_focus_sector():
    """Tests the is_focus_sector function.
    """
    date1 = datetime.now()
    date2 = datetime.now()

    focus_sectors = ["A", "B", "C"]

    observ1 = Observation("Q", date1, date2, "pat", "A", "ind", 3.4, 1.0, "sentence", 5.0, dict())
    observ2 = Observation("Q", date1, date2, "pat", "B", "ind", 3.4, 1.0, "sentence", 5.0, dict())
    observ3 = Observation("Q", date1, date2, "pat", "sec", "ind", 3.4, 1.0, "sentence", 5.0, dict())

    # observation holds a sector to focus on
    assert is_focus_sector(focus_sectors, observ1)
    assert is_focus_sector(focus_sectors, observ2)
    # observation doesn't hold a sector to focus on
    assert not is_focus_sector(focus_sectors, observ3)

    # observation holds one or multiple sectors to focus on
    meta = {
        "sectors": ["A", "B", "D"]
    }
    observ4 = Observation("Q", date1, date2, "pat", "A", "ind", 3.4, 1.0, "sentence", 5.0, meta)
    assert is_focus_sector(focus_sectors, observ4)

    # observation doesn't hold one or multiple sectors to focus on
    meta = {
        "sectors": ["D", "E"]
    }
    observ5 = Observation("Q", date1, date2, "pat", "A", "ind", 3.4, 1.0, "sentence", 5.0, meta)
    assert not is_focus_sector(focus_sectors, observ5)


def test_generate_smoothing_mean():
    """Tests the generate_smoothing_mean function
    """
    x = np.array([1.0])
    y = generate_smoothing_mean(1)
    assert len(x) == len(y)
    assert x == y

    x = generate_smoothing_mean(6)
    y = np.array([0.16666667, 0.33333333, 0.5, 0.66666667, 0.83333333, 1.0])
    assert len(x) == len(y)
    assert all([round(a, 3) == round(b, 3) for a, b in zip(x, y)])

    x = generate_smoothing_mean(8)
    y = np.array([0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0])
    assert len(x) == len(y)
    assert all([round(a, 3) == round(b, 3) for a, b in zip(x, y)])
