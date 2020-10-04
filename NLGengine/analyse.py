import sys
import csv
import pandas as pd
from datetime import datetime

from NLGengine.patterns.increase_pattern import Increase
from .observation import Observation


class Analyse:
    def __init__(self, data, period_beg, period_end):
        self.data = data
        self.period_begin = period_beg
        self.period_end = period_end
        self.observations = []


    def find_new_observations(self):

        increase = Increase(self.data, self.period_begin, self.period_end)
        increase.analyse()
        return increase.observations

if __name__ == "__main__":
    print("tadaaaaa")
    # data_path = r"test.csv"

    # df_data = pd.read_csv(data_path, sep=";")

    # period_begin = datetime(year=2020, month=9, day=28)
    # period_end = datetime(year=2020, month=9, day=29)
    # print(type(period_begin))

    # increase = Increase(df_data, period_begin, period_end)
    # increase.prep_data(1)
    # increase.x_largest_increase()
    # print(increase.period_begin)

    # for observ in increase.observations:
    #     print(observ.observation)
    #     observ.to_database()
