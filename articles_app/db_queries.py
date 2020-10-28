from datetime import datetime, date, timedelta
from django.db.models import Min
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
    months = retrieve_filterable_months(True)
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
    months = retrieve_filterable_months(True)
    data["Periode"] = ["vorige dag", "deze week", "vorige week", *months]
    return data


def retrieve_filterable_months(in_text):
    """Gets the names of the current month and the last 2 months before that if in_text is True,
    otherwise returns a tuple_pair (month, year) with the same info

    Args:
        in_text (bool): [description]

    Returns:
        list: returns the textual form of the months if 'in_text' is True, otherwise returns a tuple pair with the month and year
    """
    # get the current month and year in a tuple (month, year)
    current = (datetime.now().month, datetime.now().year)

    # get 2 previous months
    if current[0] == 2:
        last_month = (1, current[1])
        last_last_month = (12, current[1] - 1)
    elif current[0] == 1:
        last_month = (12, current[1] - 1)
        last_last_month = (11, current[1] - 1)
    else:
        last_month = (current[0] - 1, current[1])
        last_last_month = (current[0] - 2, current[1])

    filter_months = [current, last_month, last_last_month]

    if in_text:
        numb_to_month = {
            1: "januari",
            2: "februari",
            3: "maart",
            4: "april",
            5: "mei",
            6: "juni",
            7: "juli",
            8: "augustus",
            9: "september",
            10: "oktober",
            11: "november",
            12: "december"
        }
        return [numb_to_month.get(x) for (x, _) in filter_months]
    else:
        return filter_months


def get_period_range(period_filters):
    """[summary]

    Args:
        filters (list): [description]

    Returns:
        [type]: [description]
    """
    all_dates = []
    # get the months on which can be filtered
    text_months = retrieve_filterable_months(True)
    date_months = retrieve_filterable_months(False)
    # get the current week
    week = datetime.now().isocalendar()[:2]

    # check for each month if it has to be filtered on
    if text_months[0] in period_filters:
        # this month has to be filtered upon
        y = date_months[0][1]
        m = date_months[0][0]
        ndays = (date(y, m+1, 1) - date(y, m, 1)).days
        d1 = datetime(y, m, 1)
        d2 = datetime(y, m, ndays)
        all_dates.append((d1, d2))

    if text_months[1] in period_filters:
        # this month has to be filtered upon
        y = date_months[1][1]
        m = date_months[1][0]
        ndays = (date(y, m+1, 1) - date(y, m, 1)).days
        d1 = datetime(y, m, 1)
        d2 = datetime(y, m, ndays)
        all_dates.append((d1, d2))

    if text_months[2] in period_filters:
        # this month has to be filtered upon
        y = date_months[2][1]
        m = date_months[2][0]
        ndays = (date(y, m+1, 1) - date(y, m, 1)).days
        d1 = datetime(y, m, 1)
        d2 = datetime(y, m, ndays)
        all_dates.append((d1, d2))

    if "deze week" in period_filters:
        # filter on this week
        mon_date = datetime.strptime(f"{week[0]}-W{week[1]}" + '-1', '%G-W%V-%u')
        fri_date = mon_date + timedelta(4)
        all_dates.append((mon_date, fri_date))

    if "vorige week" in period_filters:
        # TODO correct for new year
        # filter on last week
        mon_date = datetime.strptime(f"{week[0]}-W{week[1] - 1}" + '-1', '%G-W%V-%u')
        fri_date = mon_date + timedelta(4)
        all_dates.append((mon_date, fri_date))

    if "vorige dag" in period_filters:
        # filter based on last day
        current_date = datetime.now().replace(hour=00, minute=00, second=00, microsecond=0)
        if current_date.weekday() == 5:
            last = current_date - timedelta(1)
        elif current_date.weekday() == 6:
            last = current_date - timedelta(2)
        else:
            last = current_date - timedelta(1)
        all_dates.append((last, current_date))

    # get the max and min date over all dates
    max_date = max([x for (_, x) in all_dates])
    min_date = min([x for (x, _) in all_dates])
    return (min_date, max_date)


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
        period_range = get_period_range(periods.get("options"))
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
    article = {}

    if Articles.objects.filter(id=article_id).exists():
        selected_article = Articles.objects.get(id=article_id)

        article["found"] = True
        article["article_id"] = selected_article.id
        article["title"] = selected_article.title
        article["content"] = selected_article.content
        article["date_show"] = selected_article.date.strftime("%d %b %Y")
        article["date_whole"] = selected_article.date.strftime("%m-%d-%Y, %H:%M:%S")
        article["author"] = selected_article.author
        article["AI_version"] = selected_article.AI_version
        article["meta_data"] = selected_article.meta_data
    else:
        article["found"] = False

    return article
