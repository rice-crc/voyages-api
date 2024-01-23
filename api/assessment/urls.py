from django.urls import path

from . import views

urlpatterns = [
    path('dataframes/',views.EstimateDataFrames.as_view()),
    path('crosstabs/',views.EstimateCrossTabs.as_view())
    ]