from django.urls import path

from . import views

urlpatterns = [
    path('', views.GeoTree.as_view()),
    path('CREATE/',views.LocationCREATE.as_view()),
    path('RETRIEVE/<int:value>',views.LocationRETRIEVE.as_view()),
    path('UPDATE/<int:value>',views.LocationUPDATE.as_view()),
    path('DESTROY/<int:value>',views.LocationDESTROY.as_view())
]
    
    