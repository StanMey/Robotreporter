import pytest

from datetime import datetime
from NLGengine.content_determination.rules import flatten, Rules
from NLGengine.observation import Observation


def test_flatten():
    """Tests the flatten function.
    """
    first_list = ["asdf", "wer", "asdf", "2341"]
    assert list(flatten(first_list)) == first_list

    second_list = ["asdf", "wer", ["asdf", "2341"], "asdf", "qwerty"]
    second_answer = ["asdf", "wer", "asdf", "2341", "asdf", "qwerty"]
    assert list(flatten(second_list)) == second_answer

    third_list = ["asdf", "wer", ["asdf", "2341"], "asdf", ["qwerty"]]
    third_answer = ["asdf", "wer", "asdf", "2341", "asdf", "qwerty"]
    assert list(flatten(third_list)) == third_answer


def test_x_times_repeat_comp():
    """Tests the x_times_repeat_comp static method of the Rules class.
    """
    date1 = datetime.now()
    date2 = datetime.now()

    # building some dictionaries for testing purposes
    comps1 = {
        "components": ["D", "E", "F"]
    }
    comps2 = {
        "components": ["D", "R", "C"]
    }
    comps3 = {
        "components": ["E", "X", "D"]
    }
    comps4 = {
        "components": ["D", "E", "F"]
    }
    observ1 = Observation("D", date1, date2, "trend", "sec", "amx", 3.4, 2.3, "sentence here", 5.0, comps1)
    observ2 = Observation("A", date1, date2, "trend", "sec", "amx", 3.4, 2.3, "sentence here", 5.0, comps2)
    observ3 = Observation("C", date1, date2, "trend", "sec", "amx", 3.4, 2.3, "sentence here", 5.0, comps3)
    observ4 = Observation("D", date1, date2, "trend", "sec", "amx", 3.4, 2.3, "sentence here", 5.0, comps4)
    observ5 = Observation("T", date1, date2, "trend", "sec", "amx", 3.4, 2.3, "sentence here", 5.0, dict())
    observ6 = Observation("D", date1, date2, "trend", "sec", "amx", 3.4, 2.3, "sentence here", 5.0, dict())

    # run the tests
    # repeated for x times
    assert Rules.x_times_repeat_comp(3, [observ1, observ2, observ6])
    assert Rules.x_times_repeat_comp(3, [observ1, observ3, observ4])

    # not repeated for x times
    assert not Rules.x_times_repeat_comp(3, [observ5, observ6])
    assert not Rules.x_times_repeat_comp(3, [observ1, observ3, observ5])
