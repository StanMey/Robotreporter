from django.core.management.base import BaseCommand
from articles_app.data_helper_functions import from_csv_to_stocks, update_observs
from datetime import datetime

import pandas as pd


# the links with the csv files holding the stock information
AMX_csv_90_file = r"articles_app/data/AMX_prices_90_days.csv"
AMX_csv_followup_file = r"articles_app/data/AMX_prices.csv"


class Command(BaseCommand):
    help = "Setup for running the site and reporter on localhost (only run in the beginning!)"

    def handle(self, *args, **options):
        try:
            # load the stock info from the csv files into the db
            from_csv_to_stocks(AMX_csv_90_file)
            from_csv_to_stocks(AMX_csv_followup_file)

            # get the min and max date from the csv files
            min_date, max_date = get_min_max_date(AMX_csv_90_file, AMX_csv_followup_file)
            # find all the possible observations during that timespan
            update_observs(min_date, max_date)

        except Exception as e:
            print(e)


def get_min_max_date(file_1, file_2):
    """Gets the min and max date from the two csv files.

    Args:
        file_1 (str): The source path of the first csv file
        file_2 (str): The source path of the second csv file

    Returns:
        tuple: Returns a tuple with the min and max date
    """
    df1 = pd.read_csv(file_1, sep=";")
    df1["date"] = pd.to_datetime(df1["date"])
    min_date = min(df1['date'])

    df2 = pd.read_csv(file_2, sep=";")
    df2["date"] = pd.to_datetime(df2["date"])
    max_date = max(df2["date"])

    return min_date, max_date
