from django.urls import path

from . import views

urlpatterns = [
    path('enslaved/', views.EnslavedList.as_view()),
    path('enslaved/autocomplete', views.EnslavedTextFieldAutoComplete.as_view()),
    path('enslaved/aggregations',views.EnslavedAggregations.as_view()),
    path('enslaved/dataframes',views.EnslavedDataFrames.as_view()),
    path('enslaver/dataframes',views.EnslaverDataFrames.as_view()),
    path('enslaver/',views.EnslaverList.as_view()),
    path('enslaver/autocomplete', views.EnslaverTextFieldAutoComplete.as_view()),
    path('enslaver/aggregations',views.EnslaverAggregations.as_view()),
    path('enslaved/aggroutes',views.EnslavedAggRoutes.as_view()),
    path('networks',views.PASTNetworks.as_view())
    ]
