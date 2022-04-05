from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
import pprint
from tools.nest import *
from tools.reqs import *
import collections

#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class EnslavedList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=EnslavedSerializer
	def options(self,request):
		j=options_handler('past/past_options.json',request)
		return JsonResponse(j,safe=False)
	def get(self,request):
		#print("username:",request.auth.user)
		times=[]
		labels=[]
		print("FETCHING...")
		times.append(time.time())
		queryset=Enslaved.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count=get_req(queryset,self,request,past_options,auto_prefetch=True)
		headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
		#read_serializer=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
		times.append(time.time())
		labels.append('building query')
		read_serializer=EnslavedSerializer(queryset,many=True)
		times.append(time.time())
		labels.append('serialization')
		serialized=read_serializer.data
		times.append(time.time())
		labels.append('sql execution')
			
		outputs=[]
		
		hierarchical=True
		if 'hierarchical' in request.query_params:
			if request.query_params['hierarchical'].lower() in ['false','0','n']:
				hierarchical=False
		
		if hierarchical==False:
			if selected_fields==[]:
				selected_fields=[i for i in past_options]
			
			for s in serialized:
				d={}
				for selected_field in selected_fields:
					keychain=selected_field.split('__')
					bottomval=bottomout(s,list(keychain))
					d[selected_field]=bottomval
				outputs.append(d)
		else:
			outputs=serialized
		times.append(time.time())
		labels.append('flattening...')
		print('--timings--')
		for i in range(1,len(times)):
			print(labels[i-1],times[i]-times[i-1])		
		return JsonResponse(outputs,safe=False,headers=headers)
	def post(self,request):
		times=[]
		labels=[]
		print("FETCHING...")
		times.append(time.time())
		queryset=Enslaved.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count=post_req(queryset,self,request,past_options,auto_prefetch=True)
		headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
		times.append(time.time())
		labels.append('building query')
		read_serializer=EnslavedSerializer(queryset,many=True)
		times.append(time.time())
		labels.append('serialization')
		serialized=read_serializer.data
		times.append(time.time())
		labels.append('sql execution')
			
		outputs=[]
		
		hierarchical=request.POST.get('hierarchical')
		if str(hierarchical).lower() in ['false','0','f','n']:
			hierarchical=False
		else:
			hierarchical=True
		
		if hierarchical==False:
			if selected_fields==[]:
				selected_fields=[i for i in past_options]
			
			for s in serialized:
				d={}
				for selected_field in selected_fields:
					keychain=selected_field.split('__')
					bottomval=bottomout(s,list(keychain))
					d[selected_field]=bottomval
				outputs.append(d)
		else:
			outputs=serialized
		times.append(time.time())
		labels.append('flattening...')
		print('--timings--')
		for i in range(1,len(times)):
			print(labels[i-1],times[i]-times[i-1])		
		return JsonResponse(outputs,safe=False,headers=headers)