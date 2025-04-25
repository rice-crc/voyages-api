from django.urls import path
from .views import batch_data_api

urlpatterns = [
    path('data', batch_data_api, name='contrib_data_api'),
]