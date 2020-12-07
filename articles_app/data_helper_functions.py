import csv
import json
import pandas as pd
from datetime import datetime
from articles_app.models import Stocks, Articles, Observations
from articles_app.nlg_queries import find_new_observations, observation_to_database, update_observation

# from articles_app import data_helper_functions as dhf
# dhf.from_csv_to_Stocks(r"articles_app/data/AMX_prices_90_days.csv")


def from_csv_to_Stocks(data_path):
    """[summary]

    Args:
        data_path ([type]): [description]
    """
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
    """[summary]
    """
    period_begin = datetime(year=2020, month=6, day=5)
    period_end = datetime(year=2020, month=10, day=2)

    begin_date = period_begin
    for new_date in pd.date_range(period_begin, period_end).to_list()[1:]:
        if (begin_date.weekday() in [5, 6]) or (new_date.weekday() in [5, 6]):
            pass
        else:
            print(begin_date, new_date)
            find_new_observations(begin_date, new_date, to_db=True, to_prompt=True)
            begin_date = new_date


def update_observs():
    """Reruns all the observations and updates the info of the observation if the observation already exists,
    otherwise adds the new observation to the db.
    """
    period_begin = datetime(year=2020, month=6, day=10)
    period_end = datetime(year=2020, month=10, day=2)

    begin_date = period_begin
    for new_date in pd.date_range(period_begin, period_end).to_list()[1:]:
        if (begin_date.weekday() in [5, 6]) or (new_date.weekday() in [5, 6]):
            pass
        else:
            print(begin_date, new_date)
            # find the observations corresponding to the time period
            observs = find_new_observations(begin_date, new_date, overwrite=True, to_db=False, to_prompt=False, to_list=True)

            # loop over all observations
            for obs in observs:
                # check if an observation already exists in the db
                exists = Observations.objects.filter(
                    pattern=obs.pattern
                ).filter(
                    serie=obs.serie
                ).filter(
                    sector=obs.sector
                ).filter(
                    period_end=obs.period_end
                ).filter(
                    period_begin=obs.period_begin
                ).filter(
                    perc_change=round(obs.perc_change, 2) if obs.perc_change is not None else None
                ).exists()

                if exists:
                    # get the current observation
                    db_observ = Observations.objects.filter(
                        pattern=obs.pattern
                    ).filter(
                        serie=obs.serie
                    ).filter(
                        sector=obs.sector
                    ).filter(
                        period_end=obs.period_end
                    ).filter(
                        period_begin=obs.period_begin
                    ).filter(
                        perc_change=round(obs.perc_change, 2) if obs.perc_change is not None else None
                    )

                    # update the information of the current observation
                    update_observation(db_observ[0], obs)
                    print(f"updated observation {db_observ[0].id}")

                else:
                    # observation doesn't exist, so add it to the db
                    observation_to_database(obs.serie,
                                            obs.period_begin,
                                            obs.period_end,
                                            obs.pattern,
                                            obs.sector,
                                            obs.indexx,
                                            obs.observation,
                                            obs.perc_change,
                                            obs.abs_change,
                                            obs.relevance1,
                                            obs.meta_data)
                    print("observation added to db")

        # update the begin date so the loop continues
        begin_date = new_date


def update_test_cases_file():
    """Gets the test_cases and binds all the chosen observations to the json for redundancy purposes.
    """
    data_file = r"./NLGengine/content_determination/observation_collection.json"
    cases_file = r"./NLGengine/content_determination/test_cases.json"

    # load all the observations
    with open(data_file) as f:
        observations = json.load(f)

    # load all the test_cases
    with open(cases_file) as f:
        test_cases = json.load(f)

    # set the information
    cases = test_cases.get("test_cases")
    test_observs = test_cases.get("observations")

    # loop over all the cases and check for both observations if they already exist
    for case in cases:
        # get the id's
        prev_observ = str(case.get("prev_observ"))
        new_observ = str(case.get("new_observ"))

        # check if prev_observ is in observations
        if prev_observ not in test_observs:
            # observation not yet in observations of test_cases.json
            test_observs[prev_observ] = observations.get(prev_observ)

        if new_observ not in test_observs:
            # observation not yet in observations of test_cases.json
            test_observs[new_observ] = observations.get(new_observ)

    # build the new json file
    data = {
        "test_cases": cases,
        "observations": test_observs
    }

    # write into json
    with open(cases_file, "w") as outfile:
        json.dump(data, outfile)


def test_cases_to_csv():
    """gets all the test cases and its observations and writes it into a csv file.
    """
    pass


def transfer_observations_to_json():
    """gets the dumped data and transfers it into a json file.
    python manage.py dumpdata --exclude=auth --exclude=contenttypes --exclude=articles_app.stocks --exclude=articles_app.articles --exclude=admin --exclude=sessions --exclude=articles_app.comment -o articles_app/data/datadump.json
    """

    data_file = r"./articles_app/data/datadump.json"
    target_file = r"./NLGengine/content_determination/observation_collection.json"

    # open the data_file
    with open(data_file) as f:
        observs_info = json.load(f)

    data = dict()
    for observ in observs_info:
        idd = str(observ.get('pk'))
        info = observ.get('fields')
        data[idd] = info

    # write into json
    with open(target_file, "w") as outfile:
        json.dump(data, outfile)
