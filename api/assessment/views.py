from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from django.views.generic.list import ListView
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
import pprint
from common.reqs import *
import collections
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class AssessmentList(generics.GenericAPIView):
	serializer_class=EstimateSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		#print("username:",request.auth.user)
		times=[]
		labels=[]
		print("FETCHING...")
		times.append(time.time())
		queryset=Estimate.objects.all()
		estimate_options=getJSONschema('Estimate',hierarchical=False)
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			estimate_options,
			auto_prefetch=True,
			retrieve_all=True
		)
		read_serializer=EstimateSerializer(queryset,many=True)
		serialized=read_serializer.data
		headers={"total_results_count":results_count}
		resp=JsonResponse(serialized,safe=False,headers=headers)
		return resp