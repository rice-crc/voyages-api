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
from geo.common import GeoTreeFilter
import collections
import gc
from .serializers import *
from geo.serializers import LocationSerializer
from voyages3.localsettings import *
from drf_yasg.utils import swagger_auto_schema
import re
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

try:
	voyage_options=options_handler('voyage/voyage_options.json',hierarchical=False)
except:
	print("WARNING. BLANK VOYAGE OPTIONS.")
	voyage_options={}

# #LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!

class VoyageList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
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
		
		You can filter on any of the nested fields by 
		'''
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=False)
		if len(error_messages)==0:
			st=time.time()
			headers={"total_results_count":results_count}
			read_serializer=VoyageSerializer(queryset,many=True)
			serialized=read_serializer.data
			resp=JsonResponse(serialized,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

# # Basic statistics
# ## takes a numeric variable
# ## returns its sum, average, max, min, and stdv
class VoyageAggregations(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("VOYAGE AGGREGATIONS+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		aggregations=params.get('aggregate_fields')
		print("aggregations:",aggregations)
		queryset=Voyage.objects.all()
		aggregation,selected_fields,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
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
	'''
	I was only able to figure out how to output a true pivot table (multi levels and columns) as a straight html dump from pandas.
	Moreover, if I styled it at all (tagged the <td>'s with id's for jquery), the size ballooned.
	Instead, then, we'll go with a custom ag-grid JS dump that can accommodate multi-level cols, but not multi-level rows.	
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("VOYAGE CROSSTABS+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			u2=STATS_BASE_URL+'crosstabs/'
			params=dict(request.POST)
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

class VoyageGroupBy(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("VOYAGE GROUPBY+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		print(params)
		groupby_by=params.get('groupby_by')
		groupby_cols=params.get('groupby_cols')
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		ids=[i[0] for i in queryset.values_list('id')]
		u2=STATS_BASE_URL+'groupby/'
		d2=params
		d2['ids']=ids
		d2['selected_fields']=selected_fields
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)# 

#DATAFRAME ENDPOINT (A resource hog -- internal use only!!)
class VoyageDataFrames(generics.GenericAPIView):
# 	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("VOYAGE DATAFRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.POST)
		retrieve_all=True
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			voyage_options,
			auto_prefetch=False,
			retrieve_all=True
		)
		queryset=queryset.order_by('id')
		sf=list(selected_fields)
		if len(error_messages)==0:
			output_dicts={}
			for s in sf:
				output_dicts[s]=[i[0] for i in queryset.values_list(s)]
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dicts,safe=False)
		else:
			print("failed\n+++++++")
			print(' | '.join(error_messages))
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)


class VoyageGeoTreeFilter(generics.GenericAPIView):
	if not no_auth:
		authentication_classes=[TokenAuthentication]
		permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		if not no_auth:
			print("VOYAGE GEO TREE FILTER+++++++\nusername:",request.auth.user)
			
		st=time.time()
		reqdict=dict(request.POST)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(queryset,self,reqdict,voyage_options,retrieve_all=True)
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


#This will only accept one field at a time
#Should only be a text field
#And it will only return max 10 results
#It will therefore serve as an autocomplete endpoint
#I should make all text queries into 'or' queries
class VoyageCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("VOYAGE CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
# 		try:
		st=time.time()
		params=dict(request.POST)
		print(params)
		k=list(params.keys())[0]
		v=params[k][0]
		
		print("voyage/autocomplete",k,v)
		queryset=Voyage.objects.all()
		if '__' in k:
			kstub='__'.join(k.split('__')[:-1])
			k_id_field=kstub+"__id"
			queryset=queryset.prefetch_related(kstub)
		else:
			k_id_field="id"
		kwargs={'{0}__{1}'.format(k, 'icontains'):v}
		queryset=queryset.filter(**kwargs)
		queryset=queryset.order_by(k)
		total_results_count=queryset.count()
		candidates=[]
		candidate_vals=[]
		fetchcount=30
		## Have to use this ugliness b/c we're not in postgres
		## https://docs.djangoproject.com/en/4.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct
		for v in queryset.values_list(k_id_field,k).iterator():
			if v[1] not in candidate_vals:
				candidates.append(v)
				candidate_vals.append(v[1])
			if len(candidates)>=fetchcount:
				break

		res={
			"total_results_count":total_results_count,
			"results":[
				{
					"id":c[0],
					"label":c[1]
				} for c in candidates
			]
		}
		
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(res,safe=False)
# 		except:
# 			print("failed\n+++++++")
# 			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)

#This endpoint will build a geographic sankey diagram based on a voyages query
class VoyageAggRoutes(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
# 		try:
		st=time.time()
		print("VOYAGE AGGREGATION ROUTES+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		zoom_level=params.get('zoom_level')
		queryset=Voyage.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			voyage_options,
			auto_prefetch=True,
			retrieve_all=True
		)
		
		queryset=queryset.order_by('id')

		zoomlevel=params.get('zoomlevel',['region'])[0]
		
		if zoomlevel not in ['region','place']:
			zoomlevel='region'
		
		if zoomlevel=='place':
			voys_values_list=queryset.values_list(
				'voyage_id',
				'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__uuid',
				'voyage_itinerary__imp_principal_port_slave_dis__geo_location__uuid',
				'voyage_slaves_numbers__imp_total_num_slaves_embarked'
			)
			graphname='place'
		elif zoomlevel=='region':
			voys_values_list=queryset.values_list(
				'voyage_id',
				'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__uuid',
				'voyage_itinerary__imp_principal_region_slave_dis__geo_location__uuid',
				'voyage_slaves_numbers__imp_total_num_slaves_embarked'
			)
			graphname='region'
		
		voys_vals_dict={"__".join([str(i) for i in vvs[1:3]]):0 for vvs in voys_values_list}
		
		bad_voyages=[]
		for v in voys_values_list:
			vk="__".join([str(i) for i in v[1:3]])
			val=v[3]
			if val is not None:
				voys_vals_dict[vk]+=val
			else:
				bad_voyages.append(val)
		
		print("COULD NOT MAP %d VOYAGES" %len(bad_voyages))
		
		u2=GEO_NETWORKS_BASE_URL+'network_maps/'
		d2={
			'graphname':graphname,
			'cachename':'voyage_maps',
			'payload':voys_vals_dict,
			'linklabels':['transportation'],
			'nodelabels':[
				'embarkation',
				'disembarkation'
			]
		}
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		j=json.loads(r.text)
		
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(j,safe=False)