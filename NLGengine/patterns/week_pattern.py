from datetime import datetime
from NLGengine.observation import Observation
from NLGengine.relevance import Relevance

import pandas as pd


class WeekPattern:
    """A class that holds methods to find week based patterns in timeseries data.
    """
    def __init__(self, df_data: pd.DataFrame, period_beg: datetime, period_end: datetime):
        """The init function.

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
        self.diff_period = 4

        self.pattern = "week"
        self.relevance = lambda x: Relevance.weekly_relevance(x)
        self.observations = []

    def give_week_recap(self):
        """Checks whether the stock in a certain stock has increased or decreased in total.
        """
        for _, row in self.df.iterrows():
            if row.perc_delta == 0.0:
                # average week
                # build the sentence
                sentence = f"{row.component} is in week {self.period_end.isocalendar()[1:2][0]} gelijk gebleven."
                # build the observation object
                data = {}
                observ = Observation(row.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.pattern,
                                     row.sector,
                                     row.indexx,
                                     row.perc_delta,
                                     row.abs_delta,
                                     sentence,
                                     self.relevance(row.perc_delta),
                                     data)
                # save the observation object
                self.observations.append(observ)
            elif row.perc_delta > 0.0:
                # positive week
                # build the sentence
                sentence = f"{row.component} is met {row.perc_delta} procent gestegen in week {self.period_end.isocalendar()[1:2][0]}."
                # build the observation object
                data = {
                    "trend": "pos"
                }
                observ = Observation(row.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.pattern,
                                     row.sector,
                                     row.indexx,
                                     row.perc_delta,
                                     row.abs_delta,
                                     sentence,
                                     self.relevance(row.perc_delta),
                                     data)
                # save the observation object
                self.observations.append(observ)
            else:
                # negative week
                # build the sentence
                sentence = f"{row.component} is met {abs(row.perc_delta)} procent gedaald in week {self.period_end.isocalendar()[1:2][0]}."
                # build the observation object
                data = {
                    "trend": "neg"
                }
                observ = Observation(row.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.pattern,
                                     row.sector,
                                     row.indexx,
                                     row.perc_delta,
                                     row.abs_delta,
                                     sentence,
                                     self.relevance(row.perc_delta),
                                     data)
                # save the observation object
                self.observations.append(observ)

    def prep_data(self):
        """Prepares and wrangles the data so the analyses can be run on it.
        """
        self.df["abs_delta"] = 0
        self.df["perc_delta"] = 0
        self.df["date"] = pd.to_datetime(self.df["date"])

        # remove all the indexes themself out of the dataframe
        all_indexes = self.df["indexx"].unique()
        self.df = self.df[~self.df["component"].isin(all_indexes)]

        # order all data by date in ascending order, because .diff() doesn't take in the date
        self.df.sort_values('date', inplace=True)

        # get all the unique components that are in the dataframe
        all_components = self.df["component"].unique()

        for component in all_components:
            # select all the rows from a certain component
            df_one_component = self.df[self.df["component"] == component]["close"].copy()
            # calculate the absolute difference
            df_abs_diff = df_one_component.diff(periods=self.diff_period)
            # calculate the percentage difference
            df_pct_diff = df_one_component.pct_change(periods=self.diff_period)

            # add both values back in the dataframe
            self.df.loc[df_abs_diff.index, 'abs_delta'] = df_abs_diff.values
            self.df.loc[df_pct_diff.index, 'perc_delta'] = df_pct_diff.values

        # format the percentage difference
        self.df["perc_delta"] = self.df["perc_delta"].apply(lambda x: round(x * 100, 2))

        # drop all rows with NaNs
        self.df.dropna(inplace=True)

    def analyse(self):
        """Run the analyses of the Week pattern.
        """
        self.prep_data()

        # check for empty dataframe
        if not self.df.empty:
            # df not empty so continue analysis
            self.give_week_recap()
