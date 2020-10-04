from datetime import datetime

from NLGengine.observation import Observation
import pandas as pd


class Increase:
    """[summary]
    """
    def __init__(self, df_series: pd.DataFrame, period_beg: datetime, period_end: datetime):
        """[summary]

        Args:
            df_series (pd.DataFrame): [description]
            period_beg (datetime): [description]
            period_end (datetime): [description]
        """
        self.df = df_series
        self.period_begin = period_beg
        self.period_end = period_end
        self.pattern = "stijging"
        self.observations = []
    

    def only_x_increase(self):
        """Checks if there are any stocks that are the only one or ones (2) that have increased in the timeperiod.
        """
        df_only_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df["date"] == self.period_end)]

        if len(df_only_inc) == 1:
            # only 1 stock has been increasing
            info = df_only_inc.iloc[0]
            sentence = f"{info.indexx}, dat profiteert van de onrust op de beurzen, is de enige stijger."
            observ = Observation(info.stock, self.period_begin, self.period_end, "Stijging", sentence, 9)
            self.observations.append(observ)

        if len(df_only_inc) == 2:
            # only 2 stocks have been increasing
            info = df_only_inc.iloc[0:2]
            sentence = f"Op {info.iloc[0].stock} en {info.iloc[1].stock} na dalen alle {info.iloc[0].indexx} fondsen"
            observ = Observation(info.stock, self.period_begin, self.period_end, "Stijging", sentence, 8)
            self.observations.append(observ)


    def x_largest_increase(self):
        """Checks how many (1,2,3) stocks have increased the most in a certain timeperiod.
        """
        # filter on positive percentages and only get the difference of the end date
        df_large_inc = self.df[(self.df["perc_delta"] > 0.0) & (self.df['date'].dt.strftime('%Y-%m-%d') == self.period_end.strftime('%Y-%m-%d'))]

        if len(df_large_inc) >= 1:
            # At least 1 stock increasing
            info = df_large_inc.iloc[0]
            sentence = f"In de {info.indexx} ging {info.stock} aan kop met een winst van {info.perc_delta} procent."
            observ = Observation(info.stock, self.period_begin, self.period_end, "Stijging", sentence, 5)
            self.observations.append(observ)

        if len(df_large_inc) >= 2:
            # At least 2 stocks increasing
            info = df_large_inc.iloc[0:2]
            sentence = f"In de {info.iloc[0].indexx} waren {info.iloc[0].stock} (+{info.iloc[0].perc_delta}%) en {info.iloc[1].stock} (+{info.iloc[1].perc_delta}%) de grootste stijgers."
            observ = Observation(info.iloc[0].stock, self.period_begin, self.period_end, "Stijging", sentence, 5)
            self.observations.append(observ)

        if len(df_large_inc) >= 3:
            # at least 3 stocks increasing
            info = df_large_inc.iloc[0:3]
            sentence = f"{info.iloc[0].stock} (+{info.iloc[0].perc_delta}%), {info.iloc[1].stock} (+{info.iloc[1].perc_delta}%) en {info.iloc[2].stock} (+{info.iloc[2].perc_delta}%) waren de positieve uitschieters."
            observ = Observation(info.iloc[0].stock, self.period_begin, self.period_end, "Stijging", sentence, 5)
            self.observations.append(observ)


    def prep_data(self, period):
        """[summary]

        Args:
            period ([type]): [description]
        """
        self.df["abs_delta"] = 0
        self.df["perc_delta"] = 0
        self.df["date"] = pd.to_datetime(self.df["date"])

        # remove all the indexes themself out of the dataframe
        all_indexes = self.df["indexx"].unique()
        self.df = self.df[~self.df["stock"].isin(all_indexes)]
        
        # get all the unique stocks that are in the dataframe
        all_stocks = self.df["stock"].unique()
        
        for stock in all_stocks:
            # select all the rows from a certain stock
            df_one_stock = self.df[self.df["stock"] == stock]["close"].copy()
            # calculate the absolute difference
            df_abs_diff = df_one_stock.diff()
            # calculate the percentage difference
            df_pct_diff = df_one_stock.pct_change()

            # add both values back in the dataframe
            self.df.loc[df_abs_diff.index, 'abs_delta'] = df_abs_diff.values
            self.df.loc[df_pct_diff.index, 'perc_delta'] = df_pct_diff.values

        # format the percentage difference
        self.df["perc_delta"] = self.df["perc_delta"].apply(lambda x: round(x * 100, 3))

        # drop all rows with NaNs
        self.df.dropna(inplace=True)

        # sort the dataframe by percentage
        self.df.sort_values(by="perc_delta", ascending=False, inplace=True)


    def analyse(self):
        """[summary]
        """
        self.prep_data(1)
        self.x_largest_increase()
        self.only_x_increase()