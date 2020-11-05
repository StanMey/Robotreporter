from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

import articles_app.db_queries as dbq
import articles_app.nlg_queries as nlgq
import articles_app.utils as util

import json


# Create your views here.
def home(request):
    """Returns a static home page which every user sees when entering the page.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    return render(request, "articles_app/home.html")


@login_required
def load_module_view(request):
    """Loads the main menu from which the user can select all the modules.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    return render(request, "articles_app/modules.html")


@login_required
def load_relevance_view(request):
    """Returns a static page with the explanation of the relevance.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    return render(request, "articles_app/relevance.html")


def robots_txt(request):
    """Loads the robot.txt file.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    lines = [
        "User-Agent: *",
        "Disallow: /admin/"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def privacy_statement(request):
    """Loads the privacy statement file.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    return render(request, "articles_app/privacy.html")


def cookie_statement(request):
    """Loads the cookie statement file.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    return render(request, "articles_app/cookies.html")


# retrieving data views
@login_required
def load_all_data_series(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_all_data_series()

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def load_data_serie_close(request, serie_name):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]
        serie_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    data = dbq.get_data_serie_close(serie_name)

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def get_observations_filters(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_available_observ_filters()
    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def get_relevance_filters(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_available_relev_filters()
    return HttpResponse(json.dumps(data), content_type="application/json")


# TODO: finding out why csrf gives error messages despite using csrf in the POST request
@login_required
@csrf_exempt
def load_observations_with_filters(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    if request.method == 'POST':
        chosen_filters = json.loads(request.body)
        data = dbq.get_filtered_observations(chosen_filters)
    else:
        data = {}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
@csrf_exempt
def load_compose_options(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    if request.method == 'POST':
        chosen_filters = json.loads(request.body)
        data = dbq.get_compose_options(chosen_filters)
    else:
        data = {}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
@csrf_exempt
def compose_article(request):
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """
    if util.is_view_only(request.user):
        # user has no permission to generate articles
        messages.info(request, "You don't have permission to generate an article")
        data = {"article_number": dbq.get_articles_set(1)[1]['article_id']}
    else:
        if request.method == 'POST':
            user_name = request.user.username
            body = json.loads(request.body)
            chosen_filters = body.get("filters")
            content = body.get("content")
            title = body.get("title")
            data = {"article_number": nlgq.construct_article(user_name, content, chosen_filters, title)}
        else:
            messages.error(request, "Can't do that right now")
            data = {"article_number": dbq.get_articles_set(1)[1]['article_id']}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_latest_observations(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_latest_observations()

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_relevance_observations(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_relevance_observations()

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
@csrf_exempt
def generate_article(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    if util.is_view_only(request.user):
        # user has no permission to generate articles
        messages.info(request, "You don't have permission to generate an article")
        data = {"article_number": dbq.get_articles_set(1)[1]['article_id']}
    else:
        # user has permission to generate articles
        if request.method == 'POST':
            # user uses the right request method
            chosen_filters = json.loads(request.body)
            user_name = request.user.username
            data = {"article_number": nlgq.build_article(user_name, chosen_filters)}
        else:
            messages.error(request, "Can't do that right now")
            data = {"article_number": dbq.get_articles_set(1)[1]['article_id']}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_articles_set(request):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_articles_set(6)

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def load_article(request, article_id):
    """[summary]

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): [description]
        article_id ([type]): [description]

    Returns:
        [type]: [description]
    """
    article = dbq.get_article(article_id)

    context = {
        'article': article
    }
    if article.get("found"):
        return render(request, "articles_app/article.html", context)
    else:
        raise Http404("Article does not exist")
