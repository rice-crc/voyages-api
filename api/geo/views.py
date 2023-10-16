from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
import time
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from .models import *
from .common import GeoTreeFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
        exclude=True
    )
class GeoTree(generics.GenericAPIView):
	# serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("GEO TREE+++++++\nusername:",request.auth.user)
		locationtree=GeoTreeFilter(select_all=True)
		resp=JsonResponse(locationtree,safe=False)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return resp