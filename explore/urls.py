from django.urls import path
from . import views

app_name = 'explore'
urlpatterns = [
        path('', views.index, name='index'),
        path('<int:area_id>/', views.area, name='area'),
        path('<int:area_id>/description/', views.area_description, name='area_description'),
        path('<int:source_id>/connection/<title>', views.new_connection, name='new_connection'),
        path('<int:source_id>/connection/<title>/delete', views.delete_connection, name='delete_connection'),
]
