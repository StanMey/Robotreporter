from datetime import datetime

from NLGengine.observation import Observation
import pandas as pd
import numpy as np


class Decrease:
    """[summary]
    """
    def __init__(self, df_data: pd.DataFrame, period_beg: datetime, period_end: datetime):
        """[summary]

        Args:
            df_data (pd.DataFrame): [description]
            period_beg (datetime): [description]
            period_end (datetime): [description]
        """
        assert isinstance(df_data, pd.DataFrame), "df_data should be a pandas Dataframe"
        assert set(["component", "indexx", "close", "date"]).issubset(df_data.columns), "missing columns in dataset"
        self.df = df_data

        assert isinstance(period_beg, datetime), "period_beg should be a datetime object"
        assert isinstance(period_end, datetime), "period_end should be a datetime object"
        assert period_beg < period_end, "period_begin is greater than period_end"
        self.period_begin = period_beg
        self.period_end = period_end

        self.pattern = "daling"
        self.observations = []
    

    def only_x_decrease(self):
        """Checks if there are any components that are the only one or ones (2) that have decreased in the timeperiod.
        """
        # only select the components that are negative
        df_only_dec = self.df[(self.df["perc_delta"] < 0.0) & (self.df["date"].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_only_dec) == 1:
            # only 1 component has been decreasing
            info = df_only_dec.iloc[0]
            sentence = f"{info.component} was vandaag met -{info.perc_delta} procent de enige daler"
            observ = Observation(info.component, self.period_begin, self.period_end, self.pattern, sentence, 9)
            self.observations.append(observ)

        if len(df_only_dec) == 2:
            # only 2 components have been decreasing
            info = df_only_dec.iloc[0:2]
            sentence = f"Op {info.iloc[0].component} en {info.iloc[1].component} na stegen alle fondsen"
            observ = Observation(info.component, self.period_begin, self.period_end, self.pattern, sentence, 8)
            self.observations.append(observ)


    def x_largest_decrease(self):
        """Checks how many (1,2,3) components have decreased the most in a certain timeperiod.
        """
        # filter on negative percentages and only get the difference of the end date
        df_large_dec = self.df[(self.df["perc_delta"] < 0.0) & (self.df['date'].dt.strftime('%d-%m-%Y') == self.period_end.strftime('%d-%m-%Y'))]

        if len(df_large_dec) >= 1:
            # At least 1 component decrease
            info = df_large_dec.iloc[0]
            sentence = f"{info.component} daalde het hardst met {info.perc_delta} procent."
            observ = Observation(info.component, self.period_begin, self.period_end, self.pattern, sentence, 5)
            self.observations.append(observ)

        if len(df_large_dec) >= 2:
            # At least 2 components decreasing
            info = df_large_dec.iloc[0:2]
            sentence = f"In de {info.iloc[0].indexx} waren {info.iloc[0].component} ({info.iloc[0].perc_delta}%) en {info.iloc[1].component} ({info.iloc[1].perc_delta}%) de hardste dalers."
            observ = Observation(info.iloc[0].component, self.period_begin, self.period_end, self.pattern, sentence, 5)
            self.observations.append(observ)

        if len(df_large_dec) >= 3:
            # at least 3 components decreasing
            info = df_large_dec.iloc[0:3]
            sentence = f"{info.iloc[0].component} ({info.iloc[0].perc_delta}%), {info.iloc[1].component} ({info.iloc[1].perc_delta}%) en {info.iloc[2].component} ({info.iloc[2].perc_delta}%) waren de negatieve uitschieters."
            observ = Observation(info.iloc[0].component, self.period_begin, self.period_end, self.pattern, sentence, 5)
            self.observations.append(observ)


    def prep_data(self, period: int):
        """[summary]

        Args:
            period (integer): [description]
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
        """[summary]
        """
        # get the amount of days between the start and end date (not including the weekend)
        diff_days = np.busday_count(self.period_begin.strftime("%Y-%m-%d"), self.period_end.strftime("%Y-%m-%d"), weekmask=[1,1,1,1,1,0,0])

        self.prep_data(diff_days)
        self.x_largest_decrease()
        self.only_x_decrease()