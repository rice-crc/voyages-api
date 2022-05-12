from django.urls import path

from . import views

urlpatterns = [
    path('', views.EnslavedList.as_view(), name='tabular'),
	path('<int:enslaved_id>/',views.SingleEnslaved.as_view()),
	path('<int:enslaved_id>/<varname>/',views.SingleEnslavedVar.as_view())
    ]