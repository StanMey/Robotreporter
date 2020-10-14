from datetime import datetime
from NLGengine.observation import Observation

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
        assert set(["component", "indexx", "close", "date"]).issubset(df_data.columns), "missing columns in dataset"
        self.df = df_data

        assert isinstance(period_beg, datetime), "period_beg should be a datetime object"
        assert isinstance(period_end, datetime), "period_end should be a datetime object"
        assert period_beg < period_end, "period_begin is greater than period_end"
        self.period_begin = period_beg
        self.period_end = period_end

        self.pattern = "trend"
        self.observations = []

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

            # select all the rows from a certain component
            df_one_component = self.df[self.df["component"] == component].copy().sort_values("date")
            # calculate the percentage difference
            df_pct_diff = df_one_component['close'].pct_change(periods=1)

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
            if trend_count >= 2:
                # select the sentence based on the latest percentage change
                if latest_perc >= 0.0:
                    sentence = f"{component} na {trend_count} negatieve dagen weer positief geëindigd."
                else:
                    sentence = f"{component} na {trend_count} positieve dagen weer negatief geëindigd."

                # find the begin period
                observ = Observation(component, period_begin_trend, self.period_end, "Trend", sentence, 6)
                self.observations.append(observ)

    def analyse(self):
        """Run the analyses of the Trend pattern.
        """
        self.check_for_turning_point()
