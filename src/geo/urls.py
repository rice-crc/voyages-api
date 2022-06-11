from django.urls import path

from . import views

urlpatterns = [
    path('', views.LocationList.as_view()),
    path('GeoJsonNetwork',views.getGeoJsonNetwork.as_view())
    ]