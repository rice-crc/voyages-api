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
from common.nest import *
from common.reqs import *
import collections

try:
	assessment_options=options_handler('assessment/assessment_options.json',hierarchical=False)
except:
	print("WARNING. BLANK ASSESSMENT OPTIONS.")
	assessment_options={}

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class AssessmentList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('assessment/assessment_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		#print("username:",request.auth.user)
		times=[]
		labels=[]
		print("FETCHING...")
		times.append(time.time())
		queryset=Estimate.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,assessment_options,auto_prefetch=True,retrieve_all=True)
		selected_fields=list(assessment_options.keys())
		times.append(time.time())
		labels.append('building query')
		times.append(time.time())
		labels.append('sql execution')
		output_dicts={}
		for sf in selected_fields:
			output_dicts[sf]=[v[0] for v in queryset.values_list(sf)]

		times.append(time.time())
		labels.append('flattening...')
		print('--timings--')
		for i in range(1,len(times)):
			print(labels[i-1],times[i]-times[i-1])		
		return JsonResponse(output_dicts,safe=False)