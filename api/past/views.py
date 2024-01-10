from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
from .serializers_READONLY import *
import pprint
from common.reqs import *
from collections import Counter
from geo.common import GeoTreeFilter
from geo.serializers_READONLY import LocationSerializer,LocationSerializerDeep
from voyages3.localsettings import *
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from common.static.Enslaver_options import Enslaver_options
from common.static.Enslaved_options import Enslaved_options
from common.serializers import autocompleterequestserializer, autocompleteresponseserializer

class EnslavedList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint returns a list of highly nested objects, each of which contains all the available information on enslaved individuals who we know to have been transported on a voyage.\
		This people-oriented data dramatically changes the nature of our dataset. While Voyages data has always been relational, the complexity of interpersonal connections in this dataset makes it graph-like and pushes the boundaries of the underlying system (Python Django).\
		For instance, you might search for a person who was bought, sold, or transported on a voyage owned by a known enslaver. Or, you might search for people who, based on the sound of their name as recorded, are believed to have come from a particular region in Africa where an ethnic group known to use that name was located.\
		However, it must be stressed that there is a tension in this dataset: the data that we have on enslaved individuals was almost entirely recorded by the people who enslaved them, or by colonial managers who technically liberated them, but oftentimes pressed these people into military service or labor. We know the names of these people, which is grounbreaking for this project because it allows us to identify named individuals in a dataset that often records only nameless quantities of people, but as you analyze this dataset you will note that most of the data we have on these enslaved people is bio-data, such as gender, age, height, and skin color -- this is qualitatively different than the data we have on the enslavers, about whom we often have a good deal of biographical data.\
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.",
		request=EnslavedListRequestSerializer,
		responses=EnslavedListResponseSerializer
	)
	def post(self,request):
		
		st=time.time()
		print("ENSLAVED LIST+++++++\nusername:",request.auth.user)
		#VALIDATE THE REQUEST
		serialized_req = EnslavedListRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE ENSLAVED PEOPLE ENTRIES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Enslaved.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaved_options,
			auto_prefetch=True
		)

		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		resp=EnslavedListResponseSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		}).data
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)
		
class EnslavedCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, enslaved people). It also accepts filters. This means that you can apply any filter you would to any other query, for instance, the enslavers list view, in the process of requesting your autocomplete suggestions, thereby rapidly narrowing your search.",
		request=EnslavedAutoCompleteRequestSerializer,
		responses=EnslavedAutoCompleteResponseSerializer,
	)	
	def post(self,request):
		st=time.time()
		print("ENSLAVED CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = EnslavedAutoCompleteRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE ENSLAVED PEOPLE BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Enslaved.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=False
		)
		
		#RUN THE AUTOCOMPLETE ALGORITHM
		final_vals=autocomplete_req(queryset,request)
		resp=dict(request.data)
		resp['suggested_values']=final_vals
		
		#VALIDATE THE RESPONSE
		serialized_resp=EnslavedAutoCompleteResponseSerializer(data=resp)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

class EnslaverCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, enslaver identities). It also accepts filters. This means that you can apply any filter you would to any other query, for instance, the enslavers list view, in the process of requesting your autocomplete suggestions, thereby rapidly narrowing your search.",
		request=EnslaverAutoCompleteRequestSerializer,
		responses=EnslaverAutoCompleteResponseSerializer,
	)	
	def post(self,request):
		st=time.time()
		print("ENSLAVER CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = EnslaverAutoCompleteRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=EnslaverIdentity.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=False
		)
		
		#RUN THE AUTOCOMPLETE ALGORITHM
		final_vals=autocomplete_req(queryset,request)
		resp=dict(request.data)
		resp['suggested_values']=final_vals
		
		#VALIDATE THE RESPONSE
		serialized_resp=EnslaverAutoCompleteResponseSerializer(data=resp)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

class EnslaverList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint returns a list of highly nested objects, each of which contains all the available information on named individuals we know to have participated in the slave trade.\
		This people-oriented data dramatically changes the nature of our dataset. While Voyages data has always been relational, the complexity of interpersonal connections in this dataset makes it graph-like and pushes the boundaries of the underlying system (Python Django).\
		Before 2022, the project had only recorded ship captains and ship owners. We now have a much more robust accounting of individuals, sometimes recorded under different names, participating in multiple voyages, and operating in a range of different roles, from investors to brokers to buyers and sellers of enslaved people. In some cases, we know the names of these enslavers' spouses, and the amounts of money they willed to their descendants upon their death. We are very much looking forward to linking this network of enslavers into other public datasets such as Stanford's Kindred network in order to map the economic legacy of these ill-gotten gains\
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.",
		request=EnslaverListRequestSerializer,
		responses=EnslaverListResponseSerializer
	)
	def post(self,request):
		st=time.time()
		print("ENSLAVER LIST+++++++\nusername:",request.auth.user)

		#VALIDATE THE REQUEST
		serialized_req = EnslaverListRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE ENSLAVERS BASED ON THE REQUEST'S FILTER OBJECT
		queryset=EnslaverIdentity.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=True
		)

		results,total_results_count,page_num,page_size=paginate_queryset(queryset,request)
		resp=EnslaverListResponseSerializer({
			'count':total_results_count,
			'page':page_num,
			'page_size':page_size,
			'results':results
		}).data
		#I'm having the most difficult time in the world validating this nested paginated response
		#And I cannot quite figure out how to just use the built-in paginator without moving to urlparams
		return JsonResponse(resp,safe=False,status=200)

class EnslavedAggregations(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The aggregations endpoints helps us to peek at numerical fields in the same way that autcomplete endpoints help us to get a sense of what the available text values are on a field.\
		So if we want to, for instance, allow a user to search on voyages by year, we might want to give them a rangeslider component. In order to make that rangeslider component, you'd have to know the minimum and maximum years during which voyages sailed -- you would also need to know, of course, whether you were searching for the minimum and maximum of years of departure, embarkation, disembarkation, return, etc.\
		Also, as with the other new endpoints we are rolling out in January 2024, you can run a filter before you query for min/max on variables. So if you've already searched for voyages arriving in Cuba, for instance, you can ask for the min and max years of disembarkation in order to make a rangeslider dynamically tailored to that search.\
		Note to maintainer(s): This endpoint was made with rangesliders in mind, so we are only exposing min & max for now. In the future, it could be very useful to have median, mean, or plug into the stats engine for a line or bar chart to create some highly interactive filtering.\
		",
		request=EnslavedFieldAggregationRequestSerializer,
		responses=EnslavedFieldAggregationResponseSerializer
	)
	def post(self,request):
		st=time.time()
		print("ENSLAVED AGGREGATIONS+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = EnslavedFieldAggregationRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Enslaved.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaved_options,
			auto_prefetch=False
		)
		
		#RUN THE AGGREGATIONS
		aggregation_field=request.data.get('varName')
		output_dict,errormessages=get_fieldstats(queryset,aggregation_field,Enslaved_options)
		print(output_dict)
		#VALIDATE THE RESPONSE
		serialized_resp=EnslavedFieldAggregationResponseSerializer(data=output_dict)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

class EnslaverAggregations(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The aggregations endpoints helps us to peek at numerical fields in the same way that autcomplete endpoints help us to get a sense of what the available text values are on a field.\
		So if we want to, for instance, allow a user to search enslavers by the year that the voyages they were associated with operated, then we might want to give them a rangeslider component. In order to make that rangeslider component, you'd have to know the minimum and maximum years during which voyages sailed -- you would also need to know, of course, whether you were searching for the minimum and maximum of years of departure, embarkation, disembarkation, return, etc.\
		Also, as with the other new endpoints we are rolling out in January 2024, you can run a filter before you query for min/max on variables. So if you've already searched for enslavers associated with voyages arriving in Cuba, for instance, you can ask for the min and max years of disembarkation in order to make a rangeslider dynamically tailored to that search.\
		Note to maintainer(s): This endpoint was made with rangesliders in mind, so we are only exposing min & max for now. In the future, it could be very useful to have median, mean, or plug into the stats engine for a line or bar chart to create some highly interactive filtering.\
		",
		request=EnslaverFieldAggregationRequestSerializer,
		responses=EnslaverFieldAggregationResponseSerializer
	)
	def post(self,request):
		st=time.time()
		print("ENSLAVER AGGREGATIONS+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		print(request.data)
# 		serialized_req = EnslaverFieldAggregationRequestSerializer(data=request.data)
# 		if not serialized_req.is_valid():
# 			return JsonResponse(serialized_req.errors,status=400)

		#FILTER THE VOYAGES BASED ON THE REQUEST'S FILTER OBJECT
		queryset=EnslaverIdentity.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=False
		)
		
		#RUN THE AGGREGATIONS
		aggregation_field=request.data.get('varName')
		output_dict,errormessages=get_fieldstats(queryset,aggregation_field,Enslaver_options)
		
		print(output_dict)
		#VALIDATE THE RESPONSE
		serialized_resp=EnslaverFieldAggregationResponseSerializer(data=output_dict)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		if not serialized_resp.is_valid():
			return JsonResponse(serialized_resp.errors,status=400)
		else:
			return JsonResponse(serialized_resp.data,safe=False)

class EnslavedDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The dataframes endpoint is mostly for internal use -- building up caches of data in the flask services.\n\
		However, it could be used for csv exports and the like.\n\
		Be careful! It's a resource hog. But more importantly, if you request fields that are not one-to-one relationships with the voyage, you're likely get back extra rows.\n\
		And finally, the example provided below puts a strict year filter on because unrestricted, it will break your swagger viewer :) \n\
		",
		request=EnslavedDataframesRequestSerializer
	)
	def post(self,request):
		print("ENSLAVED DATA FRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		
		print(request.data)
		#VALIDATE THE REQUEST
		serialized_req = EnslavedDataframesRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE ENSLAVED PEOPLE BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Enslaved.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaved_options,
			auto_prefetch=True
		)
		
		queryset=queryset.order_by('id')
		sf=request.data.get('selected_fields')
		output_dicts={}
		vals=list(eval('queryset.values_list("'+'","'.join(sf)+'")'))
		for i in range(len(sf)):
			output_dicts[sf[i]]=[v[i] for v in vals]
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		## DIFFICULT TO VALIDATE THIS WITH A SERIALIZER -- NUMBER OF KEYS AND DATATYPES WITHIN THEM CHANGES DYNAMICALLY ACCORDING TO REQ
		
		return JsonResponse(output_dicts,safe=False)

class EnslaverDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="The dataframes endpoint is mostly for internal use -- building up caches of data in the flask services.\n\
		However, it could be used for csv exports and the like.\n\
		Be careful! It's a resource hog. But more importantly, if you request fields that are not one-to-one relationships with the voyage, you're likely get back extra rows.\n\
		And finally, the example provided below puts a strict year filter on because unrestricted, it will break your swagger viewer :) \n\
		",
		request=EnslaverDataframesRequestSerializer
	)
	def post(self,request):
		print("ENSLAVER DATA FRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		
		print(request.data)
		#VALIDATE THE REQUEST
		serialized_req = EnslaverDataframesRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#FILTER THE ENSLAVERS BASED ON THE REQUEST'S FILTER OBJECT
		queryset=EnslaverIdentity.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=True
		)
		
		queryset=queryset.order_by('id')
		sf=request.data.get('selected_fields')
		output_dicts={}
		vals=list(eval('queryset.values_list("'+'","'.join(sf)+'")'))
		for i in range(len(sf)):
			output_dicts[sf[i]]=[v[i] for v in vals]
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		## DIFFICULT TO VALIDATE THIS WITH A SERIALIZER -- NUMBER OF KEYS AND DATATYPES WITHIN THEM CHANGES DYNAMICALLY ACCORDING TO REQ
		
		return JsonResponse(output_dicts,safe=False)

@extend_schema(exclude=True)
class EnslavementRelationsDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.data)
		queryset=EnslavementRelation.objects.all()
		enslavementrelationoptions={
			'id':{'type':'integer'},
			'voyage__voyage_id':{'type':'integer'},
			'voyage__id':{'type':'integer'},
			'relation_type__name':{'type':'string'},
			'voyage__voyage_ship__ship_name':{'type':'string'},
			'voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__name':{'type':'string'},
			'voyage__voyage_itinerary__imp_principal_port_slave_dis__name':{'type':'string'},
			'voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year':{'type':'integer'},
			'enslaved_in_relation__enslaved__id':{'type':'integer'},
			'enslaved_in_relation__enslaved__documented_name':{'type':'string'},
			'enslaved_in_relation__enslaved__age':{'type':'integer'},
			'enslaved_in_relation__enslaved__gender':{'type':'string'},
			'relation_enslavers__enslaver_alias__identity__id':{'type':'integer'},
			'relation_enslavers__enslaver_alias__identity__principal_alias':{'type':'string'},
			'relation_enslavers__roles__name':{'type':'string'}
		}
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			enslavementrelationoptions,
			auto_prefetch=True
		)
		queryset=queryset.order_by('id')
		selected_fields=request.data.get('selected_fields')
		output_dicts={}
		vals=list(eval('queryset.values_list("'+'","'.join(selected_fields)+'")'))
		for i in range(len(selected_fields)):
			output_dicts[selected_fields[i]]=[v[i] for v in vals]
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(output_dicts,safe=False)
		
class EnslaverGeoTreeFilter(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint is tricky. In addition to taking a filter object, it also takes a list of geographic value variable names, like 'aliases__enslaver_relations__relation__voyage__voyage_itinerary__port_of_departure__value'. \n\
		What it returns is a hierarchical tree of SlaveVoyages geographic data, filtered down to only the values used in those 'geotree valuefields' after applying the filter object.\n\
		So if you were to ask for aliases__enslaver_relations__relation__voyage__voyage_itinerary__port_of_departure__value, you would mostly get locations in Europe and the Americas; and if you searched 'aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__name', you would principally get places in the Americas and Africa.",
		request=EnslaverGeoTreeFilterRequestSerializer,
		responses=LocationSerializerDeep
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE GEO TREE FILTER+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = EnslaverGeoTreeFilterRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#extract and then peel out the geotree_valuefields
		reqdict=dict(request.data)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		
		#FILTER THE ENSLAVERS BASED ON THE REQUEST'S FILTER OBJECT
		queryset=EnslaverIdentity.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			reqdict,
			Enslaver_options
		)
		
		#THEN GET THE CORRESPONDING GEO VALUES ON THAT FIELD
		for geotree_valuefield in geotree_valuefields:
			geotree_valuefield_stub='__'.join(geotree_valuefield.split('__')[:-1])
			queryset=queryset.select_related(geotree_valuefield_stub)
		vls=[]
		for geotree_valuefield in geotree_valuefields:		
			vls+=[i[0] for i in list(set(queryset.values_list(geotree_valuefield))) if i[0] is not None]
		vls=list(set(vls))
		
		#THEN GET THE GEO OBJECTS BASED ON THAT OPERATION
		filtered_geotree=GeoTreeFilter(spss_vals=vls)
		
		### CAN'T FIGURE OUT HOW TO SERIALIZE THIS...
		
		resp=JsonResponse(filtered_geotree,safe=False)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return resp

class EnslavedGeoTreeFilter(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	@extend_schema(
		description="This endpoint is tricky. In addition to taking a filter object, it also takes a list of geographic value variable names, like 'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__value'. \n\
		What it returns is a hierarchical tree of SlaveVoyages geographic data, filtered down to only the values used in those 'geotree valuefields' after applying the filter object.\n\
		So if you were to ask for enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__value, you would mostly get locations in Europe and the Americas; and if you searched 'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__name', you would principally get places in the Americas and Africa.",
		request=EnslavedGeoTreeFilterRequestSerializer,
		responses=LocationSerializerDeep
	)
	def post(self,request):
		st=time.time()
		print("VOYAGE GEO TREE FILTER+++++++\nusername:",request.auth.user)
		
		#VALIDATE THE REQUEST
		serialized_req = EnslavedGeoTreeFilterRequestSerializer(data=request.data)
		if not serialized_req.is_valid():
			return JsonResponse(serialized_req.errors,status=400)
		
		#extract and then peel out the geotree_valuefields
		reqdict=dict(request.data)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		
		#FILTER THE ENSLAVED PEOPLE BASED ON THE REQUEST'S FILTER OBJECT
		queryset=Enslaved.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			reqdict,
			Enslaved_options
		)
		
		#THEN GET THE CORRESPONDING GEO VALUES ON THAT FIELD
		for geotree_valuefield in geotree_valuefields:
			geotree_valuefield_stub='__'.join(geotree_valuefield.split('__')[:-1])
			queryset=queryset.select_related(geotree_valuefield_stub)
		vls=[]
		for geotree_valuefield in geotree_valuefields:		
			vls+=[i[0] for i in list(set(queryset.values_list(geotree_valuefield))) if i[0] is not None]
		vls=list(set(vls))
		
		#THEN GET THE GEO OBJECTS BASED ON THAT OPERATION
		filtered_geotree=GeoTreeFilter(spss_vals=vls)
		
		### CAN'T FIGURE OUT HOW TO SERIALIZE THIS...
		
		resp=JsonResponse(filtered_geotree,safe=False)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return resp

@extend_schema(exclude=True)
class EnslavedAggRoutes(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("ENSLAVED AGGREGATION ROUTES+++++++\nusername:",request.auth.user)
		params=dict(request.data)
		zoom_level=params.get('zoom_level')
		queryset=Enslaved.objects.all()
		queryset,results_count=post_req(
			queryset,
			self,
			request,
			Enslaved_options,
			auto_prefetch=True
		)
# 		queryset=queryset.filter(enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__name='Mozambique')
		print("--->",queryset.count())
		queryset=queryset.order_by('id')
		zoomlevel=params.get('zoomlevel',['region'])[0]
		values_list=queryset.values_list('id')
		pks=[v[0] for v in values_list]
		django_query_time=time.time()
		print("Internal Django Response Time:",django_query_time-st,"\n+++++++")
		u2=GEO_NETWORKS_BASE_URL+'network_maps/'
		d2={
			'graphname':zoomlevel,
			'cachename':'ao_maps',
			'pks':pks
		}
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		j=json.loads(r.text)
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(j,safe=False)


@extend_schema(exclude=True)
class PASTNetworks(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("PAST NETWORKS+++++++\nusername:",request.auth.user)
		params=json.dumps(dict(request.data))
		print(PEOPLE_NETWORKS_BASE_URL)
		r=requests.post(PEOPLE_NETWORKS_BASE_URL,data=params,headers={"Content-type":"application/json"})
		j=json.loads(r.text)
		return JsonResponse(j,safe=False)


#CONTRIBUTIONS

@extend_schema(
		exclude=True
	)
class EnslavementRelationCREATE(generics.CreateAPIView):
	'''
	Create an enslavement relation without a pk
	'''
	queryset=EnslavementRelation.objects.all()
	serializer_class=EnslavementRelationCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

class EnslavementRelationRETRIEVE(generics.RetrieveAPIView):
	'''
	Retrieve an enslavement relation record with their pk
	'''
	queryset=EnslavementRelation.objects.all()
	serializer_class=EnslavementRelationPKSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

@extend_schema(
		exclude=True
	)
class EnslavementRelationUPDATE(generics.UpdateAPIView):
	'''
	Update an enslavement relation record with their pk
	'''
	queryset=EnslavementRelation.objects.all()
	serializer_class=EnslavementRelationCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class EnslavementRelationDESTROY(generics.DestroyAPIView):
	'''
	Delete an enslavement relation record with their pk
	'''
	queryset=EnslavementRelation.objects.all()
	serializer_class=EnslavementRelationCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class EnslaverCREATE(generics.CreateAPIView):
	'''
	Create enslaver without a pk
	'''
	queryset=EnslaverIdentity.objects.all()
	serializer_class=EnslaverCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

class EnslaverRETRIEVE(generics.RetrieveAPIView):
	'''
	Retrieve an enslaver record with their pk
	'''
	queryset=EnslaverIdentity.objects.all()
	serializer_class=EnslaverPKSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

@extend_schema(
		exclude=True
	)
class EnslaverUPDATE(generics.UpdateAPIView):
	'''
	Update an enslaver record with their pk
	'''
	queryset=EnslaverIdentity.objects.all()
	serializer_class=EnslaverCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class EnslaverDESTROY(generics.DestroyAPIView):
	'''
	Delete an enslaver record with their pk
	'''
	queryset=EnslaverIdentity.objects.all()
	serializer_class=EnslaverCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class EnslavedCREATE(generics.CreateAPIView):
	'''
	Create enslaver without a pk
	'''
	queryset=Enslaved.objects.all()
	serializer_class=EnslavedCRUDSerializer
	lookup_field='id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

class EnslavedRETRIEVE(generics.RetrieveAPIView):
	'''
	Retrieve an enslaver record with their pk
	'''
	queryset=Enslaved.objects.all()
	serializer_class=EnslavedPKSerializer
	lookup_field='enslaved_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]

@extend_schema(
		exclude=True
	)
class EnslavedUPDATE(generics.UpdateAPIView):
	'''
	Update an enslaver record with their pk
	'''
	queryset=Enslaved.objects.all()
	serializer_class=EnslavedCRUDSerializer
	lookup_field='enslaved_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]

@extend_schema(
		exclude=True
	)
class EnslavedDESTROY(generics.DestroyAPIView):
	'''
	Delete an enslaver record with their pk
	'''
	queryset=Enslaved.objects.all()
	serializer_class=EnslavedCRUDSerializer
	lookup_field='enslaved_id'
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAdminUser]


