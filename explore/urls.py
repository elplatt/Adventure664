from django.urls import path
from . import views

app_name = 'explore'
urlpatterns = [
        path('', views.index, name='index'),
        path('lobby/', views.lobby, name='lobby'),
        path('create/', views.create_area, name='create_area'),
        path('create/<area_title>', views.create_area, name='create_area'),
        path('<int:area_id>/', views.area, name='area'),
        path('<int:area_id>/edit', views.edit_area, name='edit_area'),
        path('<int:source_id>/connection/<title>', views.new_connection, name='new_connection'),
        path('<int:source_id>/connection/<title>/delete', views.delete_connection, name='delete_connection'),
        path('<int:area_id>/activity/<int:activity_id>/delete', views.delete_activity, name='delete_activity'),
        # Legacy paths, should not be used in new code
        path('<int:area_id>/description', views.edit_area, name='area_description'),
]
