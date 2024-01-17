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
from common.static.Estimate_options import Estimate_options

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
# @extend_schema(
#         exclude=True
#     )
# #right now, this thing dumps all 7 MB out -- so we can't show it on swagger
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
		read_serializer=EstimateSerializer(queryset,many=True,read_only=True)
		serialized=read_serializer.data
		headers={"total_results_count":results_count}
		resp=JsonResponse(serialized,safe=False,headers=headers)
		return resp


class EstimateDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
# 	@extend_schema(
# 		description="The dataframes endpoint is mostly for internal use -- building up caches of data in the flask services.\n\
# 		However, it could be used for csv exports and the like.\n\
# 		Be careful! It's a resource hog. But more importantly, if you request fields that are not one-to-one relationships with the voyage, you're likely get back extra rows. For instance, requesting captain names will return one row for each captain, not for each voyage.\n\
# 		And finally, the example provided below puts a strict year filter on because unrestricted, it will break your swagger viewer :) \n\
# 		",
# 		request=VoyageDataframesRequestSerializer
# 	)
	def post(self,request):
		print("ESTIMATE DATAFRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		
		#VALIDATE THE REQUEST
		serialized_req = EstimatesDataframesRequestSerializer(data=request.data,read_only=True)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Estimate.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Estimate_options,
			auto_prefetch=True
		)
		
		queryset=queryset.order_by('id')
		sf=request.data.get('selected_fields')
		output_dicts={}
		vals=list(eval('queryset.values_list("'+'","'.join(sf)+'")'))
		for i in range(len(sf)):
			output_dicts[sf[i]]=[v[i] for v in vals]
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		## DIFFICULT TO VALIDATE THIS WITH A SERIALIZER -- NUMBER OF KEYS AND DATATYPES WITHIN THEM CHANGES DYNAMICALLY ACCORDING TO REQ
		
		return JsonResponse(output_dicts,safe=False)
