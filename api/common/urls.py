from django.urls import path

from . import views

urlpatterns = [
	path('global/', views.GlobalSearch.as_view()),
	path('past_graph/', views.PastGraphMaker.as_view()),
	path('schemas/', views.Schemas.as_view()),
# 	path('sparsedate/RD/<int:id>',views.SparseDateRD.as_view())
]