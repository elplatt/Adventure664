from django.urls import path
from . import views

app_name = 'item'
urlpatterns = [
        path('create/<int:area_id>', views.create, name='create'),
        path('<int:item_id>/delete', views.delete, name='delete'),
]
