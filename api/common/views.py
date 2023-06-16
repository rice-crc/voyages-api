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
		core_name='voyages'
		
		solr = pysolr.Solr(
				'http://voyages-solr:8983/solr/%s/' %core_name,
				always_commit=True,
				timeout=10
			)
		finalsearchstring="(%s)" %(" ").join(searchstringcomponents)
		results=solr.search('text:%s' %finalsearchstring)
		results_count=results.hits
		if results_count>0:
			top_ids=[r['id'] for r in results]
			top_voys=Voyage.objects.all().filter(id__in=top_ids)
			vls=top_voys.values_list(
				'id',
				'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year',
				'voyage_ship__ship_name',
				'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name',
				'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name'
			)
# 			print(vls)
			voys={i[0]:i[1:] for i in vls}
			voynullscore={i:0 for i in voys}
			for voy in voys:
				for i in voys[voy]:
					if voys[voy] is None:
						voynullscore[voy]+=1
			
			od = collections.OrderedDict(sorted(voynullscore.items()))
			od=list(od)
			topvoy=voys[od[-1]]
			voyage_id=topvoy[0]
			
			ship_name = topvoy[1]
			if ship_name.strip()=='':
				ship_name = None
			
			if topvoy[2] is not None or topvoy[3] is not None:
				a=topvoy[2]
				b=topvoy[3]
				if topvoy[2] is None:
					a="?"
				if topvoy[3] is None:
					b="?"
				if ship_name is not None:
					itineraryvals="(%s to %s)" %(a,b)
				else:
					itineraryvals="%s to %s" %(a,b)
			else:
				itineraryvals = None
			
			yearam=str(topvoy[0])
			
			outputstrlist=[]
			if ship_name is not None:
				outputstrlist.append(ship_name)
			if yearam is not None:
				if ship_name is not None and itineraryvals is not None:
					outputstrlist.append("(%s)" %yearam)
				else:
					outputstrlist.append("%s" %yearam)
			if itineraryvals is not None:
				outputstrlist.append(itineraryvals)
			if len(outputstrlist)<=1:
				outputstr="# %s" %voyage_id
			else:
				outputstr=" ".join(outputstrlist)
			
			output_dict=[
				{
					"type": "Voyages",
					"label": outputstr,
					"results_count":results_count
				}
			]
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
			