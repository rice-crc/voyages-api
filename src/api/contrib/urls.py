from django.urls import path
from .views import batch_data_api, location_tree

urlpatterns = [
    path('data', batch_data_api, name='contrib_data_api'),
    path('location_tree', location_tree, name='location_tree'),
]