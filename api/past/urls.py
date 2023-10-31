from django.urls import path

from . import views

urlpatterns = [
    path('enslaved/', views.EnslavedList.as_view()),
    path('enslaved/autocomplete', views.EnslavedCharFieldAutoComplete.as_view()),
    path('enslaved/aggregations',views.EnslavedAggregations.as_view()),
    path('enslaved/dataframes',views.EnslavedDataFrames.as_view()),
    path('enslaver/dataframes',views.EnslaverDataFrames.as_view()),
    path('enslaver/',views.EnslaverList.as_view()),
    path('enslaver/autocomplete', views.EnslaverCharFieldAutoComplete.as_view()),
    path('enslaver/aggregations',views.EnslaverAggregations.as_view()),
    path('enslaved/aggroutes',views.EnslavedAggRoutes.as_view()),
    path('networks',views.PASTNetworks.as_view()),
    path('enslaved/geotree',views.EnslavedGeoTreeFilter.as_view()),
    path('enslaver/geotree',views.EnslaverGeoTreeFilter.as_view()),
	path('enslaver/CREATE/',views.EnslaverCREATE.as_view()),
	path('enslaver/RUD/<int:id>',views.EnslaverRUD.as_view()),
	path('enslaved/CREATE/',views.EnslavedCREATE.as_view()),
	path('enslaved/RUD/<int:enslaved_id>',views.EnslavedRUD.as_view())
    ]
