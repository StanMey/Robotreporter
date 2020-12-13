from django.urls import path

from . import views

urlpatterns = [
    path('articles/<int:article_id>', views.load_article, name="load_article"),

    path('api/dataseries', views.load_all_data_series, name="load_all_data_series"),
    path('api/dataseries/<str:serie_name>/close', views.load_data_serie_close, name="load_data_serie_close"),

    path('api/articles/generate', views.generate_article, name="generate_article"),
    path('api/articles/composeoptions', views.load_compose_options, name="load_compose_options"),
    path('api/articles/composearticle', views.compose_article, name="compose_article"),

    path('api/observations/latest', views.load_latest_observations, name="load_latest_observations"),
    path('api/observations/getfilters', views.get_observations_filters, name="get_observations_filters"),
    path('api/observations/usefilters', views.load_observations_with_filters, name="load_observations_with_filters"),
    path('api/observations/relevance', views.load_relevance_observations, name="load_relevance_observations"),

    path('api/testscores', views.load_test_scores_info, name="load_test_scores_info"),

    path('api/relevance/getfilters', views.get_relevance_filters, name="get_relevance_filters")
]
