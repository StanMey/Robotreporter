from articles_app.models import Observations, Articles, Stocks
from NLGengine.observation import Observation
from NLGengine.analyse import Analyse

import numpy as np
import pandas as pd
from datetime import datetime


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


def find_new_observations():
    """
    """
    data_path = r"./articles_app/test.csv"
    df_data = pd.read_csv(data_path, sep=";")

    period_begin = datetime(year=2020, month=9, day=28)
    period_end = datetime(year=2020, month=9, day=29)

    analyse = Analyse(df_data, period_begin, period_end)
    observs = analyse.find_new_observations()

    for obs in observs:
        observation_to_database(obs.serie, obs.period_begin, obs.period_end, obs.pattern, obs.observation, obs.relevance)
    return observs


def observation_to_database(serie, period_begin, period_end, pattern, observation, relevance):
    """Writes an observation to the database.
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