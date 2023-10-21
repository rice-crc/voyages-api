from django.urls import path

from . import views

urlpatterns = [
    path('', views.GeoTree.as_view()),
    path('CRUD/<int:value>',views.LocationCRUD.as_view()),
]
    
    