from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from .models import Stocks, Articles

from datetime import datetime
import json


# Create your views here.
def home(request):
    return render(request, "articles_app/home.html")


@login_required
def get_module_view(request):
    return render(request, "articles_app/modules.html")


@login_required
def get_all_data_series(request):
    """[summary]

    Args:
        request ([type]): [description]

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

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def get_data_serie_close(request, serie_name):
    """[summary]

    Args:
        request ([type]): [description]
        serie_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    # get all the close data from a certain serie
    close_data = Stocks.objects.filter(component__exact=serie_name)

    data = []
    count = 0

    # format the data into a json format
    for data_point in close_data:
        point = {
            "date": data_point.date.strftime("%d-%m-%Y"),
            "value": float(data_point.s_close)
        }
        data.append(point)

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def get_articles_set(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    articles_set = Articles.objects.order_by('-date')[:6]

    data = {}
    count = 1
    for article in articles_set:
        art = {}
        art["article_id"] = article.id
        art["title"] = article.title
        art["content"] = article.content
        art["date_show"] = article.date.strftime("%d %b %Y")
        art["date_whole"] = article.date.strftime("%m-%d-%Y, %H:%M:%S")
        art["author"] = article.author
        art["AI_version"] = article.AI_version
        data[count] = art
        count += 1

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def get_article(request, article_id):
    """[summary]

    Args:
        request ([type]): [description]
        article_id ([type]): [description]

    Returns:
        [type]: [description]
    """

    selected_article = Articles.objects.get(id=article_id)

    art = {}
    art["article_id"] = selected_article.id
    art["title"] = selected_article.title
    art["content"] = selected_article.content
    art["date_show"] = selected_article.date.strftime("%d %b %Y")
    art["date_whole"] = selected_article.date.strftime("%m-%d-%Y, %H:%M:%S")
    art["author"] = selected_article.author
    art["AI_version"] = selected_article.AI_version

    context = {
        'article' : art
    }
    return render(request, "articles_app/article.html", context)