from django.db.models import Min
from .models import Stocks, Articles, Observations
import articles_app.utils as util
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

    # load in the sector data
    with open(r"./articles_app/data/sectorcompany.json") as f:
        sector_info = json.load(f)

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
        # add the sector
        data[component_min]["sector"] = sector_info.get(component_min)

    return data


def get_data_serie_close(serie_name):
    """[summary]

    Args:
        serie_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    # get all the close data from a certain serie
    close_data = Stocks.objects.filter(component__exact=serie_name).order_by("-date")

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
    latest_observations = Observations.objects.order_by('-period_end', '-period_begin')[:200]

    data = []

    # format the data into a json format
    for observation in latest_observations:

        # get all the series the observation is based on
        if type(observation.meta_data.get("component")) == list:
            serie = ", ".join(observation.meta_data.get("component"))
        else:
            serie = observation.serie

        point = {
            "serie": serie,
            "period": "{0} / {1}".format(observation.period_end.strftime("%d-%m-%Y"), observation.period_begin.strftime("%d-%m-%Y")),
            "pattern": observation.pattern,
            "observation": observation.observation
        }
        data.append(point)
    return data


def get_available_observ_filters():
    """[summary]

        Returns:
        [type]: [description]
    """
    unique_series = list(Observations.objects.order_by('serie').values_list('serie', flat=True).distinct())
    unique_patterns = list(Observations.objects.values_list('pattern', flat=True).distinct())

    # load in the sector data
    with open(r"./articles_app/data/sectorcompany.json") as f:
        sector_info = json.load(f)

    data = {}
    data["Serie"] = unique_series
    data["Sector"] = sorted(list(set(list(sector_info.values()))))
    data["Patroon"] = unique_patterns
    months = util.retrieve_filterable_months(True)
    data["Periode"] = ["vorige dag", "deze week", "vorige week", *months]
    return data


def get_available_relev_filters():
    """[summary]

        Returns:
        [type]: [description]
    """
    # load in the sector data
    with open(r"./articles_app/data/sectorcompany.json") as f:
        sector_info = json.load(f)

    data = {}
    data["Sector"] = sorted(list(set(list(sector_info.values()))))
    months = util.retrieve_filterable_months(True)
    data["Periode"] = ["vorige dag", "deze week", "vorige week", *months]
    return data


def get_filtered_observations(filters):
    """[summary]

    Args:
        filters ([type]): [description]

    Returns:
        [type]: [description]
    """
    # get all the observations
    queries = Observations.objects.order_by("-period_end")

    # check if filters on pattern are selected
    patterns = filters.get("Patroon")
    if (patterns.get("total") != len(patterns.get("options"))) and (patterns.get("options") != []):
        queries = queries.filter(pattern__in=patterns.get("options"))

    # check if filters on serie are selected
    series = filters.get("Serie")
    if (series.get("total") != len(series.get("options"))) and (series.get("options") != []):
        queries = queries.filter(serie__in=series.get("options"))

    # check if filters on periode are selected
    periods = filters.get("Periode")
    if periods.get("options") != []:
        # get the max and min range of the period
        period_range = util.get_period_range(periods.get("options"))
        # apply the filter
        queries = queries.filter(period_end__range=period_range)

    # check if filters on sector are selected
    sectors = filters.get("Sector")
    if (sectors.get("total") != len(sectors.get("options"))) and (sectors.get("options") != []):
        # load in the sector data
        with open(r"./articles_app/data/sectorcompany.json") as f:
            sector_info = json.load(f)

        # filter all the selected sectors
        options = sectors.get("options")
        queries = [x for x in queries if sector_info.get(x.serie) in options]

    data = []
    # format the data into a json format
    for observation in queries:

        # get all the series the observation is based on
        if type(observation.meta_data.get("component")) == list:
            serie = ", ".join(observation.meta_data.get("component"))
        else:
            serie = observation.serie

        point = {
            "serie": serie,
            "period": "{0} / {1}".format(observation.period_end.strftime("%d-%m-%Y"), observation.period_begin.strftime("%d-%m-%Y")),
            "pattern": observation.pattern,
            "observation": observation.observation
        }
        data.append(point)
    return data


def get_compose_options(filters):
    """[summary]

    Args:
        filters ([type]): [description]

    Returns:
        [type]: [description]
    """
    # get all the observations
    queries = Observations.objects.all()

    # check if filters on periode are selected
    periods = filters.get("Periode")
    if periods.get("options") != []:
        # get the max and min range of the period
        period_range = util.get_period_range(periods.get("options"))
        # apply the filter
        queries = queries.filter(period_end__range=period_range)
    else:
        # get only the last two weeks
        period_range = util.get_period_range(["deze week", "vorige week"])
        # apply the filter
        queries = queries = queries.filter(period_end__range=period_range)

    # load in the sector data
    with open(r"./articles_app/data/sectorcompany.json") as f:
        sector_info = json.load(f)

    data = []
    # format the data into a json format
    for observation in queries.order_by("-period_end", "-relevance"):
        point = {
            "id": observation.id,
            "period": "{0} / {1}".format(observation.period_end.strftime("%d-%m-%Y"), observation.period_begin.strftime("%d-%m-%Y")),
            "sector": sector_info.get(observation.serie),
            "pattern": observation.pattern,
            "observation": observation.observation,
            "relevance": float(observation.relevance)
        }
        data.append(point)
    return data


def get_relevance_observations():
    """[summary]

        Returns:
        [type]: [description]
    """
    # get all the latest observations info
    relev_observations = Observations.objects.order_by('-period_end', '-relevance')[:200]

    data = []

    # format the data into a json format
    for observation in relev_observations:

        # get all the series the observation is based on
        if type(observation.meta_data.get("component")) == list:
            serie = ", ".join(observation.meta_data.get("component"))
        else:
            serie = observation.serie

        point = {
            "serie": serie,
            "period": "{0} / {1}".format(observation.period_end.strftime("%d-%m-%Y"), observation.period_begin.strftime("%d-%m-%Y")),
            "pattern": observation.pattern,
            "observation": observation.observation,
            "relevance": float(observation.relevance)
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

    data = []
    for article in articles_set:
        art = {}
        art["article_id"] = article.id
        art["title"] = article.title
        art["img_source"] = article.top_image
        art["content"] = f"{article.content[:120]}...."
        art["date_show"] = article.date.strftime("%d %b %Y")
        art["author"] = article.author
        data.append(art)

    return data


def get_article(article_id):
    """[summary]

    Args:
        article_id ([type]): [description]

    Returns:
        [type]: [description]
    """
    article = {}

    # check if article exists
    if Articles.objects.filter(id=article_id).exists():
        # article exists
        selected_article = Articles.objects.get(id=article_id)

        article["found"] = True
        article["article_id"] = selected_article.id
        article["img_source"] = selected_article.top_image
        article["title"] = selected_article.title
        article["content"] = selected_article.content
        article["date_show"] = selected_article.date.strftime("%d %b %Y")
        article["date_whole"] = selected_article.date.strftime("%m-%d-%Y, %H:%M:%S")
        article["author"] = selected_article.author
        article["AI_version"] = selected_article.AI_version
        article["query_set"] = selected_article
        article["meta_data"] = selected_article.meta_data
        print(article.get("meta_data").get("relevance"))

        # since 13-11-20 a new meta_data is implemented, therefore we have to check if the old format is in the article or not.
        if ("relevance" in article.get("meta_data")) and (type(article.get("meta_data").get("relevance")[0]) == dict):
            article['old_format'] = False
        else:
            article['old_format'] = True

    else:
        # article doesn't exist so set found to false so a 404 error can be thrown
        article["found"] = False

    return article
