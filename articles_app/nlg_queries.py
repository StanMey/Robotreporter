from articles_app.models import Observations, Articles, Stocks
from NLGengine.observation import Observation
from NLGengine.analyse import Analyse

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def build_article(user_name):
    """Build an article based on the most recent and relevant observations.

    Args:
        user_name (String): The name of the user that is generating the article

    Returns:
        int: The id of the generated article
    """
    # retrieve 3 random observations from the Observations table
    observation_set = list(Observations.objects.order_by('-period_end')[:10])
    # shuffle the sentences inplace
    np.random.shuffle(observation_set)

    sentences = []
    for observ in observation_set[:3]:
        sentences.append(observ.observation)

    content = " ".join(sentences)

    article = Articles()
    article.title = f"Beurs update {datetime.now().strftime('%d %b')}"
    article.content = content
    article.date = datetime.now()
    article.author = user_name
    article.AI_version = 1.0
    article.save()

    return article.id


def find_new_observations(overwrite=False, to_db=False, to_prompt=False):
    """Runs all functions to find observations, collects the observations and deals with them in the proper way.

    Args:
        overwrite (bool, optional) : Decide whether duplicate observations are handled. Defaults to False
        to_db (bool, optional): Decide whether the new observations are to be written into the database. Defaults to False.
        to_prompt (bool, optional): Decide whether the new observations are to be written to the prompt. Defaults to False.
    """
    all_observations = []
    period_begin = datetime(year=2020, month=9, day=16)
    period_end = datetime(year=2020, month=9, day=17)

    run_period_observations(period_begin, period_end, overwrite)
    run_week_observations(period_begin, period_end)
    run_trend_observations(period_end, 14)

    if to_db:
        # write all the found observations into the database
        for observ in all_observations:
            observation_to_database(observ.serie, observ.period_begin, observ.period_end, observ.pattern, observ.observation, observ.relevance)

    if to_prompt:
        # write all the found observations to the prompt
        for observ in all_observations:
            print(observ)
            print(observ.period_begin, observ.period_end)


def run_period_observations(period_begin, period_end, overwrite):
    """
    Check if the given period has already been observed,
    if not get all the relevant data and run the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period
        overwrite (bool): If duplicate observations can be made

    Returns:
        list: A list with the observations found
    """
    observs = []
    # check if this period in observations has already been asked before
    observ_exists = Observations.objects.filter(period_begin=period_begin).filter(period_end=period_end).exists()
    if not observ_exists or overwrite:
        # retrieve all data over the stocks in this period
        data = Stocks.objects.filter(date__range=(period_begin, period_end))
        # convert the data to a dataframe
        q = data.values('component', 'indexx', 'date', 's_close')
        df_data = pd.DataFrame.from_records(q)

        # prepare the data for the analysis
        df_data.rename(columns={"s_close": "close"}, inplace=True)
        df_data['close'] = df_data['close'].astype('float')

        # run the analyser to find observations
        analyse = Analyse(df_data, period_begin, period_end)
        analyse.find_new_observations()
        observs.extend(analyse.observations)

    return observs


def run_week_observations(period_begin, period_end):
    """
    Check if a whole week has already been observed,
    if not gets all the weeks in the range of the beginning and the end of the period and runs the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period

    Returns:
        list: A list with the observations found
    """
    observs = []
    # get all dates in the period range and find all unique weeknumbers
    all_dates = list(pd.date_range(period_begin, period_end))
    weeknumbers = list(set([x.isocalendar()[:2] for x in all_dates]))

    # get all the begin and end dates of the observable week (so the date of the monday and friday)
    # https://stackoverflow.com/questions/17087314/get-date-from-week-number
    all_periods = []
    for numb in weeknumbers:
        mon_date = datetime.strptime(f"{numb[0]}-W{numb[1]}" + '-1', '%G-W%V-%u')
        fri_date = mon_date + timedelta(4)
        all_periods.append((mon_date, fri_date))

    # check for every week if there is already an observation made
    open_periods = [x for x in all_periods if not Observations.objects.filter(pattern="week").filter(period_begin=x[0]).filter(period_end=x[1]).exists()]

    # run a new observation if the week hasn't been observerd
    if len(open_periods) > 0:
        for period in open_periods:

            # retrieve all data over the stocks in this period
            data = Stocks.objects.filter(date__range=period)
            # convert the data to a dataframe
            q = data.values('component', 'indexx', 'date', 's_close')
            df_data = pd.DataFrame.from_records(q)

            # prepare the data for the analysis
            df_data.rename(columns={"s_close": "close"}, inplace=True)
            df_data['close'] = df_data['close'].astype('float')

            # run the analyser to find observations
            analyse = Analyse(df_data, *period)
            analyse.find_weekly_observations()
            observs.extend(analyse.observations)
    return observs


def run_trend_observations(period_end, delta_days):
    """Gets all the data between the beginning of the period and the end of the period and runs a trend analysis.

    Args:
        period_end (datetime): The date with the end of the period
        delta_days (int): Indicates how far back the data has to be retrieved

    Returns:
        list: A list with the observations found
    """
    observs = []
    # get the data for the trend analyses
    end_date = period_end
    begin_date = period_end - timedelta(delta_days)

    # retrieve all data over the stocks in this period
    data = Stocks.objects.filter(date__range=(begin_date, end_date))
    # convert the data to a dataframe
    q = data.values('component', 'indexx', 'date', 's_close')
    df_data = pd.DataFrame.from_records(q)

    # prepare the data for the analysis
    df_data.rename(columns={"s_close": "close"}, inplace=True)
    df_data['close'] = df_data['close'].astype('float')

    # run the analyser to find observations
    analyse = Analyse(df_data, begin_date, end_date)
    analyse.find_trend_observations()
    observs.extend(analyse.observations)

    return observs


def observation_to_database(serie, period_begin, period_end, pattern, observation, relevance):
    """Writes an observation to the database.

    Args:
        serie (String): The name of the serie over which an observation has been made
        period_begin (datetime): The date with the beginning of the period of the observation
        period_end (datetime): The date with the end of the period of the observation
        pattern (String): A string with the pattern that was found
        observation (String): A string with the sentence of the observation
        relevance (Float): The relevance the observation holds
    """
    observ = Observation()
    observ.serie = serie
    observ.period_begin = period_begin
    observ.period_end = period_end
    observ.pattern = pattern
    observ.observation = observation
    observ.relevance = relevance
    # save to the db
    observ.save()
