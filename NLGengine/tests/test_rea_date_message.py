import pytest

from NLGengine.realisation.date_message import DateMessage


def test_day_to_string():
    """Tests the day_to_string function.
    """
    assert DateMessage.day_to_string(0) == "maandag"
    assert DateMessage.day_to_string(3) == "donderdag"
    assert DateMessage.day_to_string(6) == "zondag"

    with pytest.raises(AssertionError):
        DateMessage.day_to_string(9)
    with pytest.raises(AssertionError):
        DateMessage.day_to_string(-1)


def test_month_to_string():
    """Tests the month_to_string function.
    """
    assert DateMessage.month_to_string(1) == "januari"
    assert DateMessage.month_to_string(7) == "juli"
    assert DateMessage.month_to_string(12) == "december"

    with pytest.raises(AssertionError):
        DateMessage.month_to_string(0)
    with pytest.raises(AssertionError):
        DateMessage.month_to_string(13)


def test_number_to_string():
    """Tests the number_to_string function.
    """
    assert DateMessage.number_to_string(1) == "een"
    assert DateMessage.number_to_string(9) == "negen"
    assert DateMessage.number_to_string(15) == "vijftien"
    assert DateMessage.number_to_string(20) == "twintig"
    assert DateMessage.number_to_string(21) == "21"
    assert DateMessage.number_to_string(30) == "30"


def test_day_difference_to_string():
    """Tests the day_difference_to_string function.
    """
    assert DateMessage.day_difference_to_string(0, False) == "dezelfde dag"
    assert DateMessage.day_difference_to_string(1, False) == "de dag daarvoor"
    assert DateMessage.day_difference_to_string(3, False) == "drie dagen daarvoor"
    assert DateMessage.day_difference_to_string(8, False) == "acht dagen daarvoor"

    assert DateMessage.day_difference_to_string(0, True) == "vandaag"
    assert DateMessage.day_difference_to_string(1, True) == "gisteren"
    assert DateMessage.day_difference_to_string(3, True) == "drie dagen geleden"
    assert DateMessage.day_difference_to_string(8, True) == "acht dagen geleden"


def test_explicit_day_difference_to_string():
    """Tests the explicit_day_difference_to_string function.
    """
    assert DateMessage.explicit_day_difference_to_string(0, False) == "de maandag ervoor"
    assert DateMessage.explicit_day_difference_to_string(2, False) == "de woensdag ervoor"
    assert DateMessage.explicit_day_difference_to_string(4, False) == "de vrijdag ervoor"

    assert DateMessage.explicit_day_difference_to_string(0, True) == "de maandag hiervoor"
    assert DateMessage.explicit_day_difference_to_string(2, True) == "de woensdag hiervoor"
    assert DateMessage.explicit_day_difference_to_string(3, True) == "de donderdag hiervoor"

    with pytest.raises(AssertionError):
        DateMessage.explicit_day_difference_to_string(9, True)


def test_week_difference_to_string():
    """Tests the week_difference_to_string function.
    """
    assert DateMessage.week_difference_to_string(0, False) == "dezelfde week"
    assert DateMessage.week_difference_to_string(1, False) == "de week daarvoor"
    assert DateMessage.week_difference_to_string(4, False) == "vier weken daarvoor"
    assert DateMessage.week_difference_to_string(8, False) == "acht weken daarvoor"

    assert DateMessage.week_difference_to_string(0, True) == "deze week"
    assert DateMessage.week_difference_to_string(2, True) == "twee weken geleden"
    assert DateMessage.week_difference_to_string(6, True) == "zes weken geleden"
    assert DateMessage.week_difference_to_string(11, True) == "elf weken geleden"


def test_explicit_week_difference_to_string():
    """Tests the explicit_week_difference_to_string function.
    """
    assert DateMessage.explicit_week_difference_to_string(1, False) == "de week ervoor op dinsdag"
    assert DateMessage.explicit_week_difference_to_string(5, False) == "de week ervoor op zaterdag"

    assert DateMessage.explicit_week_difference_to_string(2, True) == "de week hiervoor op woensdag"
    assert DateMessage.explicit_week_difference_to_string(4, True) == "de week hiervoor op vrijdag"

    with pytest.raises(AssertionError):
        DateMessage.explicit_week_difference_to_string(-1, False)


def test_month_difference_to_string():
    """Tests the month_difference_to_string function.
    """
    assert DateMessage.month_difference_to_string(0, False) == "dezelfde maand"
    assert DateMessage.month_difference_to_string(1, False) == "de maand daarvoor"
    assert DateMessage.month_difference_to_string(4, False) == "vier maanden daarvoor"

    assert DateMessage.month_difference_to_string(0, True) == "deze maand"
    assert DateMessage.month_difference_to_string(1, True) == "vorige maand"
    assert DateMessage.month_difference_to_string(3, True) == "drie maanden geleden"
