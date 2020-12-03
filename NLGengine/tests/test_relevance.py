import pytest
from pytest import approx

from NLGengine.relevance import Relevance


def test_tanh():
    """Tests the tanh function
    """
    assert Relevance.tanh(0) == approx(0)
    assert Relevance.tanh(1.0) == approx(0.761, abs=1e-3)
    assert Relevance.tanh(1.6) == approx(0.921, abs=1e-3)
    assert Relevance.tanh(2.0) == approx(0.964, abs=1e-3)


def test_period_single_relevance():
    """Tests the period_single_relevance function
    """
    assert Relevance.period_single_relevance(1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.period_single_relevance(-1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.period_single_relevance(1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.period_single_relevance(-1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.period_single_relevance(2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)
    assert Relevance.period_single_relevance(-2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)


def test_period_combi_relevance():
    """Tests the period_combi_relevance function
    """
    assert Relevance.period_combi_relevance(0, factor=1.0, multi=1.0) == approx(1.0, abs=1e-3)
    assert Relevance.period_combi_relevance(0.2, factor=1.0, multi=1.0) == approx(0.802, abs=1e-3)
    assert Relevance.period_combi_relevance(-0.2, factor=1.0, multi=1.0) == approx(0.802, abs=1e-3)
    assert Relevance.period_combi_relevance(0.5, factor=1.0, multi=1.0) == approx(0.537, abs=1e-3)
    assert Relevance.period_combi_relevance(-0.5, factor=1.0, multi=1.0) == approx(0.537, abs=1e-3)
    assert Relevance.period_combi_relevance(1.0, factor=1.0, multi=1.0) == approx(0.238, abs=1e-3)
    assert Relevance.period_combi_relevance(-1.0, factor=1.0, multi=1.0) == approx(0.238, abs=1e-3)


def test_weekly_relevance():
    """Tests the weekly_relevance function
    """
    assert Relevance.weekly_relevance(1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.weekly_relevance(-1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.weekly_relevance(1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.weekly_relevance(-1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.weekly_relevance(2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)
    assert Relevance.weekly_relevance(-2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)


def test_trend_relevance():
    """Tests the trend_relevance function
    """
    assert Relevance.trend_relevance(0, factor=5.4, multi=1.0) == approx(0, abs=1e-3)
    assert Relevance.trend_relevance(1, factor=5.4, multi=1.0) == approx(0.183, abs=1e-3)
    assert Relevance.trend_relevance(2, factor=5.4, multi=1.0) == approx(0.354, abs=1e-3)
    assert Relevance.trend_relevance(3, factor=5.4, multi=1.0) == approx(0.504, abs=1e-3)
    assert Relevance.trend_relevance(5, factor=5.4, multi=1.0) == approx(0.728, abs=1e-3)
    assert Relevance.trend_relevance(8, factor=5.4, multi=1.0) == approx(0.901, abs=1e-3)

    with pytest.raises(AssertionError):
        Relevance.trend_relevance(-1)

    with pytest.raises(AssertionError):
        Relevance.trend_relevance(-4)


def test_whole_sector_relevance():
    """Tests the whole_sector_relevance function
    """
    assert Relevance.whole_sector_relevance(1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.whole_sector_relevance(-1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.whole_sector_relevance(1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.whole_sector_relevance(-1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.whole_sector_relevance(2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)
    assert Relevance.whole_sector_relevance(-2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)


def test_one_comp_sector_relevance():
    """Tests the one_comp_sector_relevance function
    """
    assert Relevance.one_comp_sector_relevance(1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.one_comp_sector_relevance(-1.0, factor=1.0, multi=1.0) == approx(0.761, abs=1e-3)
    assert Relevance.one_comp_sector_relevance(1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.one_comp_sector_relevance(-1.6, factor=1.0, multi=1.0) == approx(0.921, abs=1e-3)
    assert Relevance.one_comp_sector_relevance(2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)
    assert Relevance.one_comp_sector_relevance(-2.0, factor=1.0, multi=1.0) == approx(0.964, abs=1e-3)
