from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
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
from django.views.generic.base import TemplateView
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
import networkx as nx

location_options=options_handler('geo/location_options.json',hierarchical=False)




class LocationList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer
	def options(self,request):
		j=options_handler('geo/location_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		try:
			times=[]
			labels=[]
			#print("+++++++\nusername:",request.auth.user)
			print("+++++++\nGEO")
			st=time.time()
			queryset=Location.objects.all()
			queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,location_options,auto_prefetch=True,retrieve_all=True)
			if len(error_messages)==0:
				headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
				labels.append('building query')
				read_serializer=LocationSerializer(queryset,many=True)
				labels.append('serialization')
				serialized=read_serializer.data
				labels.append('sql execution')
			
				outputs=[]
		
				hierarchical=request.POST.get('hierarchical')
				if str(hierarchical).lower() in ['false','0','f','n']:
					hierarchical=False
				else:
					hierarchical=True
		
				if hierarchical==False:
					if selected_fields==[]:
						selected_fields=[i for i in location_options]
			
					for s in serialized:
						d={}
						for selected_field in selected_fields:
							keychain=selected_field.split('__')
							bottomval=bottomout(s,list(keychain))
							d[selected_field]=bottomval
						outputs.append(d)
				else:
					outputs=serialized
				labels.append('flattening...')
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				for i in range(1,len(times)):
					print(labels[i-1],times[i]-times[i-1])		
				return JsonResponse(outputs,safe=False,headers=headers)
			else:
				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)
		except:
			return JsonResponse({'status':'false','message':'geo request failed'}, status=500)


class getGeoJsonNetwork(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer	
	def post(self,request):
		try:
			print("+++++++\nFULL GeoJSON Network")
			st=time.time()
			adjacencies=Adjacency.objects.all()
			routes_featurecollection={"type":"FeatureCollection","features":[]}
			prefetch_fields=[
				'source',
				'target'
			]
			for f in prefetch_fields:
				adjacencies=adjacencies.prefetch_related(f)
		
			for adjacency in adjacencies:
				adj_id=adjacency.id
				source=adjacency.source
				target=adjacency.target
				routes_featurecollection['features'].append({
				"type":"Feature",
				"geometry":{
					"id":adj_id,
					"type":"LineString",
					"coordinates":[
						(source.longitude,source.latitude),
						(target.longitude,target.latitude)
					]
				},
				"properties":{"source_id":source.id,"target_id":target.id}
				})
		
			print("Internal Response Time:",time.time()-st,"\n+++++++")
		
			#d=open('routes.json','w')
			#d.write(json.dumps(routes_featurecollection,cls=DjangoJSONEncoder))
			#d.close()
		
			return JsonResponse(routes_featurecollection,safe=False)
		except:
			return JsonResponse({'status':'false','message':'geo request failed'}, status=500)

class getRoutes(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer	
	def post(self,request):
	
		return JsonResponse({},safe=False)