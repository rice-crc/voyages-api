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
from voyages3.localsettings import *
import re
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from common.static.Source_options import Source_options
from rest_framework import filters

class SourceList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=SourceSerializer
	def post(self,request):
		'''
		Voyages has always been built on scholarship, with references to many different archival sources. In the legacy version of the site, the sources were organized with a unique short reference ("short_ref") and a full reference ("full_ref"), like OMNO & Outward Manifests for New Orleans. When these sources were connected to Voyages, they would oftentimes be connected along with a field called "text_ref" that pointed at a specific location in the archive, or page number in the book.
		
		In this new build, we have moved all of our sources over to Zotero where they can be cleaned up -- the data got messy over the years, because bibliographical data is notoriously difficult to format. We now effectively have 2 unique keys: a Zotero ID and a "short_ref". We have also created records for individual pages that point at these new sources, because our work with several libraries on the South Seas Co. documents for an NEH grant means that we have images and page-level data for some new sources, allowing for unprecedented granularity in our work with archives.
		
		These changes necessitated that we create Docs as its own django app and endpoint. Now, each "Source" points at one or more Voyages, Enslaved People, or Enslavers. In turn, some of these Sources also have page-level metadata and links to IIIF images. For more information on the IIIF specification, visit https://iiif.io/api/index.html
		'''
		print("SOURCE LIST+++++++\nusername:",request.auth.user)
		queryset=Source.objects.all()
		queryset=queryset.order_by('id')
		source_options=getJSONschema('Source',hierarchical=False)
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			source_options,
			retrieve_all=False
		)
		
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=SourceSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

class SourceListGENERIC(generics.ListAPIView):
	'''
	TESTING A GENERIC, EASY-TO-SEARCH, PAGINATED LIST OF SOURCES FOR DELLAMONICA & SSC
	
	GET queries to this endpoint with the param "search" will search the following:
	
		A. EXACT on 
			1. "short_ref__name", e.g. 1713Poll
			2. "date__year", e.g. 1982
			3. "zotero_item_id", e.g. FPGTSQXM
		B. ICOMPLETE on "title"
	
	Because sources have massively nested data in some cases, I have had to restrict us to a maximum of 5 results per page.
	
	DON'T search OMNO in Swagger. My server can take Daniel Domingues Texas data, but your browser cannot :)
	'''
	queryset=Source.objects.all()
	queryset.prefetch_related(
		'page_connections',
		'source_enslaver_connections',
		'source_voyage_connections',
		'source_enslaved_connections',
		'source_enslavement_relation_connections'
	)
	queryset.select_related(
		'short_ref',
		'date'
	)
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=SourceSerializer
	filter_backends = [filters.SearchFilter]
	search_fields = ['title','=date__year','short_ref__name','=zotero_item_id']

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

class ShortRefCREATE(generics.CreateAPIView):
	'''
	Shortrefs by canonical name, like "OMNO", "IMNO", or "DOCP Huntington 57 21"
	'''
	queryset=ShortRef.objects.all()
	serializer_class=CRUDShortRefSerializer
	lookup_field='name'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

class ShortRefRETRIEVE(generics.RetrieveAPIView):
	'''
	Shortrefs by canonical name, like "OMNO", "IMNO", or "DOCP Huntington 57 21"
	
	These used to be unique values on the sources table in Voyages. In that legacy model, we had a short_ref and a full_ref for each source, and then, in our union table with voyages, we had a text_ref field where we would put page numbers, or box and folder numbers, etc. However, this led to a good deal of schema abuse (duplication, inconsistent use of fields, etc.)
	
	In the new model, we maintain the uniqueness of Short Ref's but we allow many Source objects to connect to these short ref's. The new source objects have much more, and much more structured data, being managed remotely in Zotero. Each source therefore now has an additional unique identifier: its Zotero Item ID.
	
	It could make sense to give these short refs their own Zotero listings.
	'''
	queryset=ShortRef.objects.all()
	serializer_class=ShortRefSerializer
	lookup_field='name'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

class ShortRefUPDATE(generics.UpdateAPIView):
	'''
	Shortrefs by canonical name, like "OMNO", "IMNO", or "DOCP Huntington 57 21"
	'''
	queryset=ShortRef.objects.all()
	serializer_class=CRUDShortRefSerializer
	lookup_field='name'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

class ShortRefDESTROY(generics.DestroyAPIView):
	'''
	Shortrefs by canonical name, like "OMNO", "IMNO", or "DOCP Huntington 57 21"
	'''
	queryset=ShortRef.objects.all()
	serializer_class=CRUDShortRefSerializer
	lookup_field='name'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

	
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
	
class SourceRETRIEVE(generics.RetrieveAPIView):
	'''
	The lookup field for sources is the pk (id)
	'''
	queryset=Source.objects.all()
	serializer_class=SourceSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

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