from django.urls import path

from . import views

urlpatterns = [
	path('enslaved/', views.EnslavedList.as_view()),
	path('enslaved/<int:enslaved_id>',views.EnslavedGET.as_view()),
	path('enslaved/autocomplete/', views.EnslavedCharFieldAutoComplete.as_view()),
	path('enslaved/aggregations/',views.EnslavedAggregations.as_view()),
	path('enslaved/dataframes/',views.EnslavedDataFrames.as_view()),
	path('enslaved/aggroutes/',views.EnslavedAggRoutes.as_view()),
	path('enslavementrelation/dataframes/',views.EnslavementRelationDataFrames.as_view()),
	path('enslaver/',views.EnslaverList.as_view()),
	path('enslaver/<int:id>',views.EnslaverGET.as_view()),
	path('enslaver/autocomplete/', views.EnslaverCharFieldAutoComplete.as_view()),
	path('enslaver/aggregations/',views.EnslaverAggregations.as_view()),
	path('enslaver/dataframes/',views.EnslaverDataFrames.as_view()),
	path('networks/',views.PASTNetworks.as_view()),
	path('enslaved/geotree/',views.EnslavedGeoTreeFilter.as_view()),
	path('enslaver/geotree/',views.EnslaverGeoTreeFilter.as_view()),
	path('enslaved/languagegrouptree/',views.EnslavedLanguageGroupTree.as_view()),
	path('enlaver/EnslaverRoleList/',views.EnslaverRoleList.as_view()),	
	
	
# 	path('enslavementrelation/CREATE/',views.EnslavementRelationCREATE.as_view()),
# 	path('enslavementrelation/<int:id>',views.EnslavementRelationRETRIEVE.as_view()),
# 	path('enslavementrelation/UPDATE/<int:id>',views.EnslavementRelationUPDATE.as_view()),
# 	path('enslavementrelation/DESTROY/<int:id>',views.EnslavementRelationDESTROY.as_view()),
# 	path('enslaver/CREATE/',views.EnslaverCREATE.as_view()),
	
# 	path('enslaver/UPDATE/<int:id>',views.EnslaverUPDATE.as_view()),
# 	path('enslaver/DESTROY/<int:id>',views.EnslaverDESTROY.as_view()),
# 	path('enslaved/CREATE/',views.EnslavedCREATE.as_view()),
	
# 	path('enslaved/UPDATE/<int:enslaved_id>',views.EnslavedUPDATE.as_view()),
# 	path('enslaved/DESTROY/<int:enslaved_id>',views.EnslavedDESTROY.as_view())
]
