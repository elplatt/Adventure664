"""adventure URL Configuration

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
import os

from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.static import serve

import home.views

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.join(BASE_DIR, 'site')

urlpatterns = [
    path('', RedirectView.as_view(url='explore/', permanent=False), name='index'),
    path('admin/', admin.site.urls),
    path('explore/', include('explore.urls')), 
    path('api/explore/', include('explore.api_urls')),
    path('items/', include('item.urls')),
    path('player/', include('player.urls')),
    path('accounts/register', home.views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('tutorial/', include('tutorial.urls')),
    path('guide/', TemplateView.as_view(template_name='home/guide.html'), name='guide'),
]
