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
from voyages3.localsettings import STATS_BASE_URL




#list view. Only keeping it around for the model
class AssessmentList(generics.RetrieveAPIView):	
	queryset=Estimate.objects.all()
	lookup_field='id'
	serializer_class=EstimateSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]


class EstimateDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The dataframes endpoint is mostly for internal use -- building up caches of data in the flask services.\n\
		However, it could be used for csv exports and the like.\n\
		Be careful! It's a resource hog.",
		request=EstimateDataframesRequestSerializer
	)
	def post(self,request):
		print("ESTIMATE DATAFRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		
		#VALIDATE THE REQUEST
		serialized_req = EstimateDataframesRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Estimate.objects.all()
# 		print(queryset)
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

class EstimateCrossTabs(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="Paginated crosstabs endpoint, with Pandas as the back-end.",
		request=EstimateCrossTabRequestSerializer,
		responses=EstimateCrossTabResponseSerializer
	)
	def post(self,request):
		st=time.time()
		print("ESTIMATE CROSSTABS+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = EstimateCrossTabRequestSerializer(data=request.data)
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
		
		#MAKE THE CROSSTABS REQUEST TO VOYAGES-STATS
		ids=[i[0] for i in queryset.values_list('id')]
		u2=STATS_BASE_URL+'pivot/'
		params=dict(request.data)
		stats_req_data=params
		stats_req_data['ids']=ids
		stats_req_data['cachename']='estimate_pivot_tables'
		r=requests.post(url=u2,data=json.dumps(stats_req_data),headers={"Content-type":"application/json"})
		
		#VALIDATE THE RESPONSE
		if r.ok:
			j=json.loads(r.text)
			serialized_resp=EstimateCrossTabResponseSerializer(data=j)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)