from django.urls import path

from . import views

urlpatterns = [
    path('enslaved/', views.EnslavedList.as_view()),
#     path('enslaved/autocomplete', views.EnslavedTextFieldAutoComplete.as_view()),    
    path('enslaved/aggregations',views.EnslavedAggregations.as_view()),
    path('enslaver/',views.EnslaverList.as_view()),
#     path('enslavers/autocomplete', views.EnslaverTextFieldAutoComplete.as_view()),    
    path('enslavers/aggregations',views.EnslaverAggregations.as_view()),
# 	path('<int:enslaved_id>/',views.SingleEnslaved.as_view()),
# 	path('<int:enslaved_id>/<varname>/',views.SingleEnslavedVar.as_view())
# 	
    ]
# 
