from django.urls import path

from . import views

urlpatterns = [
    path('global/', views.GlobalSearch.as_view())
    ]
    
    