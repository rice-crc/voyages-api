from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
import time
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.views.generic.list import ListView
from .models import *
from .common import GeoTreeFilter
from drf_spectacular.utils import extend_schema
from .serializers import CRUDLocationSerializer
from .serializers_READONLY import LocationSerializer

@extend_schema(
		exclude=True
	)
class LocationCREATE(generics.CreateAPIView):
	'''
	CREATE Source without a pk
	
	You must provide: value, name, longitude, latitude, and location_type as a nested object.
	
	For places and regions you *should* provide a parent in child_of field
	'''
	queryset=Location.objects.all()
	serializer_class=CRUDLocationSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]


class LocationRETRIEVE(generics.RetrieveAPIView):
	'''
	The lookup field for geographic locations is "VALUE". This corresponds to the legacy SPSS codes used for geo data -- first for voyage itineraries and ship construction/registration locations, but later on for enslaved peoples\' origins and final known locations, as well as for Enslavers\' place of birth etc. In the legacy SV website db, these 'Locations' were stored as separate models, hierarchically ordered.
	
		1. Place
		2. Region
		3. Broad Region
	
	While the SPSS codes / "value" fields in these models were supposed to be unique, this was not always the case. I therefore decided to collapse these into a single model, enforce the uniqueness of the value fields, create a location_type model to store these locations, and store the hierarchical relation through a child_of foreign key.
	'''
	queryset=Location.objects.all()
	serializer_class=LocationSerializer
	lookup_field='value'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

@extend_schema(
		exclude=True
	)
class LocationUPDATE(generics.UpdateAPIView):
	'''
	The lookup field for contributions is "VALUE". This corresponds to the legacy SPSS codes used for geo data -- first for voyage itineraries and ship construction/registration locations, but later on for enslaved peoples\' origins and final known locations, as well as for Enslavers\' place of birth etc. In the legacy SV website db, these 'Locations' were stored as separate models, hierarchically ordered.
	
		1. Place
		2. Region
		3. Broad Region
	
	While the SPSS codes / "value" fields in these models were supposed to be unique, this was not always the case. I therefore decided to collapse these into a single model, enforce the uniqueness of the value fields, create a location_type model to store these locations, and store the hierarchical relation through a child_of foreign key.
	'''
	queryset=Location.objects.all()
	serializer_class=CRUDLocationSerializer
	lookup_field='value'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class LocationDESTROY(generics.DestroyAPIView):
	'''
	The lookup field for contributions is "VALUE". This corresponds to the legacy SPSS codes used for geo data -- first for voyage itineraries and ship construction/registration locations, but later on for enslaved peoples\' origins and final known locations, as well as for Enslavers\' place of birth etc. In the legacy SV website db, these 'Locations' were stored as separate models, hierarchically ordered.
	'''
	queryset=Location.objects.all()
	serializer_class=CRUDLocationSerializer
	lookup_field='value'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]
