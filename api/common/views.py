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
import collections
import gc
from voyages3.localsettings import *
import re
import pysolr
from voyage.models import Voyage

class GlobalSearch(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("Global Search+++++++\nusername:",request.auth.user)
		
		params=dict(request.POST)
		search_string=params.get('search_string')
		# Oh, yes. Little Bobby Tables, we call him.
		search_string=re.sub("\s+"," ",search_string[0])
		search_string=search_string.strip()
		searchstringcomponents=[''.join(filter(str.isalnum,s)) for s in search_string.split(' ')]
		
		core_names= [
			'voyages',
			'enslaved',
			'enslavers',
			'blog'
		]
		
		output_dict=[]
		
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
			