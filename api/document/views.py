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
from common.nest import *
from common.reqs import *
import collections
import gc
from .serializers import *
from voyages3.localsettings import *
import re
from django.db.models import Q

try:
	zotero_source_options=options_handler('document/zotero_source_options.json',hierarchical=False)
except:
	print("WARNING. BLANK ZOTERO OPTIONS.")
	zotero_source_options={}

class ZoteroSourceList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('document/zotero_source_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		queryset=ZoteroSource.objects.all()
		queryset=queryset.order_by('id')
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,zotero_source_options,retrieve_all=False)
		
		if len(error_messages)==0:
			st=time.time()
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
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
def z_source_page(request,zotero_source_id=1):
	
	if request.user.is_authenticated:
# 		print(zotero_source_id)
		doc=ZoteroSource.objects.get(id=zotero_source_id)
		
# 		print(doc)
		return render(request, "single_doc.html", {'zs':doc})
	else:
		return HttpResponseForbidden("Forbidden")