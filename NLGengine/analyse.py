from NLGengine.patterns.increase_pattern import Increase
from NLGengine.patterns.decrease_pattern import Decrease
from NLGengine.patterns.week_pattern import WeekPattern
from NLGengine.patterns.trend_pattern import Trend
from NLGengine.patterns.sector_pattern import Sector


class Analyse:
    """A class for running the analysis over the given data.
    """
    def __init__(self, data, period_beg, period_end):
        """The init function.

        Args:
            data (pd.dataframe): The dataframe to be used for running the analysis
            period_beg (datetime.datetime): The datetime of the beginning of the period
            period_end (datetime.datetime): The datetime of the end of the period
        """
        self.data = data
        self.period_begin = period_beg
        self.period_end = period_end
        self.observations = []

    def find_period_observations(self):
        """Runs the analysis of the fixed period based patterns.
        """
        increase = Increase(self.data.copy(deep=True), self.period_begin, self.period_end)
        increase.analyse()
        self.observations.extend(increase.observations)

        decrease = Decrease(self.data.copy(deep=True), self.period_begin, self.period_end)
        decrease.analyse()
        self.observations.extend(decrease.observations)

        sector = Sector(self.data.copy(deep=True), self.period_begin, self.period_end)
        sector.analyse()
        self.observations.extend(sector.observations)

    def find_weekly_observations(self):
        """Runs the analysis of the weekly based patterns.
        """
        week_pattern = WeekPattern(self.data.copy(deep=True), self.period_begin, self.period_end)
        week_pattern.analyse()
        self.observations.extend(week_pattern.observations)

    def find_trend_observations(self):
        """Runs the analysis of the trend based patterns.
        """
        trend_pattern = Trend(self.data.copy(deep=True), self.period_begin, self.period_end)
        trend_pattern.analyse()
        self.observations.extend(trend_pattern.observations)
