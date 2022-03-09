from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
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

d=open('assessment/assessment_options.json','r')
assessment_options=(json.loads(d.read()))
d.close()

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class AssessmentList(generics.GenericAPIView):
	serializer_class=EstimateSerializer
	def options(self,request):
		schema=options_handler(self,request,flatfile=assessment_options,auto='False')
		return JsonResponse(schema,safe=False)
	def get(self,request):
		r=requests.options("http://127.0.0.1:8000/assessment/?hierarchical=False&auto=False")
		options=json.loads(r.text)
		times=[]
		labels=[]
		print("FETCHING...")
		times.append(time.time())
		queryset=Estimate.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count=get_req(queryset,self,request,options,retrieve_all=True)
		selected_fields=list(options.keys())
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