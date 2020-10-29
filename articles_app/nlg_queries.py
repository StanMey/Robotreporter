from articles_app.models import Observations, Articles, Stocks
from NLGengine.observation import Observation
from NLGengine.analyse import Analyse

import pandas as pd
import json
from datetime import datetime, timedelta


def build_article(user_name, filters, bot=False):
    """Build an article based on the most recent and relevant observations.

    Args:
        user_name (String): The name of the user that is generating the article
        filters (dict): The filters that has been chosen for the selection of the Observations

    Returns:
        int: The id of the generated article
    """
    # current_date = datetime.now().replace(hour=00, minute=00, second=00, microsecond=0)
    current_date = datetime(year=2020, month=9, day=24)
    begin_date = current_date - timedelta(10)

    # retrieve 3 random observations from the Observations table
    observation_set = list(Observations.objects.filter(
                                    period_begin__gte=begin_date
                           ).order_by('-period_end', '-relevance')[:10])

    sentences = []
    for observ in observation_set[:5]:
        print(observ.period_end, observ.relevance, observ.observation)
        sentences.append(f"{observ.observation} (rel: {observ.relevance})")

    content = " ".join(sentences)
    print(content)

    # get the meta data and save it into the article
    meta = {}
    meta["manual"] = filters.get("manual")
    meta["filters"] = {}

    for x in ["Sector", "Periode"]:
        selection = filters.get(x)
        print(selection)
        if (selection.get("total") != len(selection.get("options"))) and (selection.get("options") != []):
            meta["filters"][x] = selection.get("options")
        else:
            meta["filters"][x] = "Alles"

    article = Articles()
    article.title = f"Beurs update {datetime.now().strftime('%d %b')}"
    article.content = content
    article.date = datetime.now()
    article.AI_version = 1.2
    article.meta_data = meta
    if bot:
        article.author = "nieuwsbot"
    else:
        article.author = user_name
    article.save()

    return article.id


def construct_article(user_name, content, filters):
    """Build an article based on a sentence construction the user has made.

    Args:
        user_name (String): The name of the user that is generating the article
        content (list): The array with all the chosen observations by the user
        filters (dict): The filters that has been chosen for the selection of the Observations

    Returns:
        int: The id of the newly generated article
    """
    sentences = []
    for observ in content:
        sentences.append(f"{observ[4]} (rel: {observ[3]})")

    content = " ".join(sentences)

    # get the meta data and save it into the article
    meta = {}
    meta["manual"] = filters.get("manual")
    meta["filters"] = {}

    for x in ["Sector", "Periode"]:
        selection = filters.get(x)
        if (selection.get("total") != len(selection.get("options"))) and (selection.get("options") != []):
            meta["filters"][x] = selection.get("options")
        else:
            meta["filters"][x] = "Alles"

    article = Articles()
    # TODO get the max date
    article.title = f"Beurs update {datetime.now().strftime('%d %b')}"
    article.content = content
    article.date = datetime.now()
    article.AI_version = 1.2
    article.meta_data = meta
    article.author = user_name
    article.save()

    return article.id


def testing_find_observs():
    """Small function for testing and development purposes.
    """
    # period_begin = datetime(year=2020, month=7, day=14)
    period_begin = datetime(year=2020, month=9, day=16)
    period_end = datetime(year=2020, month=9, day=17)

    find_new_observations(period_begin, period_end, to_prompt=True, overwrite=True)


def find_new_observations(period_begin: datetime, period_end: datetime, overwrite=False, to_db=False, to_prompt=False):
    """Runs all functions to find observations, collects the observations and deals with them in the proper way.

    Args:
        overwrite (bool, optional) : Decide whether duplicate observations are handled. Defaults to False
        to_db (bool, optional): Decide whether the new observations are to be written into the database. Defaults to False.
        to_prompt (bool, optional): Decide whether the new observations are to be written to the prompt. Defaults to False.
    """
    all_observations = []

    all_observations.extend(run_period_observations(period_begin, period_end, overwrite))
    all_observations.extend(run_week_observations(period_begin, period_end, overwrite))
    all_observations.extend(run_trend_observations(period_end, 14, overwrite))

    if to_db:
        # write all the found observations into the database
        for observ in all_observations:
            observation_to_database(observ.serie, observ.period_begin, observ.period_end, observ.pattern, observ.observation, observ.relevance, observ.meta_data)

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

        # load in the sector data and add it to the dataframe
        with open(r"./articles_app/data/sectorcompany.json") as f:
            sector_info = json.load(f)
        df_data["sector"] = df_data["component"].apply(lambda x: sector_info.get(x))
        df_data.dropna(inplace=True)

        # run the analyser to find observations
        analyse = Analyse(df_data, period_begin, period_end)
        analyse.find_period_observations()
        observs.extend(analyse.observations)

    return observs


def run_week_observations(period_begin, period_end, overwrite):
    """
    Check if a whole week has already been observed,
    if not gets all the weeks in the range of the beginning and the end of the period and runs the analysis.

    Args:
        period_begin (datetime): The date with the beginning of the period
        period_end (datetime): The date with the end of the period
        overwrite (bool): If duplicate observations can be made

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

    if overwrite:
        open_periods = all_periods
    else:
        # check for every week if there is already an observation made
        open_periods = [x for x in all_periods if not Observations.objects.filter(pattern="week").filter(period_begin=x[0]).filter(period_end=x[1]).exists()]

    # run a new observation if the week hasn't been observerd
    if len(open_periods) > 0:
        for period in open_periods:
            print(period)
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


def run_trend_observations(period_end, delta_days, overwrite):
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

    if overwrite:
        observs.extend(analyse.observations)
    else:
        observs.extend([x for x in analyse.observations if not Observations.objects.filter(pattern=x.pattern).filter(serie=x.serie).filter(period_end=x.period_end).filter(period_end=x.period_end).exists()])

    return observs


def observation_to_database(serie, period_begin, period_end, pattern, observation, relevance, meta):
    """Writes an observation to the database.

    Args:
        serie (String): The name of the serie over which an observation has been made
        period_begin (datetime): The date with the beginning of the period of the observation
        period_end (datetime): The date with the end of the period of the observation
        pattern (String): A string with the pattern that was found
        observation (String): A string with the sentence of the observation
        relevance (Float): The relevance the observation holds
    """
    try:
        observ = Observations()
        observ.serie = serie
        observ.period_begin = period_begin
        observ.period_end = period_end
        observ.pattern = pattern
        observ.observation = observation
        observ.relevance = relevance
        observ.meta_data = meta
        # save to the db
        observ.save()
    except Exception as e:
        print(f"{e}\n{observation}\n{meta}\n")
