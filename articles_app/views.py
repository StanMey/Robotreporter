from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from .forms import CommentForm

import articles_app.db_queries as dbq
import articles_app.nlg_queries as nlgq
import articles_app.utils as util

import json


# Create your views here.
def home(request):
    """Returns a static home page which every user sees when entering the page.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/home.html")


@login_required
def load_moduleA_view(request):
    """Loads the view of module A.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/moduleA.html")


@login_required
def load_moduleB_view(request):
    """Loads the view of module B.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/moduleB.html")


@login_required
def load_moduleC_view(request):
    """Loads the view of module C.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/moduleC.html")


@login_required
def load_moduleD_view(request):
    """Loads the view of module D with the help of a paginator.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    data = dbq.get_articles_set(60)
    paginator = Paginator(data, 6)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "articles_app/moduleD.html", {'page_obj': page_obj})


def load_latest_articles(request):
    """Loads the latest 3 articles to show to a not-logged in user.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    articles = dbq.get_articles_set(3)
    return render(request, "articles_app/latest_articles.html", {'articles': articles})


def load_latest_single_article(request, article_id):
    """Checks if the selected article is of the latest 3 articles, if so returns the information about the article.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user
        article_id (int): [description]

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    articles = dbq.get_articles_set(3)
    # check if article belongs to the last three articles made
    # TODO perhaps only give back articles made by the 'nieuwsbot'
    if article_id in [x.get('article_id') for x in articles]:
        # article belongs to the last three articles made
        article = dbq.get_article(article_id)
        if article.get("found"):
            # article has been found
            return render(request, "articles_app/latest_article.html", {'article': article})
        else:
            # article does not exist
            messages.info(request, "artikel niet gevonden")
    else:
        # article doesn't belong to the last three articles made
        messages.info(request, "Geen toegang tot artikel")

    return render(request, "articles_app/latest_articles.html", {'articles': articles})


@login_required
def about_page(request):
    """Loads the about page when a user is logged in.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/about.html")


@login_required
def load_background_view(request):
    """Loads the extended background page when a user is logged in.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/explainer_pages/background.html")


@login_required
def load_sysabout_view(request):
    """Loads the about system page when a user is logged in.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/explainer_pages/about_system.html")


@login_required
def load_inspirations_view(request):
    """Loads the inspirations page when a user is logged in.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/explainer_pages/inspirations.html")


@login_required
def load_relevance_view(request):
    """Returns a static page with the explanation of the relevance.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/explainer_pages/relevance.html")


@login_required
def load_test_scores_view(request):
    """Loads the view with the test scores and the explanation.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/explainer_pages/sit_rel_explained.html")


def robots_txt(request):
    """Loads the robot.txt file.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    lines = [
        "User-Agent: *",
        "Disallow: /admin/"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def privacy_statement(request):
    """Loads the privacy statement file.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/privacy.html")


def cookie_statement(request):
    """Loads the cookie statement file.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    return render(request, "articles_app/cookies.html")


# retrieving data views
@login_required
def load_all_data_series(request):
    """Retrieves the max date, min date, sector and latest value of every unique component
    and returns the json data to the site.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: [description]
    """
    data = dbq.get_all_data_series()

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def load_data_serie_close(request, serie_name):
    """Gets all the stock close points for a particular component.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user
        serie_name (str): The name of the component

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
    """
    data = dbq.get_data_serie_close(serie_name)

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def get_observations_filters(request):
    """Get all the available filters to filter the observations on.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
    """
    data = dbq.get_available_observ_filters()
    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def get_relevance_filters(request):
    """Get all the available compose options for generating an article.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
    """
    data = dbq.get_available_compose_filters()
    return HttpResponse(json.dumps(data), content_type="application/json")


# TODO: finding out why csrf gives error messages despite using csrf in the POST request
@login_required
@csrf_exempt
def load_observations_with_filters(request):
    """Apply the filters and return the filtered observations.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
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
    """Get all the available observations to let the user compose its own article.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
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
    """Takes in the chosen observations and constructs the article for the user.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
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
    """Loads in all the observations.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
    """
    data = dbq.get_latest_observations()

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def load_test_scores_info(request):
    """Loads in all the test cases with the scores per test case.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
    """
    data = nlgq.get_test_case_info()
    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
@csrf_exempt
def generate_article(request):
    """Generates an article.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user

    Returns:
        django.http.response.HttpResponse: Returns the json data to the webpage
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
def load_article(request, article_id):
    """Loads one single article.
    https://djangocentral.com/creating-comments-system-with-django/

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): The request made by the user
        article_id (int): The id of the article

    Returns:
        django.http.response.HttpResponse: Combines a given template with a given context dictionary
                                           and returns an HttpResponse object with that rendered text.
    """
    article = dbq.get_article(article_id)
    context = {}

    if not article.get("found"):
        # article not found
        raise Http404("Article does not exist")
    else:
        # article found

        comments = article.get("query_set").comments.filter(active=True)[:3]

        if request.method == "POST":
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                # create Comment object but not yet save it
                new_comment = comment_form.save(commit=False)
                # assign the article to the comment
                new_comment.article = article.get("query_set")
                # assign the user as the author to the comment
                new_comment.author = request.user.username
                # save the comment to the database
                new_comment.save()
                messages.info(request, "Feedback ontvangen")
        else:
            comment_form = CommentForm()

        if article.get("AI_version") >= 1.4:
            # a new format as to the showcase of meta data is being used
            chosen_observs = article.get("meta_data").get("observs")
            sit_relev = article.get("meta_data").get("sit_relev")
            meta_observs = []

            for x in range(len(chosen_observs)):
                # get the id of the observation
                oid = chosen_observs[x]
                # retrieve the observation
                ob = dbq.get_single_observation(oid)
                # check if observation has been found
                if ob.get("found"):
                    # article has been found
                    # retrieve the situational relevation and format the periods
                    ob["rel_sit"] = sit_relev[x]
                    ob["period_show"] = "{0} / {1}".format(ob.get("prd_begin").strftime("%d-%m-%Y"), ob.get("prd_end").strftime("%d-%m-%Y"))

                    meta_observs.append(ob)

            # add meta_observs to the context
            context["meta_observs"] = meta_observs

        # build the context
        context["article"] = article
        context["comments"] = comments
        context["comment_form"] = comment_form

        # TODO set a slider or stars in the crispy form
        return render(request, "articles_app/article.html", context)
