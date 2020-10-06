from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .db_queries import *
from .nlg_queries import *
from .utils import *

from datetime import datetime
import json


# Create your views here.
def home(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    return render(request, "articles_app/home.html")

 
@login_required
def load_module_view(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    return render(request, "articles_app/modules.html")


@login_required
def load_all_data_series(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = get_all_data_series()

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def load_data_serie_close(request, serie_name):
    """[summary]

    Args:
        request ([type]): [description]
        serie_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = get_data_serie_close(serie_name)

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_latest_observations(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = get_latest_observations()

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_relevance_observations(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = get_relevance_observations()

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def generate_article(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    if is_view_only(request.user):
        # user has no permission to generate articles
        messages.info(request, f"You don't have permission to generate an article")
        data = {"article_number" : get_articles_set(1)[1]['article_id']}
    else:
        user_name = request.user.username
        data = {"article_number" : build_article(user_name)}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_articles_set(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = get_articles_set(6)

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def load_article(request, article_id):
    """[summary]

    Args:
        request ([type]): [description]
        article_id ([type]): [description]

    Returns:
        [type]: [description]
    """
    article = get_article(article_id)

    context = {
        'article' : article
    }
    return render(request, "articles_app/article.html", context)