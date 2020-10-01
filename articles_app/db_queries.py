from datetime import datetime
from django.db.models import Max, Min
from .models import Stocks, Articles, Observations
import json


def get_all_data_series():
    """[summary]

    Returns:
        [type]: [description]
    """
    # https://gist.github.com/ryanpitts/1304725
    model_min_set = Stocks.objects.values('component').annotate(min_date=Min('date')).order_by()

    model_max_set = [row for row in Stocks.objects.raw("""SELECT S.id, S.component, S.date, S.s_close
                                    FROM articles_app_stocks S INNER JOIN (
                                        SELECT component, MAX(date) AS ddate
                                        from articles_app_stocks
                                        GROUP BY component) AS B ON S.component = B.component AND S.date = B.ddate""")]

    data = {}
    for i in range(len(model_max_set)):
        component_max = model_max_set[i].component
        component_min = model_min_set[i].get("component")

        if component_max not in data:
            data[component_max] = {}
        if component_min not in data:
            data[component_min] = {}
        
        data[component_min]["min_date"] = model_min_set[i].get("min_date").strftime("%d-%m-%Y")
        data[component_max]["max_date"] = model_max_set[i].date.strftime("%d-%m-%Y")
        data[component_max]["close"] = float(model_max_set[i].s_close)
    
    return data


def get_data_serie_close(serie_name):
    """[summary]

    Args:
        serie_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    # get all the close data from a certain serie
    close_data = Stocks.objects.filter(component__exact=serie_name)

    data = []

    # format the data into a json format
    for data_point in close_data:
        point = {
            "date": data_point.date.strftime("%d-%m-%Y"),
            "value": float(data_point.s_close)
        }
        data.append(point)
    
    return data


def get_latest_observations():
    """[summary]

        Returns:
        [type]: [description]
    """
    # get all the latest observations info
    latest_observations = Observations.objects.order_by('-period_end', '-period_begin')[:100]

    data = []

    # format the data into a json format
    for observation in latest_observations:
        point = {
            "serie": observation.serie,
            "period": "{0} / {1}".format(observation.period_begin.strftime("%d-%m-%Y"), observation.period_end.strftime("%d-%m-%Y")),
            "pattern": observation.pattern,
            "observation": observation.observation
        }
        data.append(point)
    return data


def get_relevance_observations():
    """[summary]

        Returns:
        [type]: [description]
    """
    # get all the latest observations info
    relev_observations = Observations.objects.order_by('-period_end', 'relevance', '-period_begin')[:100]
    
    data = []

    # format the data into a json format
    for observation in relev_observations:
        point = {
            "serie": observation.serie,
            "period": "{0} / {1}".format(observation.period_begin.strftime("%d-%m-%Y"), observation.period_end.strftime("%d-%m-%Y")),
            "pattern": observation.pattern,
            "observation": observation.observation,
            "relevance": observation.relevance
        }
        data.append(point)
    return data


def get_articles_set(amount):
    """[summary]

    Args:
        amount ([type]): [description]

    Returns:
        [type]: [description]
    """
    articles_set = Articles.objects.order_by('-date')[:amount]

    data = {}
    count = 1
    for article in articles_set:
        art = {}
        art["article_id"] = article.id
        art["title"] = article.title
        art["content"] = article.content
        art["date_show"] = article.date.strftime("%d %b %Y")
        art["date_whole"] = article.date.strftime("%d-%m-%Y, %H:%M:%S")
        art["author"] = article.author
        art["AI_version"] = article.AI_version
        data[count] = art
        count += 1
    
    return data


def get_article(article_id):
    """[summary]

    Args:
        article_id ([type]): [description]

    Returns:
        [type]: [description]
    """

    selected_article = Articles.objects.get(id=article_id)

    article = {}
    article["article_id"] = selected_article.id
    article["title"] = selected_article.title
    article["content"] = selected_article.content
    article["date_show"] = selected_article.date.strftime("%d %b %Y")
    article["date_whole"] = selected_article.date.strftime("%m-%d-%Y, %H:%M:%S")
    article["author"] = selected_article.author
    article["AI_version"] = selected_article.AI_version

    return article