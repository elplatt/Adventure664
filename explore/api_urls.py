from django.urls import path
from . import views

app_name = 'explore_api'
urlpatterns = [
    path('<int:area_id>/activity', views.json_activity, name='activity')
]
