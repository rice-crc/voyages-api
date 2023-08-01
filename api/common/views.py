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
from past.models import *
import uuid

#this isn't pretty
#but i'm having trouble finding a more elegant way of exporting this data to an external service
#without installing networkx on this django instance, which i don't want to do!
class VoyageGraphMaker(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		voys=Voyage.objects.all()
		voy_vals=voys.values_list(
			'id',
			'voyage_ship__ship_name',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name')
		
		voyage_id_map={uuid.uuid4():v[0] for v in voy_vals}
		
		enslavervoyageconnections=EnslaverVoyageConnection.objects.all()
		
		enslavervoyageconnection_vals=enslavervoyageconnections.values_list(
			'enslaver_alias_id',
			'voyage_id',
			'role__name'
		)
		
		enslaver_aliases=EnslaverAlias.objects.all()
		
		enslaver_alias_map={uuid.uuid4():v[0] for v in voy_vals}
		
		enslaver_aliases_vals=enslaver_aliases.values_list(
			'id',
			'alias',
			'identity_id'
		)
		
		enslaver_aliases_id_map={uuid.uuid4():a[0] for a in enslaver_aliases_vals}
		
		enslaver_identities=EnslaverIdentity.objects.all()
		
		enslaver_identities_vals=enslaver_identities.values_list(
			'id',
			'principal_alias',
			'principal_location__place',
			'birth_year',
			'death_year'
		)
		
		enslaver_identities_id_map={uuid.uuid4():ei[0] for ei in enslaver_identities_vals}
		
		enslaved_people=Enslaved.objects.all()
		
		enslaved_people_vals=enslaved_people.values_list(
			'id',
			'documented_name',
			'age',
			'gender'
		)
		
		enslaved_id_map={uuid.uuid4():e[0] for e in enslaved_people_vals}
		
		enslavementrelations=EnslavementRelation.objects.all()
		
		enslavementrelation_vals=enslavementrelations.values_list(
			'id',
			'relation_type__name'
		)
		
		enslaved_in_relation=EnslavedInRelation.objects.all()
		
		enslaved_in_relation_vals=enslaved_in_relation.values_list(
			'relation_id',
			'enslaved_id'
		)
		
		enslaver_in_relation=EnslaverInRelation.objects.all()
		
		enslaver_in_relation.values_list(
			'relation_id',
			'enslaver_alias_id',
			'role__name'
		)
		
		




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
			