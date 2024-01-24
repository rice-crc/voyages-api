from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.template import loader
from django.shortcuts import redirect,render
from django.core.paginator import Paginator
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.views.generic.list import ListView
from collections import Counter
import urllib
import json
import requests
import time
from .models import *
import pprint
from common.reqs import *
import collections
import gc
from .serializers import *
from .serializers_READONLY import *
from voyages3.localsettings import REDIS_HOST,REDIS_PORT,DEBUG,GEO_NETWORKS_BASE_URL,PEOPLE_NETWORKS_BASE_URL,USE_REDIS_CACHE
import re
import redis
import hashlib
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from common.static.Source_options import Source_options
from rest_framework import filters

redis_cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

class SourceList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		request=SourceRequestSerializer,
		responses=SourceSerializer
	)
	
	def post(self,request):
		'''
		Voyages has always been built on scholarship, with references to many different archival sources. In the legacy version of the site, the sources were organized with a unique short reference ("short_ref") and a full reference ("full_ref"), like OMNO & Outward Manifests for New Orleans. When these sources were connected to Voyages, they would oftentimes be connected along with a field called "text_ref" that pointed at a specific location in the archive, or page number in the book.
		
		In this new build, we have moved all of our sources over to Zotero where they can be cleaned up -- the data got messy over the years, because bibliographical data is notoriously difficult to format. We now effectively have 2 unique keys: a Zotero ID and a "short_ref". We have also created records for individual pages that point at these new sources, because our work with several libraries on the South Seas Co. documents for an NEH grant means that we have images and page-level data for some new sources, allowing for unprecedented granularity in our work with archives.
		
		These changes necessitated that we create Docs as its own django app and endpoint. Now, each "Source" points at one or more Voyages, Enslaved People, or Enslavers. In turn, some of these Sources also have page-level metadata and links to IIIF images. For more information on the IIIF specification, visit https://iiif.io/api/index.html
		'''
		st=time.time()
		print("SOURCE LIST+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = SourceRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#AND ATTEMPT TO RETRIEVE A REDIS-CACHED RESPONSE
		if USE_REDIS_CACHE:
			srd=serialized_req.data
			hashdict={
				'req_name':str(self.request),
				'req_data':srd
			}
			hashed=hashlib.sha256(json.dumps(hashdict,sort_keys=True,indent=1).encode('utf-8')).hexdigest()
			cached_response = redis_cache.get(hashed)
		else:
			cached_response=None
			
		#RUN THE QUERY IF NOVEL, RETRIEVE IT IF CACHED
		if cached_response is None:
			#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
			queryset=Source.objects.all()
			queryset=queryset.order_by('id')
			queryset,results_count=post_req(	
				queryset,
				self,
				request,
				Source_options
			)

			results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
			resp=SourceListResponseSerializer({
				'count':total_results_count,
				'page':page_num,
				'page_size':page_size,
				'results':results
			}).data
			#I'm having the most difficult time in the world validating this nested paginated response
			#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
			#SAVE THIS NEW RESPONSE TO THE REDIS CACHE
			if USE_REDIS_CACHE:
				redis_cache.set(hashed,json.dumps(resp))
		else:
			resp=json.loads(cached_response)
		
		if DEBUG:
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			
		return JsonResponse(resp,safe=False,status=200)

class SourceRETRIEVE(generics.RetrieveAPIView):
	'''
	The lookup field for sources is the pk (id)
	'''
	queryset=Source.objects.all()
	serializer_class=SourceCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

#######################
# default view will be a paginated gallery
@extend_schema(
		exclude=True
	)
def Gallery(request,collection_id=None,pagenumber=1):
	
	if request.user.is_authenticated:
		
		#let's only get the zotero objects that have pages
		#otherwise, no need for the gallery -- and it lards the gallery up
		sources=Source.objects.order_by().all().filter(~Q(page_connections=None))
		
		other_collections=[]
		page_collection_id=None
		page_collection_label="No Collection Selected"
		for collection_tuple in sources.values_list(
			"short_ref__id",
			"short_ref__name"
		).distinct():
			this_collection_id,this_collection_label=collection_tuple
			if this_collection_id==collection_id:
				print(this_collection_id,this_collection_label)
				page_collection_label=this_collection_label
				page_collection_id=this_collection_id
			else:
				other_collections.append({
					"id":this_collection_id,
					"label":this_collection_label
				})
			
		sources=sources.filter(short_ref__id=collection_id).distinct()
		sources=sources.order_by('id')
		sources_paginator=Paginator(sources, 12)
		this_page=sources_paginator.get_page(pagenumber)
		
		return render(
			request,
			"gallery.html",
			{
				"page_collection_label":page_collection_label,
				"page_obj": this_page,
				"other_collections":other_collections,
				"page_collection_id":page_collection_id
			}
		)
	else:
		return HttpResponseForbidden("Forbidden")
		

#######################
# then the individual page view
@extend_schema(
		exclude=True
	)
def source_page(request,source_id=1):
	if request.user.is_authenticated:
		source=Source.objects.get(id=source_id)
		return render(request, "single_doc.html", {'source':source})
	else:
		return HttpResponseForbidden("Forbidden")

@extend_schema(
		exclude=True
	)
class SourceCREATE(generics.CreateAPIView):
	'''
	CREATE Source without a pk
	
	You must provide a ShortRef, which are our legacy short-text unique identifiers for documentary sources. A valid (< 100 chars) value in a nested short_ref field will create a new short ref if it does not already exist.
	
	Voyages, Enslaved, and Enslavers are presented in this model, but are set to read-only.
	'''
	queryset=Source.objects.all()
	serializer_class=SourceCRUDSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]
	
@extend_schema(
		exclude=True
	)
class SourceUPDATE(generics.UpdateAPIView):
	'''
	The lookup field for sources is the pk (id)
	
	Voyages, Enslaved, and Enslavers are presented in this model, but are set to read-only.
	'''
	queryset=Source.objects.all()
	serializer_class=SourceCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class SourceDESTROY(generics.DestroyAPIView):
	'''
	The lookup field for sources is the pk (id)
	
	Voyages, Enslaved, and Enslavers are presented in this model, but are set to read-only.
	'''
	queryset=Source.objects.all()
	serializer_class=SourceCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]