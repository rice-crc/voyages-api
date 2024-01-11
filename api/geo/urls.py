from django.urls import path

from . import views

urlpatterns = [
    path('',views.LocationCREATE.as_view()),
    path('<int:value>',views.LocationRETRIEVE.as_view()),
    path('<int:value>',views.LocationUPDATE.as_view()),
    path('<int:value>',views.LocationDESTROY.as_view())
]
    
    