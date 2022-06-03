from django.urls import path

from . import views

urlpatterns = [
    path('', views.VoyageList.as_view()),
    path('dataframes',views.VoyageDataFrames.as_view()),
    path('caches',views.VoyageCaches.as_view()),
    path('aggregations',views.VoyageAggregations.as_view()),
	path('autocomplete',views.VoyageTextFieldAutoComplete.as_view()),
	path('groupby',views.VoyageGroupBy.as_view()),
	path('crosstabs',views.VoyageCrossTabs.as_view()),
	path('<int:voyage_id>/',views.SingleVoyage.as_view()),
	path('<int:voyage_id>/<varname>/',views.SingleVoyageVar.as_view())
    ]
    
    