import pytest

from NLGengine.content_determination.rules import flatten, Rules


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
    pass
