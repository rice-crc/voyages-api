from django.urls import path

from . import views

urlpatterns = [
    path('', views.VoyageList.as_view()),
    path('dataframes',views.VoyageDataFrames.as_view()),
    path('animationcache',views.VoyageAnimationCache.as_view()),
    path('geo',views.VoyagePlaceList.as_view()),
    path('aggregations',views.VoyageAggregations.as_view()),
	path('autocomplete',views.VoyageTextFieldAutoComplete.as_view())
    ]