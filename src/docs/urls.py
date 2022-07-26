from django.urls import path

from . import views

urlpatterns = [
    path('', views.DocList.as_view()),
    ]
    
    