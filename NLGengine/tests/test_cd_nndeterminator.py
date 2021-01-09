import pytest
import numpy as np

from datetime import datetime
from NLGengine.observation import Observation
from NLGengine.content_determination.nndeterminator import one_hot_encode_input, is_focus_sector, generate_smoothing_mean


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


def test_one_hot_encode_input():
    """Tests the one_hot_encode_input function
    """
    pass
