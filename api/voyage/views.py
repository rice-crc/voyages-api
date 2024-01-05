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
# from common.serializers import autocompleterequestserializer, autocompleteresponseserializer,crosstabresponseserializer,crosstabrequestserializer
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
	@extend_schema(
		description="\
		This endpoint returns a list of nested objects, each of which contains all the available information on individual voyages.\n\
		Voyages are the legacy natural unit of the project. They are useful because they gather together:\n\
			1. Numbers of people and demographic data\n\
			2. Geographic itinerary data\n\
			3. Important dates\n\
			4. Named individuals\n\
			5. Documentary sources\n\
			6. Data on the vessel\n\
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.\n\
		",
		request=VoyageListReqSerializer
	)
	
	def post(self,request):
		st=time.time()
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageListReqSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=True
		)
		
		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		
		resp=VoyageListRespSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		}).data
		
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)


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
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False
		)
		aggregation_field=request.data.get('aggregation_field')
		output_dict,errormessages=get_fieldstats(queryset,aggregation_field,Voyage_options)
		
		if len(errormessages)==0:
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

@extend_schema(
		exclude=True
	)
class VoyageCrossTabs(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="Paginated crosstabs endpoint, with Pandas as the back-end.",
		request=VoyageCrossTabRequestSerializer,
		responses=VoyageCrossTabResponseSerializer,
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
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Voyage_options
		)
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
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Voyage_options
		)
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
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False
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
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			reqdict,
			Voyage_options
		)
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
		request=VoyageAutoCompleteRequestSerializer,
		responses=VoyageAutoCompleteResponseSerializer,
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = VoyageAutoCompleteRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Voyage.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Voyage_options,
			auto_prefetch=False
		)
		
		#RUN THE AUTOCOMPLETE ALGORITHM
		final_vals=autocomplete_req(queryset,request)
		resp=dict(request.data)
		resp['suggested_values']=final_vals
		
		#VALIDATE THE RESPONSE
		serialized_resp=VoyageAutoCompleteResponseSerializer(data=resp)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

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
			queryset,results_count,error_messages=post_req(
				queryset,
				self,
				request,
				Voyage_options,
				auto_prefetch=True
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

@extend_schema(
		exclude=True
	)
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


