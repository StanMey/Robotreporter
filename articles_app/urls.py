from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('moduleA/', views.load_moduleA_view, name="load_moduleA_view"),
    path('moduleB/', views.load_moduleB_view, name="load_moduleB_view"),
    path('moduleC/', views.load_moduleC_view, name="load_moduleC_view"),
    path('moduleD/', views.load_moduleD_view, name="load_moduleD_view"),

    path('articles/<int:article_id>', views.load_article, name="load_article"),
    path('latest/', views.load_latest_articles, name="load_latest_articles"),
    path('latest/<int:article_id>', views.load_latest_single_article, name="load_latest_single_article"),
    path('relevance/', views.load_relevance_view, name="load_relevance_view"),
    path('testscores/', views.load_test_scores_view, name="load_test_scores_view")
]
