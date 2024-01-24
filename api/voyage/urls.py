from django.urls import path

from . import views

urlpatterns = [
    path('', views.VoyageList.as_view()),
    path('dataframes/',views.VoyageDataFrames.as_view()),
    path('aggregations/',views.VoyageAggregations.as_view()),
	path('autocomplete/',views.VoyageCharFieldAutoComplete.as_view()),
	path('groupby/',views.VoyageGroupBy.as_view()),
	path('crosstabs/',views.VoyageCrossTabs.as_view()),
	path('aggroutes/',views.VoyageAggRoutes.as_view()),
	path('geotree/',views.VoyageGeoTreeFilter.as_view()),
	path('CREATE/<int:voyage_id>',views.VoyageCreate.as_view()),
	path('RUD/<int:voyage_id>',views.VoyageRetrieveUpdateDestroy.as_view()),
	path('NationalityList/',views.NationalityList.as_view()),
	path('RigOfVesselList/',views.RigOfVesselList.as_view()),
	path('TonTypeList/',views.TonTypeList.as_view()),
	path('ParticularOutcomeList/',views.ParticularOutcomeList.as_view()),
	path('SlavesOutcomeList/',views.SlavesOutcomeList.as_view()),
	path('ResistanceList/',views.ResistanceList.as_view()),
	path('OwnerOutcomeList/',views.OwnerOutcomeList.as_view()),
	path('VesselCapturedOutcomeList/',views.VesselCapturedOutcomeList.as_view())
]
