from datetime import datetime

from NLGengine.observation import Observation
from NLGengine.relevance import Relevance
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


class Decrease:
    """A class that holds methods to find decrease based patterns in timeseries data in a period.
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

        self.indiv_pattern = "individu-daling"
        self.combi_pattern = "combi-daling"
        self.combi_diff_threshold = 1.0
        self.combi_diff_significance = 1.6

        self.indiv_relevance = lambda x: Relevance.period_single_relevance(x)
        self.combi_relevance = lambda x: Relevance.period_combi_relevance(x)
        self.observations = []

    def only_x_decrease(self):
        """Checks if there are any components that are the only one or ones (2) that have decreased in the timeperiod.
        """
        # only select the components that are negative
        df_dec = self.df[(self.df["perc_delta"] < 0.0) & (self.df["date"].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_dec) == 0:
            # no component has been decreasing, only increasing components
            # build the sentence
            info = "AMX"
            sentence = f"Alle fondsen binnen de {info} zijn vandaag gestegen."
            # build the observation object
            data = {}
            observ = Observation(info,
                                 self.period_begin,
                                 self.period_end,
                                 "combi-stijging",
                                 None,
                                 info,
                                 None,
                                 None,
                                 sentence,
                                 9.5,
                                 data)
            # save the observation object
            self.observations.append(observ)

        if len(df_dec) == 1:
            # only 1 component has been decreasing
            info = df_dec.iloc[0]
            # build the sentence
            sentence = f"{info.component} was vandaag met {info.perc_delta} procent de enige daler"
            # build the observation object
            data = {}
            observ = Observation(info.component,
                                 self.period_begin,
                                 self.period_end,
                                 self.combi_pattern,
                                 info.sector,
                                 info.indexx,
                                 info.perc_delta,
                                 info.abs_delta,
                                 sentence,
                                 self.indiv_relevance(abs(info.perc_delta) + self.combi_diff_threshold),
                                 data)
            # save the observation object
            self.observations.append(observ)

        if len(df_dec) == 2:
            # only 2 components have been decreasing
            info = df_dec.iloc[0:2]
            # collect the additional metadata
            # build the sentence
            sentence = f"Op {info.iloc[0].component} en {info.iloc[1].component} na stegen alle fondsen"
            # build the observation object
            data = {
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

    def x_largest_decrease(self):
        """Checks how many (1,2,3) components have decreased the most in a certain timeperiod.
        """
        # since we only want one of these observations below to return we add a 'not_found' variable
        # which switches to False when an observation has been found
        not_found = True

        # filter on negative percentages and only get the difference of the end date
        df_large_dec = self.df[(self.df["perc_delta"] < 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_large_dec) >= 3 and not_found:
            # there are at least 3 decreasing
            first = df_large_dec.iloc[0]
            second = df_large_dec.iloc[1]
            third = df_large_dec.iloc[2]
            if (abs(third.perc_delta) > self.combi_diff_significance) and (abs(first.perc_delta - second.perc_delta) <= self.combi_diff_threshold) and (abs(second.perc_delta - third.perc_delta) <= self.combi_diff_threshold):
                # check whether there is a significant decrease between the third and the rest,
                # and between 1, 2 and 3 there is no significant decrease
                # build the sentence
                sentence = f"""{first.component} ({first.perc_delta}%), {second.component} ({second.perc_delta}%)
                               en {third.component} ({third.perc_delta}%) waren de negatieve uitschieters."""
                # build the observation object
                data = {
                    "components": [first.component, second.component, third.component],
                    "sectors": [first.sector, second.sector, third.sector],
                    "perc_change": [first.perc_delta, second.perc_delta, third.perc_delta],
                    "abs_change": [first.abs_delta, second.abs_delta, third.abs_delta]
                }
                # calculate the relevance
                rel = ((abs(first.perc_delta - second.perc_delta) + abs(second.perc_delta - third.perc_delta)) / 2)
                observ = Observation(first.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.combi_pattern,
                                     None,
                                     first.indexx,
                                     None,
                                     None,
                                     sentence,
                                     self.combi_relevance(rel),
                                     data)
                # save the observation object
                self.observations.append(observ)
                not_found = False

        if len(df_large_dec) >= 2 and not_found:
            # there are at least 2 decreasing
            first = df_large_dec.iloc[0]
            second = df_large_dec.iloc[1]
            if (abs(second.perc_delta) > self.combi_diff_significance) and (abs(first.perc_delta - second.perc_delta) < self.combi_diff_threshold):
                # check whether there is a significant decrease between second and the rest,
                # and between 1 and 2 there is no significant decrease
                # build the sentence
                sentence = f"""In de {first.indexx} waren {first.component} ({first.perc_delta}%) en
                            {second.component} ({second.perc_delta}%) de hardste dalers."""
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
                                     self.combi_relevance(abs(first.perc_delta - second.perc_delta)),
                                     data)
                # save the observation object
                self.observations.append(observ)
                not_found = False

        if len(df_large_dec) >= 1 and not_found:
            # there are at least 1 decreasing
            first = df_large_dec.iloc[0]
            if abs(first.perc_delta) > self.combi_diff_significance:
                # check whether there is a significant increase between 1 and the rest
                # build the sentence
                sentence = f"{first.component} daalde het hardst met {abs(first.perc_delta)} procent."
                # build the observation object
                data = {}
                observ = Observation(first.component,
                                     self.period_begin,
                                     self.period_end,
                                     self.combi_pattern,
                                     first.sector,
                                     first.indexx,
                                     first.perc_delta,
                                     first.abs_delta,
                                     sentence,
                                     self.indiv_relevance(abs(first.perc_delta) + self.combi_diff_threshold),
                                     data)
                # save the observation object
                self.observations.append(observ)
                not_found = False

    def all_fallers(self):
        """Gets all individual components that have decreased in the time period.
        """
        # filter on negative percentages and only get the difference of the end date
        df_inc = self.df[(self.df["perc_delta"] < 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        # loop over all the falling stocks and save the observations
        for index, info in df_inc.iterrows():
            # build the sentence
            sentence = f"Aandeel {info.component} met {abs(info.perc_delta)}% gedaald."
            # build the observation object
            data = {}
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
        self.df.sort_values(by="perc_delta", ascending=True, inplace=True)

    def analyse(self):
        """Runs the analysis over the data.
        """
        # get the amount of days between the start and end date (not including the weekend)
        diff_days = np.busday_count(self.period_begin.strftime("%Y-%m-%d"),
                                    self.period_end.strftime("%Y-%m-%d"),
                                    weekmask=[1, 1, 1, 1, 1, 0, 0])

        self.prep_data(diff_days)
        self.x_largest_decrease()
        self.only_x_decrease()
        self.all_fallers()
