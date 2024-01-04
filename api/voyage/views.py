from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.views.generic.list import ListView
from rest_framework.pagination import PageNumberPagination
from collections import Counter
import urllib
import json
import requests
import time
from .models import *
import pprint
from rest_framework import filters
from common.reqs import *
from common.serializers import autocompleterequestserializer, autocompleteresponseserializer,crosstabresponseserializer,crosstabrequestserializer
from geo.common import GeoTreeFilter
import collections
import gc
from .serializers import *
from .serializers_READONLY import *
from geo.serializers_READONLY import LocationSerializer
from rest_framework import serializers
from voyages3.localsettings import *
from drf_yasg.utils import swagger_auto_schema
import re
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from common.static.Voyage_options import Voyage_options

class VoyageList(generics.GenericAPIView):
	permission_classes=[IsAuthenticated]
	authentication_classes=[TokenAuthentication]
	serializer_class=VoyageSerializer
	def post(self,request):
		'''
		This endpoint returns a list of nested objects, each of which contains all the available information on individual voyages.
		
		Voyages are the legacy natural unit of the project. They are useful because they gather together:
		
			1. Numbers of people and demographic data
			2. Geographic itinerary data
			3. Important dates
			4. Named individuals
			5. Documentary sources
			6. Data on the vessel
		
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.
		'''
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			retrieve_all=False
		)
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=VoyageSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

# # Basic statistics
# ## takes a numeric variable
# ## returns its sum, average, max, min, and stdv
@extend_schema(
		exclude=True
	)
class VoyageAggregations(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("VOYAGE AGGREGATIONS+++++++\nusername:",request.auth.user)
		params=dict(request.data)
		aggregations=params.get('aggregate_fields')
		print("aggregations:",aggregations)
		queryset=Voyage.objects.all()
		aggregation,selected_fields,results_count,error_messages=post_req(queryset,self,request,Voyage_options,retrieve_all=True)
		output_dict={}
		if len(error_messages)==0:
			for a in aggregation:
				print(a)
				for k in a:
					v=a[k]
					fn=k.split('__')[-1]
					varname=k[:-len(fn)-2]
					if varname in output_dict:
						output_dict[varname][fn]=a[k]
					else:
						output_dict[varname]={fn:a[k]}
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		else:
			print("failed\n",' | '.join(error_messages),"\n+++++++",)
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

@extend_schema(
		exclude=True
	)
class VoyageStatsOptions(generics.GenericAPIView):
	'''
	Need to make the stats engine's indexed variables transparent to the user
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		u2=STATS_BASE_URL+'get_indices/'
		r=requests.get(url=u2,headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)
	def options(self,request):
		u2=STATS_BASE_URL+'get_indices/'
		r=requests.get(url=u2,headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)


class VoyageCrossTabs(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="Paginated crosstabs endpoint, with Pandas as the back-end.",
		request=crosstabrequestserializer,
		responses=crosstabresponseserializer,
		examples=[	
			OpenApiExample(
				'Paginated request for binned years & embarkation geo vars',
				summary='Multi-level, paginated, 20-year bins',
				description='Here, we request cross-tabs on the geographic locations where enslaved people were embarked in 20-year periods. We also request that our columns be grouped in a multi-level way, from broad region to region and place. The cell value we wish to calculate is the number of people embarked, and we aggregate these as a sum. We are requesting the first 5 rows of these cross-tab results.',
				value={
					"columns":[
						"voyage_itinerary__imp_broad_region_of_slave_purchase__name",
						"voyage_itinerary__imp_principal_region_of_slave_purchase__name",
						"voyage_itinerary__imp_principal_place_of_slave_purchase__name"
					],
					"rows":"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
					"binsize": 20,
					"rows_label":"YEARAM",
					"agg_fn":"sum",
					"value_field":"voyage_slaves_numbers__imp_total_num_slaves_embarked",
					"offset":0,
					"limit":5
				},
				request_only=True,
				response_only=False
			)
		]
	
	)

	def post(self,request):
		st=time.time()
		print("VOYAGE CROSSTABS+++++++\nusername:",request.auth.user)
		params=dict(request.data)
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,Voyage_options,retrieve_all=True)
		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			u2=STATS_BASE_URL+'crosstabs/'
			params=dict(request.data)
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			if r.ok:
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				return JsonResponse(json.loads(r.text),safe=False)
			else:
				return JsonResponse({'status':'false','message':'bad groupby request'}, status=400)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

@extend_schema(
		exclude=True
	)
class VoyageGroupBy(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("VOYAGE GROUPBY+++++++\nusername:",request.auth.user)
		print(request.data)
		params=dict(request.data)
		print(params)
		groupby_by=params.get('groupby_by')
		groupby_cols=params.get('groupby_cols')
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,Voyage_options,retrieve_all=True)
		ids=[i[0] for i in queryset.values_list('id')]
		u2=STATS_BASE_URL+'groupby/'
		d2=params
		d2['ids']=ids
		d2['selected_fields']=selected_fields
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)# 

@extend_schema(
		exclude=True
	)
#DATAFRAME ENDPOINT (A resource hog -- internal use only!!)
class VoyageDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("VOYAGE DATAFRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		retrieve_all=True
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False,
			retrieve_all=True
		)
		queryset=queryset.order_by('id')
		sf=list(selected_fields)
		if len(error_messages)==0:
			output_dicts={}
			vals=list(eval('queryset.values_list("'+'","'.join(selected_fields)+'")'))
			for i in range(len(sf)):
				output_dicts[sf[i]]=[v[i] for v in vals]
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dicts,safe=False)
		else:
			print("failed\n+++++++")
			print(' | '.join(error_messages))
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

@extend_schema(
		exclude=True
	)
class VoyageGeoTreeFilter(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("VOYAGE GEO TREE FILTER+++++++\nusername:",request.auth.user)
		st=time.time()
		reqdict=dict(request.data)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,reqdict,Voyage_options,retrieve_all=True)
		for geotree_valuefield in geotree_valuefields:
			geotree_valuefield_stub='__'.join(geotree_valuefield.split('__')[:-1])
			queryset=queryset.select_related(geotree_valuefield_stub)
		vls=[]
		for geotree_valuefield in geotree_valuefields:		
			vls+=[i[0] for i in list(set(queryset.values_list(geotree_valuefield))) if i[0] is not None]
		vls=list(set(vls))
		filtered_geotree=GeoTreeFilter(spss_vals=vls)
		resp=JsonResponse(filtered_geotree,safe=False)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return resp

class VoyageCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	queryset=Voyage.objects.all()
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, the voyage). It also accepts filters. This means that you can apply any filter you would to any other query, for instance, the voyages list view, in the process of requesting your autocomplete suggestions, thereby rapidly narrowing your search.",
		request=autocompleterequestserializer,
		responses=autocompleteresponseserializer,
		examples = [
			OpenApiExample(
				'Autocomplete on any voyages-related field',
				summary='Filtered autocomplete for enslaver names like George',
				description='Here, we search for voyages that arrived btw 1820-1850 associated with enslavers whose names are like "George". As you can see from the "offset" and "limit" values, we are requesting five suggestions after 10, meaning we want 11,12,13,14,15. In other words, this is most likely a request for page 3.',
				value={
					"varname":"voyage_enslavement_relations__relation_enslavers__enslaver_alias__identity__principal_alias",
					"querystr":"george",
					"offset":10,
					"limit":5,
					"filter":{
						"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year":[1820,1840]
					}
				},
				request_only=True,
				response_only=False
			),
			OpenApiExample(
				'Suggested values are returned',
				summary='Filtered autocomplete for enslaver names like George',
				description='Here, we search for voyages that arrived btw 1820-1850 associated with enslavers whose names are like "George". We see five items (# 11,12,13,14,15) returned.',
				value={
					"varname":"voyage_enslavement_relations__relation_enslavers__enslaver_alias__identity__principal_alias",
					"querystr":"george",
					"offset":10,
					"limit":5,
					"filter":{
						"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year":[1820,1840]
					},
					"suggested_values":[
						{
							"value": "Brown, George"
						},
						{
							"value": "Bulloch, George L"
						},
						{
							"value": "Burdick, George"
						},
						{
							"value": "Burke, George"
						},
						{
							"value": "Burkley, George W"
						},
						{
							"value": "Callahan, George"
						}
					]
				},
				request_only=False,
				response_only=True
			)
		]
	)
	def post(self,request):
		st=time.time()
		queryset=Voyage.objects.all()
		print("VOYAGE CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		options=Voyage_options
		
		rdata=request.data

		varname=str(rdata.get('varname'))
		querystr=str(rdata.get('querystr'))
		offset=int(rdata.get('offset'))
		limit=int(rdata.get('limit'))
	
		max_offset=500
	
		if offset>max_offset:
			final_vals=[]
		else:
			queryset,selected_fields,results_count,error_messages=post_req(
				queryset,
				self,
				request,
				options,
				auto_prefetch=False,
				retrieve_all=True
			)
			final_vals=autocomplete_req(queryset,varname,querystr,offset,max_offset,limit)
		
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		resp=dict(rdata)
		resp['suggested_values']=final_vals
		
		read_serializer=autocompleteresponseserializer(resp)
		serialized=read_serializer.data
		
		print(' | '.join(error_messages))
		
		return JsonResponse(serialized,safe=False)

#This endpoint will build a geographic sankey diagram based on a voyages query
@extend_schema(
		exclude=True
	)
class VoyageAggRoutes(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		try:
			st=time.time()
			print("VOYAGE AGGREGATION ROUTES+++++++\nusername:",request.auth.user)
			params=dict(request.data)
			zoom_level=params.get('zoom_level')
			queryset=Voyage.objects.all()
			queryset,selected_fields,results_count,error_messages=post_req(
				queryset,
				self,
				request,
				Voyage_options,
				auto_prefetch=True,
				retrieve_all=True
			)
			queryset=queryset.order_by('id')
			zoomlevel=params.get('zoomlevel',['region'])[0]
			values_list=queryset.values_list('id')
			pks=[v[0] for v in values_list]
			django_query_time=time.time()
			print("Internal Django Response Time:",django_query_time-st,"\n+++++++")
			u2=GEO_NETWORKS_BASE_URL+'network_maps/'
			d2={
				'graphname':zoomlevel,
				'cachename':'voyage_maps',
				'pks':pks
			}
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			j=json.loads(r.text)
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(j,safe=False)
		except:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)


@extend_schema(
		exclude=True
	)
class VoyageCREATE(generics.CreateAPIView):
	'''
	Create Voyage without a pk
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageCRUDSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

class VoyageRETRIEVE(generics.RetrieveAPIView):
	'''
	The lookup field for contributions is "voyage_id". This corresponds to the legacy voyage_id unique identifiers. For create operations they should be chosen with care as they have semantic significance.
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class VoyageUPDATE(generics.UpdateAPIView):
	'''
	The lookup field for contributions is "voyage_id". This corresponds to the legacy voyage_id unique identifiers. For create operations they should be chosen with care as they have semantic significance.
	
	Previously, the SQL pk ("id") always corresponded to the "voyage_id" field. We will not be enforcing this going forward.
	
	M2M relations will not be writable here EXCEPT in the case of union/"through" tables.
	
	Examples:
	
		1. You CANNOT create an Enslaved (person) record as you traverse voyage_enslavement_relations >> relation_enslaved, but only the EnslavementRelation record that joins them
		2. You CAN create an EnslaverInRelation record as you traverse voyage_enslavement_relations >> relation_enslaver >> enslaver_alias >> enslaver_identity ...
		3. ... but you CANNOT create an EnslaverRole record during that traversal, like voyage_enslavement_relations >> relation_enslaver >> enslaver_role
	
	I have also, for the time, set all itinerary Location foreign keys as read_only.
	
	Godspeed.
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageCRUDSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class VoyageDESTROY(generics.DestroyAPIView):
	'''
	The lookup field for contributions is "voyage_id". This corresponds to the legacy voyage_id unique identifiers. For create operations they should be chosen with care as they have semantic significance.
	'''
	queryset=Voyage.objects.all()
	serializer_class=VoyageCRUDSerializer
	lookup_field='voyage_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]


