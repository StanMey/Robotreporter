from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('overview/', views.load_module_view, name="load_module_view"),
    path('articles/<int:article_id>', views.load_article, name="load_article"),

    path('overview/api/dataseries', views.load_all_data_series, name="load_all_data_series"),
    path('overview/api/dataseries/<str:serie_name>/close', views.load_data_serie_close, name="load_data_serie_close"),

    path('overview/api/articles', views.load_articles_set, name="load_articles_set"),
    path('overview/api/articles/generate', views.generate_article, name="generate_article"),

    path('overview/api/observations/latest', views.load_latest_observations, name="load_latest_observations"),
    path('overview/api/observations/getfilters', views.get_observations_filters, name="get_observations_filters"),
    path('overview/api/observations/usefilters', views.load_observations_with_filters, name="load_observations_with_filters"),
    path('overview/api/observations/relevance', views.load_relevance_observations, name="load_relevance_observations")
]