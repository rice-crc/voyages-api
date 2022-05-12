from django.urls import path

from . import views

urlpatterns = [
    path('', views.VoyageList.as_view()),
    path('dataframes',views.VoyageDataFrames.as_view()),
    path('caches',views.VoyageCaches.as_view()),
    path('geo',views.VoyagePlaceList.as_view()),
    path('aggregations',views.VoyageAggregations.as_view()),
	path('autocomplete',views.VoyageTextFieldAutoComplete.as_view()),
	path('groupby',views.VoyageGroupBy.as_view()),
	#path('<int:voyage_id>/',views.VoyageListHuman.as_view()),
	path('<int:voyage_id>/<varname>/',views.VoyageVarListHuman.as_view())
    ]
    
    