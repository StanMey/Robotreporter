from datetime import datetime

from NLGengine.observation import Observation
from NLGengine.relevance import Relevance
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


class Increase:
    """A class that holds methods to find increase based patterns in timeseries data in a period.
    """
    def __init__(self, df_data: pd.DataFrame, period_beg: datetime, period_end: datetime):
        """The init function.

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

        self.combi_pattern = "combi-stijging"
        self.indiv_pattern = "invidu-stijging"

        self.relevance = lambda x: Relevance.period_relevance(x)
        self.observations = []

    def only_x_increase(self):
        """Checks if there are any components that are the only one or ones (2) that have increased in the timeperiod.
        """
        # only select the components that are positive
        df_only_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df["date"].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_only_inc) == 0:
            # no component has been increasing, only decreasing components
            info = "AMX"
            # collect the additional metadata
            data = {
                    "component": info,
                    "perc_change": 0.0
                }
            # save the observation
            sentence = f"Alle fondsen binnen de {info} zijn vandaag gedaald."
            observ = Observation(info, self.period_begin, self.period_end, "combi-daling", sentence, 9.0, data)
            self.observations.append(observ)

        if len(df_only_inc) == 1:
            # only 1 component has been increasing
            info = df_only_inc.iloc[0]
            # collect the additional metadata
            data = {
                    "component": info.component,
                    "perc_change": info.perc_delta,
                    "abs_change": info.abs_delta,
                    "relev": self.relevance(info.perc_delta)
                }
            # save the observation
            sentence = f"{info.component}, dat profiteert van de onrust op de beurzen, is de enige stijger."
            observ = Observation(info.component, self.period_begin, self.period_end, self.combi_pattern, sentence, self.relevance(info.perc_delta), data)
            self.observations.append(observ)

        if len(df_only_inc) == 2:
            # only 2 components have been increasing
            info = df_only_inc.iloc[0:2]
            # collect the additional metadata
            data = {
                    "component": list(info.component),
                    "perc_change": list(info.perc_delta),
                    "abs_change": list(info.abs_delta),
                    "relev": [self.relevance(x.perc_delta) for (_, x) in info.iterrows()]
                }
            # save the observation
            sentence = f"Op {info.iloc[0].component} en {info.iloc[1].component} na dalen alle {info.iloc[0].indexx} fondsen"
            observ = Observation(info.iloc[0].component, self.period_begin, self.period_end, self.combi_pattern, sentence, self.relevance(np.mean(info.perc_delta)), data)
            self.observations.append(observ)

    def x_largest_increase(self):
        """Checks how many (1,2,3) components have increased the most in a certain timeperiod.
        """
        # filter on positive percentages and only get the difference of the end date
        df_large_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_large_inc) >= 1:
            # At least 1 component increasing
            info = df_large_inc.iloc[0]
            # collect the additional metadata
            data = {
                    "component": info.component,
                    "perc_change": info.perc_delta,
                    "abs_change": info.abs_delta,
                    "relev": self.relevance(info.perc_delta)
                }
            # save the observation
            sentence = f"In de {info.indexx} ging {info.component} aan kop met een winst van {info.perc_delta} procent."
            observ = Observation(info.component, self.period_begin, self.period_end, self.combi_pattern, sentence, self.relevance(info.perc_delta), data)
            self.observations.append(observ)

        if len(df_large_inc) >= 2:
            # At least 2 components increasing
            info = df_large_inc.iloc[0:2]
            # collect the additional metadata
            data = {
                    "component": list(info.component),
                    "perc_change": list(info.perc_delta),
                    "abs_change": list(info.abs_delta),
                    "relev": [self.relevance(x.perc_delta) for (_, x) in info.iterrows()]
                }
            # save the observation
            sentence = f"In de {info.iloc[0].indexx} waren {info.iloc[0].component} (+{info.iloc[0].perc_delta}%) en {info.iloc[1].component} (+{info.iloc[1].perc_delta}%) de grootste stijgers."
            observ = Observation(info.iloc[0].component, self.period_begin, self.period_end, self.combi_pattern, sentence, self.relevance(np.mean(info.perc_delta)), data)
            self.observations.append(observ)

        if len(df_large_inc) >= 3:
            # at least 3 components increasing
            info = df_large_inc.iloc[0:3]
            # collect the additional metadata
            data = {
                    "component": list(info.component),
                    "perc_change": list(info.perc_delta),
                    "abs_change": list(info.abs_delta),
                    "relev": [self.relevance(x.perc_delta) for (_, x) in info.iterrows()]
                }
            # save the observation
            sentence = f"{info.iloc[0].component} (+{info.iloc[0].perc_delta}%), {info.iloc[1].component} (+{info.iloc[1].perc_delta}%) en {info.iloc[2].component} (+{info.iloc[2].perc_delta}%) waren de positieve uitschieters."
            observ = Observation(info.iloc[0].component, self.period_begin, self.period_end, self.combi_pattern, sentence, self.relevance(np.mean(info.perc_delta)), data)
            self.observations.append(observ)

    def all_risers(self):
        """Gets all individual components that have increased in the time period.
        """
        # filter on positive percentages and only get the difference of the end date
        df_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        # loop over all the rising stocks and save the observations
        for index, info in df_inc.iterrows():
            # collect the additional metadata
            data = {
                    "component": info.component,
                    "perc_change": info.perc_delta,
                    "abs_change": info.abs_delta,
                    "relev": self.relevance(info.perc_delta)
                }
            # save the observation
            sentence = f"Aandeel {info.component} met {info.perc_delta}% gestegen."
            observ = Observation(info.component, self.period_begin, self.period_end, self.indiv_pattern, sentence, self.relevance(info.perc_delta), data)
            self.observations.append(observ)

    def prep_data(self, period: int):
        """Prepares and wrangles the data so the analyses can be run on it.

        Args:
            period (integer): The amount of days between the beginning of the period and the end
        """
        self.df["abs_delta"] = 0
        self.df["perc_delta"] = 0
        self.df["date"] = pd.to_datetime(self.df["date"])

        # order all data by date in ascending order, because .diff() doesn't take in the date
        self.df.sort_values('date', inplace=True)

        # remove all the indexes themself out of the dataframe
        all_indexes = self.df["indexx"].unique()
        self.df = self.df[~self.df["component"].isin(all_indexes)]

        # get all the unique components that are in the dataframe
        all_components = self.df["component"].unique()

        for component in all_components:
            # select all the rows from a certain component
            df_one_component = self.df[self.df["component"] == component]["close"].copy()
            # calculate the absolute difference
            df_abs_diff = df_one_component.diff(periods=period)
            # calculate the percentage difference
            df_pct_diff = df_one_component.pct_change(periods=period)

            # add both values back in the dataframe
            self.df.loc[df_abs_diff.index, 'abs_delta'] = df_abs_diff.values
            self.df.loc[df_pct_diff.index, 'perc_delta'] = df_pct_diff.values

        # format the percentage difference
        self.df["perc_delta"] = self.df["perc_delta"].apply(lambda x: round(x * 100, 2))

        # drop all rows with NaNs
        self.df.dropna(inplace=True)

        # sort the dataframe by percentage
        self.df.sort_values(by="perc_delta", ascending=False, inplace=True)

    def analyse(self):
        """Runs the analysis over the data.
        """
        # get the amount of days between the start and end date (not including the weekend)
        diff_days = np.busday_count(self.period_begin.strftime("%Y-%m-%d"), self.period_end.strftime("%Y-%m-%d"), weekmask=[1, 1, 1, 1, 1, 0, 0])

        self.prep_data(diff_days)
        self.x_largest_increase()
        self.only_x_increase()
        self.all_risers()
