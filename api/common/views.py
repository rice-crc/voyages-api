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

		

@extend_schema(exclude=True)
class GlobalSearch(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("Global Search+++++++\nusername:",request.auth.user)
		
		params=dict(request.data)
		search_string=params.get('search_string')
		# Oh, yes. Little Bobby Tables, we call him.
		
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

		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(output_dict,safe=False)

# class SparseDateRD(generics.RetrieveDestroyAPIView):
# 	'''
# 	The lookup field for sparse dates is "id," the SQL primary key.
# 	
# 	Sparse dates consist of nullable integer month, day, and year fields. They are referenced by the voyages dates table as OneToOne relations.
# 	
# 	As OneToOne keys, they are built to be created for a specific field in another table to reference, updated only when that field\'s value needs updating, and destroyed as soon as they are no longer needed.
# 	
# 	Therefore, the "Create" (or in DRF PUT as Create) should only be used via referencing models. Here, we only want to be able to Retrieve or Destroy this data.
# 	'''
# 	queryset=SparseDate.objects.all()
# 	serializer_class=SparseDateSerializer
# 	lookup_field='id'
# 	authentication_classes=[TokenAuthentication]
# 	permission_classes=[IsAdminUser]