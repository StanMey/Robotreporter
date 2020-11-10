"""nieuwsbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from users import views as user_views
from articles_app import views as app_views


urlpatterns = [
    path('', app_views.home, name='home'),
    path('modules/', include('articles_app.urls')),
    path('data/', include('articles_app.urls_data')),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('robots.txt/', app_views.robots_txt, name='robots_txt'),
    path('privacy/', app_views.privacy_statement, name="privacy_statement"),
    path('cookies/', app_views.cookie_statement, name="cookie_statement"),
    path('about/', app_views.about_page, name="about_page"),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
