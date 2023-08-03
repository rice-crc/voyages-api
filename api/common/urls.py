from django.urls import path

from . import views

urlpatterns = [
	path('global/', views.GlobalSearch.as_view()),
	path('past_graph/', views.PastGraphMaker.as_view())
]