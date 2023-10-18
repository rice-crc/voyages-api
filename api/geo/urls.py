from django.urls import path

from . import views

urlpatterns = [
    path('', views.GeoTree.as_view()),
    path('RUD/<int:value>',views.LocationRUD.as_view())
    ]
    
    