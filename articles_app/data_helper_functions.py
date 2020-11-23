import csv
import pandas as pd
from datetime import datetime
from articles_app.models import Stocks, Articles, Observations
from articles_app.nlg_queries import find_new_observations

# from articles_app import data_helper_functions as dhf
# dhf.from_csv_to_Stocks(r"articles_app/data/AMX_prices_90_days.csv")


def from_csv_to_Stocks(data_path):

    with open(data_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                stock = Stocks()
                stock.indexx = row[7]
                stock.component = row[0]
                stock.volume = row[1]
                stock.s_open = row[2]
                stock.s_high = row[3]
                stock.s_low = row[4]
                stock.s_close = row[5]
                stock.date = datetime.strptime(row[6], '%d-%m-%Y')

                stock.save()

                line_count += 1
        print(f'Processed {line_count} lines.')


def fill_observations():
    period_begin = datetime(year=2020, month=6, day=10)
    period_end = datetime(year=2020, month=10, day=2)

    begin_date = period_begin
    for new_date in pd.date_range(period_begin, period_end).to_list()[1:]:
        if (begin_date.weekday() in [5, 6]) or (new_date.weekday() in [5, 6]):
            pass
        else:
            print(begin_date, new_date)
            find_new_observations(begin_date, new_date, to_db=True, to_prompt=True)
            begin_date = new_date


def remove_observations():
    Observations.objects.all().delete()


def update_observs():
    period_begin = datetime(year=2020, month=8, day=10)
    period_end = datetime(year=2020, month=10, day=2)


def test_observs():
    Observations.objects.all().delete()

    period_begin = datetime(year=2020, month=8, day=10)
    period_end = datetime(year=2020, month=10, day=2)

    begin_date = period_begin
    for new_date in pd.date_range(period_begin, period_end).to_list()[1:]:
        if (begin_date.weekday() in [5, 6]) or (new_date.weekday() in [5, 6]):
            pass
        else:
            print(begin_date, new_date)
            find_new_observations(begin_date, new_date, to_db=True, to_prompt=True)
            begin_date = new_date
