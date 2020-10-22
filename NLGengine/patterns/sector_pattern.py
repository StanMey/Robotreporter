from datetime import datetime
from NLGengine.observation import Observation
from NLGengine.relevance import Relevance

import pandas as pd
import numpy as np


class Sector:
    """A class that holds methods to find increase based patterns in timeseries data in a period.
    https://www.aandelencheck.nl/aandelen/
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

        self.pattern = "sector"
        self.relevance = lambda x: abs(x)
        self.observations = []

    def analyse_general_sector_performance(self):
        """[summary]
        """
        # TODO check what extra to safe in the meta_data
        # TODO check calculation for relevance
        # get all unique sectors
        sectors = self.df["sector"].unique()

        for sector in sectors:
            # select all the rows from a certain sector
            df_one_sector = self.df[self.df["sector"] == sector][["component", "perc_delta", "indexx"]].copy()

            if (df_one_sector["perc_delta"] > 0.0).all():
                # all components in the sector have increased
                # collect the additional metadata
                data = {
                        "component": list(df_one_sector.component),
                        "perc_change": list(df_one_sector.perc_delta),
                        "sector": sector,
                        "relev": [self.relevance(x.perc_delta) for (_, x) in df_one_sector.iterrows()]
                    }
                # save the observation
                sentence = f"De bedrijven in de sector {sector} in de {df_one_sector.iloc[0].indexx} deden het goed vandaag."
                observ = Observation(df_one_sector.iloc[0].component, self.period_begin, self.period_end, self.pattern, sentence, self.relevance(np.mean(df_one_sector.perc_delta)), data)
                self.observations.append(observ)

            if (df_one_sector["perc_delta"] < 0.0).all():
                # all components in the sector have decreased
                # collect the additional metadata
                data = {
                        "component": list(df_one_sector.component),
                        "perc_change": list(df_one_sector.perc_delta),
                        "sector": sector,
                        "relev": [self.relevance(x.perc_delta) for (_, x) in df_one_sector.iterrows()]
                    }
                # save the observation
                sentence = f"De bedrijven in de sector {sector} in de {df_one_sector.iloc[0].indexx} deden het niet goed vandaag en daalden allemaal."
                observ = Observation(df_one_sector.iloc[0].component, self.period_begin, self.period_end, self.pattern, sentence, self.relevance(np.mean(df_one_sector.perc_delta)), data)
                self.observations.append(observ)

    def analyse_component_sector_performance(self):
        """[summary]
        """
        # get all the unique components that are in the dataframe
        all_components = self.df["component"].unique()

        for component in all_components:
            # get the row of the current component
            current_comp = self.df.loc[self.df["component"] == component]
            # get the sector of the current component
            current_sector = self.df.loc[self.df["component"] == component]["sector"].item()
            # get the rest of the rows with the same sector but not the same component
            sector_peers = self.df.loc[(self.df["component"] != component) & (self.df["sector"] == current_sector)]

            if len(sector_peers) == 0:
                # no other sector peers in the current index
                pass
            else:
                # has other sector peers in the current index
                if (current_comp["perc_delta"].item() > sector_peers["perc_delta"]).all():
                    # component has the highest percentage relative to other components in the sector
                    # collect the additional metadata
                    data = {
                            "component": component,
                            "perc_change": current_comp.perc_delta.item(),
                            "sector": current_sector,
                            "relev": self.relevance(current_comp.perc_delta.item())
                        }
                    # save the observation
                    sentence = f"{component} presteerde bovenmaats ten opzichte van sectorgenoten in de {current_comp.indexx.item()}."
                    observ = Observation(component, self.period_begin, self.period_end, self.pattern, sentence, self.relevance(np.mean(current_comp.perc_delta.item())), data)
                    self.observations.append(observ)

                if (current_comp["perc_delta"].item() < sector_peers["perc_delta"]).all():
                    # component has the lowest percentage relative to other components in the sector
                    # collect the additional metadata
                    data = {
                            "component": component,
                            "perc_change": current_comp.perc_delta.item(),
                            "sector": current_sector,
                            "relev": self.relevance(current_comp.perc_delta.item())
                        }
                    # save the observation
                    sentence = f"{component} presteerde ondermaats ten opzichte van sectorgenoten in de {current_comp.indexx.item()}."
                    observ = Observation(component, self.period_begin, self.period_end, self.pattern, sentence, self.relevance(np.mean(current_comp.perc_delta.item())), data)
                    self.observations.append(observ)

    def prep_data(self, period: int):
        """Prepares and wrangles the data so the analyses can be run on it.

        Args:
            period (integer): The amount of days between the beginning of the period and the end
        """
        self.df["perc_delta"] = 0
        self.df["date"] = pd.to_datetime(self.df["date"])

        # order all data by date in ascending order, because .diff() doesn't take in the date
        self.df.sort_values('date', inplace=True)

        # get all the unique components that are in the dataframe
        all_components = self.df["component"].unique()

        for component in all_components:
            # select all the rows from a certain component
            df_one_component = self.df[self.df["component"] == component]["close"].copy()
            # calculate the percentage difference
            df_pct_diff = df_one_component.pct_change(periods=period)

            # add both values back in the dataframe
            self.df.loc[df_pct_diff.index, 'perc_delta'] = df_pct_diff.values

        # format the percentage difference
        self.df["perc_delta"] = self.df["perc_delta"].apply(lambda x: round(x * 100, 2))

        # drop all rows with NaNs
        self.df.dropna(inplace=True)

    def analyse(self):
        """Run the analyses of the Trend pattern.
        """
        self.prep_data(1)
        self.analyse_general_sector_performance()
        self.analyse_component_sector_performance()
