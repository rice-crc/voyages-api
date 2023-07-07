from django.urls import path

from . import views

urlpatterns = [
    path('', views.GlobalSearch.as_view())
    ]
    
    