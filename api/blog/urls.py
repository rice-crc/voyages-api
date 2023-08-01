from django.urls import path

from . import views

urlpatterns = [
    path('', views.PostList.as_view()),
    path('autocomplete', views.PostTextFieldAutoComplete.as_view())
]
    
    