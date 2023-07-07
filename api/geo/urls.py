from django.urls import path

from . import views

urlpatterns = [
    path('', views.GeoTree.as_view())
    ]
    
    