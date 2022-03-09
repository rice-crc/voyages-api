from django.urls import path

from . import views

urlpatterns = [
    path('', views.EnslavedList.as_view(), name='tabular'),
    ]