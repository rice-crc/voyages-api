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
from blog.models import Post
from common.reqs import getJSONschema
import uuid
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
#this isn't pretty
#but i'm having trouble finding a more elegant way of exporting this data to an external service
#without installing networkx on this django instance, which i don't want to do!@extend_schema(exclude=True)

@extend_schema(exclude=True)
class PastGraphMaker(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		#VOYAGE DICT
		voys=Voyage.objects.all()
		voys.prefetch_related(
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location'
		)
		voys.select_related(
			'voyage_ship',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate'
		)
		voy_vals=voys.values_list(
			'id',
			'voyage_ship__ship_name',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name'
		)
		
		valkeys=[
			'id',
			'voyage_ship__ship_name',
			'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year',
			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name'
		]
		
		voy_df={
			k:[
				voy_vals[i][valkeys.index(k)] for i in range(len(voy_vals))
			]
			for k in valkeys
		}
				
		#ENSLAVER DICT
		enslaver_aliases=EnslaverAlias.objects.all()
		enslaver_aliases=enslaver_aliases.select_related('identity')
		enslaver_aliases_vals=enslaver_aliases.values_list(
			'id',
			'identity__id',
			'identity__principal_alias'
		)

		valkeys=(
			'alias_id',
			'id',
			'principal_alias'
		)
		
		enslaver_aliases_df={
			k:[
				enslaver_aliases_vals[i][valkeys.index(k)] for i in range(len(enslaver_aliases_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVED PEOPLE DICT
		enslaved_people=Enslaved.objects.all()
		enslaved_people_vals=enslaved_people.values_list(
			'id',
			'documented_name',
			'age',
			'gender'
		)
		
		valkeys=(
			'id',
			'documented_name',
			'age',
			'gender'
		)
		
		enslaved_people_df={
			k:[
				enslaved_people_vals[i][valkeys.index(k)] for i in range(len(enslaved_people_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVEMENT RELATION DICT
		enslavementrelations=EnslavementRelation.objects.all()
		enslavementrelations=enslavementrelations.select_related('relation_type')
		enslavementrelation_vals=enslavementrelations.values_list(
			'id',
			'relation_type__name',
			'voyage'
		)
		valkeys=(
			'id',
			'relation_type__name',
			'voyage'
		)
		
		enslavementrelation_df={
			k:[
				enslavementrelation_vals[i][valkeys.index(k)] for i in range(len(enslavementrelation_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVED IN RELATION
		enslaved_in_relation=EnslavedInRelation.objects.all()
		enslaved_in_relation_vals=enslaved_in_relation.values_list(
			'relation',
			'enslaved'
		)
		valkeys=(
			'relation',
			'enslaved'
		)
		
		enslaved_in_relation_df={
			k:[
				enslaved_in_relation_vals[i][valkeys.index(k)] for i in range(len(enslaved_in_relation_vals))
			]
			for k in valkeys
		}
		
		#ENSLAVER IN RELATION
		enslaver_in_relation=EnslaverInRelation.objects.all()
		enslaver_in_relation=enslaver_in_relation.select_related('role')
		enslaver_in_relation_vals=enslaver_in_relation.values_list(
			'relation',
			'enslaver_alias',
			'role__name'
		)
		valkeys=(
			'relation',
			'enslaver_alias',
			'role__name'
		)
		
		enslaver_in_relation_df={
			k:[
				enslaver_in_relation_vals[i][valkeys.index(k)] for i in range(len(enslaver_in_relation_vals))
			]
			for k in valkeys
		}
		
		relation_map={
			'enslaved':enslaved_people_df,
			'enslavers':enslaver_aliases_df,
			'voyages':voy_df,
			'enslavement_relations':enslavementrelation_df,
			'enslaved_in_relation':enslaved_in_relation_df,
			'enslavers_in_relation':enslaver_in_relation_df	
		}
		print("PAST GRAPH MAKER elapsed time:",time.time()-st)
		return JsonResponse(relation_map,safe=False)

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
		
		params=dict(request.POST)
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
			