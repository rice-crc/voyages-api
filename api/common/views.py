from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.views.generic.list import ListView
from collections import Counter
import urllib
import json
import requests
import time
import collections
import gc
from voyages3.localsettings import *
import re
import pysolr
from .serializers import *
from voyage.models import Voyage
from past.models import *
from blog.models import Post
from common.reqs import getJSONschema
import uuid
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema(exclude=True)
class Schemas(generics.GenericAPIView):
	def get(self,request):
		schema_name=request.GET.get('schema_name')
		hierarchical=request.GET.get('hierarchical')
		if schema_name is not None and hierarchical is not None:
			schema_json=getJSONschema(schema_name,hierarchical)
			return JsonResponse(schema_json,safe=False)
		else:
			return JsonResponse({'status':'false','message':'you must specify schema_name (string) and hierarchical (boolean)'}, status=502)

		

class GlobalSearch(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint takes a string and passes it on to Solr, which searches across all indexed text fields (currently all text fields) in our core models (Voyages, Enslaved People, Enslavers, and Blog Posts [documents next...]). It returns counts and the first 10 primary keys for each",
		request=GlobalSearchRequestSerializer,
		responses=GlobalSearchResponseItemSerializer
	)
	def post(self,request):
		st=time.time()
		print("Global Search+++++++\nusername:",request.auth.user)
		
		params=dict(request.data)
		search_string=params.get('search_string')
		# Oh, yes. Little Bobby Tables, we call him.
		
		#VALIDATE THE REQUEST
		serialized_req = GlobalSearchRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		output_dict=[]
		coretuples=[
			['voyages',Voyage.objects.all()],
			['enslaved',Enslaved.objects.all()],
			['enslavers',EnslaverIdentity.objects.all()],
			['blog',Post.objects.all()]
		]
		
		if search_string is None:
		
			for core in coretuples:
				corename,qset=core
				results_count=qset.count()
				topten_ids=[i[0] for i in qset[:9].values_list('id')]
				output_dict.append({
					'type':corename,
					'results_count':results_count,
					'ids':topten_ids
				})
		else:
			search_string=search_string[0]
			search_string=re.sub("\s+"," ",search_string)
			search_string=search_string.strip()
			searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in search_string.split(' ')]
		
			core_names=[ct[0] for ct in coretuples]
		
			for core_name in core_names:
		
				solr = pysolr.Solr(
						'http://voyages-solr:8983/solr/%s/' %core_name,
						always_commit=True,
						timeout=10
					)
				finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
				results=solr.search('text:%s' %finalsearchstring)
				results_count=results.hits
				ids=[r['id'] for r in results]
				output_dict.append({
					'type':core_name,
					'results_count':results_count,
					'ids':ids
				})

		#VALIDATE THE RESPONSE
		serialized_resp=GlobalSearchResponseItemSerializer(data=output_dict,many=True)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)