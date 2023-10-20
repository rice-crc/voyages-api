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
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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
from voyages3.localsettings import *
import re
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class ZoteroSourceList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=SourceSerializer
	def post(self,request):
		'''
		Voyages has always been built on scholarship, with references to many different archival sources. In the legacy version of the site, the sources were organized with a unique short reference ("short_ref") and a full reference ("full_ref"), like OMNO & Outward Manifests for New Orleans. When these sources were connected to Voyages, they would oftentimes be connected along with a field called "text_ref" that pointed at a specific location in the archive, or page number in the book.
		
		In this new build, we have moved all of our sources over to Zotero where they can be cleaned up -- the data got messy over the years, because bibliographical data is notoriously difficult to format. We now effectively have 2 unique keys: a Zotero ID and a "short_ref". We have also created records for individual pages that point at these new sources, because our work with several libraries on the South Seas Co. documents for an NEH grant means that we have images and page-level data for some new sources, allowing for unprecedented granularity in our work with archives.
		
		These changes necessitated that we create Docs as its own django app and endpoint. Now, each "ZoteroSource" points at one or more Voyages, Enslaved People, or Enslavers. In turn, some of these Sources also have page-level metadata and links to IIIF images. For more information on the IIIF specification, visit https://iiif.io/api/index.html
		'''
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		queryset=ZoteroSource.objects.all()
		queryset=queryset.order_by('id')
		zotero_source_options=getJSONschema('ZoteroSource',hierarchical=False)
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			zotero_source_options,
			retrieve_all=False
		)
		
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=ZoteroSourceSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

#######################
# default view will be a paginated gallery
@extend_schema(
        exclude=True
    )
def Gallery(request,collection_id=None,pagenumber=1):
	
	if request.user.is_authenticated:
		
		#let's only get the zotero objects that have pages
		#otherwise, no need for the gallery -- and it lards the gallery up
		docs=ZoteroSource.objects.order_by().all().filter(~Q(page_connection=None))
		
		other_collections=[]
		for collection_tuple in docs.values_list(
			"legacy_source__id",
			"legacy_source__short_ref"
		).distinct():
			
			this_collection_id,this_collection_label=collection_tuple
			
			if this_collection_id==collection_id:
				page_collection_label=this_collection_label
				page_collection_id=this_collection_id
			else:
				other_collections.append({
					"id":this_collection_id,
					"label":this_collection_label
				})
			
		if collection_id is None:
			
			page_collection_id=min(docs.values_list('legacy_source__id'))[0]
			
			page_collection_label=docs.filter(legacy_source__id=page_collection_id).first().legacy_source.short_ref
			
		docs=docs.filter(legacy_source__id=collection_id).distinct()
		docs=docs.order_by('id')
		docs_paginator=Paginator(docs, 12)
		this_page=docs_paginator.get_page(pagenumber)
		
# 		print(other_collections)
		
		return render(
			request,
			"gallery.html",
			{
				"page_obj": this_page,
				"other_collections":other_collections,
				"page_collection_label":page_collection_label,
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
def z_source_page(request,zotero_source_id=1):
	
	if request.user.is_authenticated:
# 		print(zotero_source_id)
		doc=ZoteroSource.objects.get(id=zotero_source_id)
		
# 		print(doc)
		return render(request, "single_doc.html", {'zs':doc})
	else:
		return HttpResponseForbidden("Forbidden")