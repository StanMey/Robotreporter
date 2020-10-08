from articles_app.models import Observations, Articles, Stocks
from NLGengine.observation import Observation
from NLGengine.analyse import Analyse

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def build_article(user_name):
    """
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
    article.title = content[:50]
    article.content = content
    article.date = datetime.now()
    article.author = user_name
    article.AI_version = 1.0
    article.save()

    return article.id


def find_new_observations(to_db=False, to_prompt=False):
    """[summary]

    Args:
        to_db (bool, optional): [description]. Defaults to False.
        to_prompt (bool, optional): [description]. Defaults to False.
    """
    all_observations = []
    period_begin = datetime(year=2020, month=9, day=24)
    period_end = datetime(year=2020, month=9, day=25)

    # check if this period in observations has already been asked before
    observ_exists = Observations.objects.filter(period_begin=period_begin).filter(period_end=period_end).exists()
    if not observ_exists:
        # retrieve all data over the stocks in this period
        data = Stocks.objects.filter(date__range=(period_begin, period_end))
        # convert the data to a dataframe
        q = data.values('component', 'indexx', 'date', 's_close')
        df_data = pd.DataFrame.from_records(q)

        # prepare the data for the analysis
        df_data.rename(columns={"s_close" : "close"}, inplace=True)
        df_data['close'] = df_data['close'].astype('float')

        # run the analyser to find observations
        analyse = Analyse(df_data, period_begin, period_end)
        analyse.find_new_observations()
        all_observations.extend(analyse.observations)
    
    # check if the week has already been observed
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
            df_data.rename(columns={"s_close" : "close"}, inplace=True)
            df_data['close'] = df_data['close'].astype('float')
            
            # run the analyser to find observations
            analyse = Analyse(df_data, *period)
            analyse.find_weekly_observations()
            all_observations.extend(analyse.observations)
    
    if to_db:
        # write all the found observations into the database
        for observ in all_observations:
            observation_to_database(observ.serie, observ.period_begin, observ.period_end, observ.pattern, observ.observation, observ.relevance)

    if to_prompt:
        # write all the found observations to the prompt
        for observ in all_observations:
            print(observ)
            print(observ.period_begin, observ.period_end)


def observation_to_database(serie, period_begin, period_end, pattern, observation, relevance):
    """Writes an observation to the database.

    Args:
        serie ([type]): [description]
        period_begin ([type]): [description]
        period_end ([type]): [description]
        pattern ([type]): [description]
        observation ([type]): [description]
        relevance ([type]): [description]
    """
    observ = Observations()
    observ.serie = serie
    observ.period_begin = period_begin
    observ.period_end = period_end
    observ.pattern = pattern
    observ.observation = observation
    observ.relevance = relevance
    # save to the db
    observ.save()