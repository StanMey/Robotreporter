from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.get_module_view, name="get_module_view"),
    path('articles/api/dataseries', views.get_all_data_series, name="get_data_series"),
    path('articles/api/dataseries/<str:serie_name>/close', views.get_data_serie_close, name="get_data_serie_close"),
    path('articles/api/articles', views.get_articles_set, name="get_articles_set"),
    path('articles/api/articles/<int:article_id>', views.get_article, name="get_article")
]