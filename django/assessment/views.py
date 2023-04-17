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
#from .prefetch_settings import *
from tools.nest import *
from tools.reqs import *
import collections

try:
	assessment_options=options_handler('assessment/assessment_options.json',hierarchical=False)
except:
	print("WARNING. BLANK DOCS OPTIONS.")
	assessment_options={}

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class AssessmentList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=EstimateSerializer
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
		queryset,selected_fields,next_uri,prev_uri,results_count=post_req(queryset,self,request,assessment_options,auto_prefetch=True,retrieve_all=True)
		selected_fields=list(assessment_options.keys())
		times.append(time.time())
		labels.append('building query')
		read_serializer=EstimateSerializer(queryset,many=True)
		times.append(time.time())
		labels.append('serialization')
		serialized=read_serializer.data
		times.append(time.time())
		labels.append('sql execution')
		output_dicts={}
		for selected_field in selected_fields:
			keychain=selected_field.split('__')
			for s in serialized:
				bottomval=bottomout(s,list(keychain))
				if selected_field in output_dicts:
					output_dicts[selected_field].append(bottomval)
				else:
					output_dicts[selected_field]=[bottomval]

		times.append(time.time())
		labels.append('flattening...')
		print('--timings--')
		for i in range(1,len(times)):
			print(labels[i-1],times[i]-times[i-1])		
		return JsonResponse(output_dicts,safe=False)