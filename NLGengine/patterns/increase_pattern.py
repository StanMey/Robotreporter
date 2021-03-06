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
        assert set(["component", "indexx", "close", "date", "sector"]).issubset(df_data.columns), "missing columns in dataset"
        self.df = df_data

        assert isinstance(period_beg, datetime), "period_beg should be a datetime object"
        assert isinstance(period_end, datetime), "period_end should be a datetime object"
        assert period_beg < period_end, "period_begin is greater than period_end"
        self.period_begin = period_beg
        self.period_end = period_end

        self.indiv_pattern = "individu-stijging"
        self.combi_pattern = "combi-stijging"
        self.combi_diff_threshold = 1.0
        self.combi_diff_significance = 1.6

        self.indiv_relevance = lambda x: Relevance.period_single_relevance(x)
        self.combi_relevance = lambda x: Relevance.period_combi_relevance(x)
        self.observations = []

    def only_x_increase(self):
        """Checks if there are any components that are the only one or ones (2) that have increased in the timeperiod.
        """
        # only select the components that are positi ve
        df_only_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df["date"].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_only_inc) == 0:
            # no component has been increasing, only decreasing components
            # build the sentence
            info = "AMX"
            sentence = f"alle fondsen binnen de {info} zijn vandaag gedaald"
            # build the observation object
            data = {
                "only_x": 0
            }
            observ = Observation(info,
                                 self.period_begin,
                                 self.period_end,
                                 "combi-daling",
                                 None,
                                 info,
                                 None,
                                 None,
                                 sentence,
                                 9.5,
                                 data)
            # save the observation object
            self.observations.append(observ)

        if len(df_only_inc) == 1:
            # only 1 component has been increasing
            info = df_only_inc.iloc[0]
            # build the sentence
            sentence = f"{info.component} was met {info.perc_delta} procent de enige stijger"
            # build the observation object
            data = {
                "only_x": 1
            }
            observ = Observation(info.component,
                                 self.period_begin,
                                 self.period_end,
                                 self.combi_pattern,
                                 info.sector,
                                 info.indexx,
                                 info.perc_delta,
                                 info.abs_delta,
                                 sentence,
                                 self.indiv_relevance(info.perc_delta + self.combi_diff_threshold),
                                 data)
            # save the observation object
            self.observations.append(observ)

        if len(df_only_inc) == 2:
            # only 2 components have been increasing
            info = df_only_inc.iloc[0:2]
            # build the sentence
            sentence = f"op {info.iloc[0].component} en {info.iloc[1].component} na daalden alle {info.iloc[0].indexx} fondsen"
            # build the observation object
            data = {
                "only_x": 2,
                "components": list(info.component),
                "sectors": list(info.sector),
                "perc_change": list(info.perc_delta),
                "abs_change": list(info.abs_delta),
            }
            observ = Observation(info.iloc[0].component,
                                 self.period_begin,
                                 self.period_end,
                                 self.combi_pattern,
                                 None,
                                 info.iloc[0].indexx,
                                 None,
                                 None,
                                 sentence,
                                 self.indiv_relevance(np.mean([info.iloc[0].perc_delta, info.iloc[1].perc_delta])),
                                 data)
            # save the observation object
            self.observations.append(observ)

    def x_largest_increase(self):
        """Checks how many (1,2,3) components have increased the most in a certain timeperiod.
        """
        # since we only want one of these observations below to return we add a 'not_found' variable
        # which switches to False when an observation has been found
        not_found = True

        # filter on positive percentages and only get the difference of the end date
        df_large_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_large_inc) >= 3 and not_found:
            # there are at least 3 increasing
            first = df_large_inc.iloc[0]
            second = df_large_inc.iloc[1]
            third = df_large_inc.iloc[2]
            if (third.perc_delta > self.combi_diff_significance) and ((first.perc_delta - second.perc_delta) <= self.combi_diff_threshold) and ((second.perc_delta - third.perc_delta) <= self.combi_diff_threshold):
                # check whether there is a significant increase between the third and the rest,
                # and between 1, 2 and 3 there is no significant increase
                # build the sentence
                sentence = (
                    f"{first.component} ({first.perc_delta}%), {second.component} ({second.perc_delta}%)"
                    f"en {third.component} ({third.perc_delta}%) waren de positieve uitschieters.")
                # build the observation objec t
                data = {
                    "components": [first.component, second.component, third.component],
                    "sectors": [first.sector, second.sector, third.sector],
                    "perc_change": [first.perc_delta, second.perc_delta, third.perc_delta],
                    "abs_change": [first.abs_delta, second.abs_delta, third.abs_delta]
                }
                observ = Observation(first.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.combi_pattern,
                                     None,
                                     first.indexx,
                                     None,
                                     None,
                                     sentence,
                                     self.combi_relevance((((first.perc_delta - second.perc_delta) + (second.perc_delta - third.perc_delta)) / 2)),
                                     data)
                # save the observation object
                self.observations.append(observ)
                not_found = False

        if len(df_large_inc) >= 2 and not_found:
            # there are at least 2 increasing
            first = df_large_inc.iloc[0]
            second = df_large_inc.iloc[1]
            if (second.perc_delta > self.combi_diff_significance) and ((first.perc_delta - second.perc_delta) <= self.combi_diff_threshold):
                # check whether there is a significant increase between second and the rest,
                # and between 1 and 2 there is no significant increase
                # build the sentence
                sentence = f"""In de {first.indexx} waren {first.component} ({first.perc_delta}%)
                            en {second.component} ({second.perc_delta}%) de grootste stijgers."""
                # build the observation object
                data = {
                    "components": [first.component, second.component],
                    "sectors": [first.sector, second.sector],
                    "perc_change": [first.perc_delta, second.perc_delta],
                    "abs_change": [first.abs_delta, second.abs_delta]
                }
                observ = Observation(first.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.combi_pattern,
                                     None,
                                     first.indexx,
                                     None,
                                     None,
                                     sentence,
                                     self.combi_relevance((first.perc_delta - second.perc_delta)),
                                     data)
                # save the observation object
                self.observations.append(observ)
                not_found = False

        if len(df_large_inc) >= 1 and not_found:
            # there are at least 1 increasing
            first = df_large_inc.iloc[0]
            if first.perc_delta > self.combi_diff_significance:
                # check whether there is a significant increase between 1 and the rest
                # build the sentence
                sentence = f"In de {first.indexx} ging {first.component} aan kop met een winst van {first.perc_delta} procent."
                # build the observation object
                data = {
                    "components": [first.component],
                    "sectors": [first.sector],
                    "perc_change": [first.perc_delta],
                    "abs_change": [first.abs_delta]
                }
                observ = Observation(first.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.combi_pattern,
                                     first.sector,
                                     first.indexx,
                                     first.perc_delta,
                                     first.abs_delta,
                                     sentence,
                                     self.indiv_relevance(first.perc_delta + self.combi_diff_threshold),
                                     data)
                # save the observation object
                self.observations.append(observ)
                not_found = False

    def all_risers(self):
        """Gets all individual components that have increased in the time period.
        """
        # filter on positive percentages and only get the difference of the end date
        df_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        # get the AMX indexx and its percentage change
        indexx_info = self.df[self.df['component'] == "AMX"]
        long_sentence = None

        if float(indexx_info.perc_delta) < 0.0:
            long_sentence = f", terwijl de AMX met {str(abs(float(indexx_info.perc_delta)))} procent daalde"

        # remove the indexes
        df_inc = df_inc[~df_inc["component"].isin(["AMX"])]

        # loop over all the rising stocks and save the observations
        for index, info in df_inc.iterrows():
            # build the sentence
            sentence = f"Aandeel {info.component} is met {info.perc_delta}% gestegen."
            # build the observation object
            data = {
                "long": long_sentence
            }
            observ = Observation(info.component,
                                 self.period_begin,
                                 self.period_end,
                                 self.indiv_pattern,
                                 info.sector,
                                 info.indexx,
                                 info.perc_delta,
                                 info.abs_delta,
                                 sentence,
                                 self.indiv_relevance(info.perc_delta),
                                 data)
            # save the observation object
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
        diff_days = np.busday_count(self.period_begin.strftime("%Y-%m-%d"),
                                    self.period_end.strftime("%Y-%m-%d"),
                                    weekmask=[1, 1, 1, 1, 1, 0, 0])

        self.prep_data(diff_days)

        # check for empty dataframe
        if not self.df.empty:
            # df not empty so continue analysis
            self.all_risers()

            # remove all the indexes themself out of the dataframe
            all_indexes = self.df["indexx"].unique()
            self.df = self.df[~self.df["component"].isin(all_indexes)]

            self.x_largest_increase()
            self.only_x_increase()
