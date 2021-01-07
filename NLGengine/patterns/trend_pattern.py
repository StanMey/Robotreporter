from datetime import datetime
from NLGengine.observation import Observation
from NLGengine.relevance import Relevance

import pandas as pd


class Trend:
    """A class that holds methods to find trend based patterns in timeseries data.
    """
    def __init__(self, df_data: pd.DataFrame, period_beg: datetime, period_end: datetime):
        """The init function

        Args:
            df_data (pd.DataFrame): The data in a pandas dataframe
            period_beg (datetime): The date with the beginning of the period
            period_end (datetime): The date with the end of the period
        """
        assert isinstance(df_data, pd.DataFrame), "df_data should be a pandas Dataframe"
        assert set(["component", "indexx", "close", "date", "sector"]).issubset(df_data.columns), "missing columns in dataset"
        self.df = df_data

        assert isinstance(period_beg, datetime), "period_beg should be a datetime object"
        assert isinstance(period_end, datetime), "period_end should be a datetime object"
        assert period_beg < period_end, "period_begin is greater than period_end"
        self.period_begin = period_beg
        self.period_end = period_end

        self.pattern = "trend"
        self.relevance = lambda x: Relevance.trend_relevance(x)
        self.observations = []
        self.trend_threshold = 2

    def check_for_turning_point(self):
        """
        Checks for the turning point in a timeseries.
        Firstly the latest change is analysed whether it is negative or positive.
        Hereafter there is checked when this change has happened,
        e.g. (if a stock has changed to positive after 2 days of negativeness)
        """
        # get all the unique components that are in the dataframe
        all_components = self.df["component"].unique()

        # loop over all component and select per component
        for component in all_components:

            # get the sector of the current component
            sector = self.df[self.df["component"] == component]["sector"].iloc[0]
            # get the indexx of the current component
            indexx = sector = self.df[self.df["component"] == component]["indexx"].iloc[0]
            # select all the rows from a certain component
            df_one_component = self.df[self.df["component"] == component].copy().sort_values("date")
            # calculate the percentage difference
            df_pct_diff = df_one_component['close'].diff(periods=1)

            count = 0
            trend_count = 0

            for index, value in df_pct_diff[::-1].iteritems():
                if count == 0:
                    latest_perc = value
                else:
                    if latest_perc >= 0.0:
                        # the latest percentage was positive, so check when it switched
                        if value < 0.0:
                            # negative percentage, so no switch yet
                            trend_count += 1
                        else:
                            # positive percentage, so switch happened
                            period_begin_trend = df_one_component.loc[index].date
                            break
                    else:
                        # the latest percentage was negative, so check when it switched
                        if value > 0.0:
                            # negative percentage, so no switch yet
                            trend_count += 1
                        else:
                            # positive percentage, so switch happened
                            period_begin_trend = df_one_component.loc[index].date
                            break
                count += 1

            # decide if the trend is strong enough
            if trend_count >= self.trend_threshold:
                # build the sentence
                # select the sentence based on the latest percentage change
                if latest_perc >= 0.0:
                    sentence = f"{component} is na {trend_count} negatieve dagen weer positief geëindigd."
                    data = {
                        "trend_duration": trend_count,
                        "trend": "pos"
                    }
                else:
                    sentence = f"{component} is na {trend_count} positieve dagen weer negatief geëindigd."
                    data = {
                        "trend_duration": trend_count,
                        "trend": "neg"
                    }
                # build the observation object
                observ = Observation(component,
                                     period_begin_trend,
                                     self.period_end,
                                     self.pattern,
                                     sector,
                                     indexx,
                                     None,
                                     None,
                                     sentence,
                                     self.relevance(trend_count),
                                     data)
                # save the observation object
                self.observations.append(observ)

    def prep_data(self):
        """Prepares the data for the analyses.
        """
        # remove all the indexes themself out of the dataframe
        all_indexes = self.df["indexx"].unique()
        self.df = self.df[~self.df["component"].isin(all_indexes)]

    def analyse(self):
        """Run the analyses of the Trend pattern.
        """
        self.prep_data()

        # check for empty dataframe
        if not self.df.empty:
            # df not empty so continue analysis
            self.check_for_turning_point()
