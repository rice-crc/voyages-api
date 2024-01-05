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
from geo.serializers_READONLY import LocationSerializer
from voyages3.localsettings import *
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from common.static.Enslaver_options import Enslaver_options
from common.static.Enslaved_options import Enslaved_options
from common.serializers import autocompleterequestserializer, autocompleteresponseserializer


class EnslavedList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=EnslavedSerializer
	def post(self,request):
		'''
		This endpoint returns a list of highly nested objects, each of which contains all the available information on enslaved individuals who we know to have been transported on a voyage.
		
		This people-oriented data dramatically changes the nature of our dataset. While Voyages data has always been relational, the complexity of interpersonal connections in this dataset makes it graph-like and pushes the boundaries of the underlying system (Python Django).
		
		For instance, you might search for a person who was bought, sold, or transported on a voyage owned by a known enslaver. Or, you might search for people who, based on the sound of their name as recorded, are believed to have come from a particular region in Africa where an ethnic group known to use that name was located.
		
		However, it must be stressed that there is a tension in this dataset: the data that we have on enslaved individuals was almost entirely recorded by the people who enslaved them, or by colonial managers who technically liberated them, but oftentimes pressed these people into military service or labor. We know the names of these people, which is grounbreaking for this project because it allows us to identify named individuals in a dataset that often records only nameless quantities of people, but as you analyze this dataset you will note that most of the data we have on these enslaved people is bio-data, such as gender, age, height, and skin color -- this is qualitatively different than the data we have on the enslavers, about whom we often have a good deal of biographical data.
		
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.
		'''
		st=time.time()
		print("ENSLAVED LIST+++++++\nusername:",request.auth.user)
		queryset=Enslaved.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Enslaved_options,
			auto_prefetch=True
		)
		paginated_queryset=paginate_queryset(queryset,request)
		if len(error_messages)==0:
			headers={"total_results_count":results_count}
			read_serializer=EnslavedSerializer(paginated_queryset,many=True)
			serialized=read_serializer.data
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(serialized,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)


class EnslavedCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	queryset=Enslaved.objects.all()
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, the voyage). It also accepts filters. This means that you can apply any filter you would to any other query, for instance, the voyages list view, in the process of requesting your autocomplete suggestions, thereby rapidly narrowing your search.",
		request=autocompleterequestserializer,
		responses=autocompleteresponseserializer,
		examples = [
			OpenApiExample(
				'Autocomplete on any enslaved-related field',
				summary='Autocomplete for names like bo',
				description='Here, we search for enslaved peoples names that are like "bo". From the offset and limit values, you can see that we are requesting the first 20 entries.',
				value={
					"varname":"documented_name",
					"querystr":"bo",
					"offset":0,
					"limit":20,
					"filter":{}
				},
				request_only=True,
				response_only=False
			),
			OpenApiExample(
				'Suggested values are returned',
				summary='Autocomplete for names like "bo"',
				description='Here, we see the first 20 entries like "bo" in our list of enslaved peoples names',
				value={
					"varname": "documented_name",
					"querystr": "bo",
					"offset": 0,
					"limit": 20,
					"filter": {},
					"suggested_values": [{"value": "?, Bob"},{"value": "?, Claborne"},{"value": "?, Claiborne"},{"value": "??bon"},{"value": "?ill, Bob"},{"value": "?way, Bob"},{"value": "A Bossuh"},{"value": "A. Bossou"},{"value": "Abalobo"},{"value": "Abamboh"},{"value": "Abanaboo"},{"value": "Abaraboo"},{"value": "Abbaboo"},{"value": "Abbeeboo"},{"value": "Abbo"},{"value": "Abbobocah"},{"value": "Abboboday"},{"value": "Abbochay"},{"value": "Abbodoo"},{"value": "Abboe"}]},
				request_only=False,
				response_only=True
			)
		]
	)
	def post(self,request):
		st=time.time()
		queryset=Enslaved.objects.all()
		print("ENSLAVED CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		options=Enslaved_options
		
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
				auto_prefetch=False
			)
			final_vals=autocomplete_req(queryset,varname,querystr,offset,max_offset,limit)
		
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		resp=dict(rdata)
		resp['suggested_values']=final_vals
		
		read_serializer=autocompleteresponseserializer(resp)
		serialized=read_serializer.data
		
		print(' | '.join(error_messages))
		
		return JsonResponse(serialized,safe=False)

class EnslaverCharFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	queryset=Enslaved.objects.all()
	@extend_schema(
		description="The autocomplete endpoints provide paginated lists of values on fields related to the endpoints primary entity (here, the voyage). It also accepts filters. This means that you can apply any filter you would to any other query, for instance, the enslavers list view, in the process of requesting your autocomplete suggestions, thereby rapidly narrowing your search.",
		request=autocompleterequestserializer,
		responses=autocompleteresponseserializer,
		examples = [
			OpenApiExample(
				'Autocomplete on any enslavers-related field',
				summary='Autocomplete for enslaved names related to enslavers',
				description='Here, we search for the names of enslaved people that are like "sal" IN RELATION TO the enslavers. From the offset and limit values, you can see that we are requesting the first 20 entries.',
				value={
					"varname":"aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__documented_name",
					"querystr":"sal",
					"offset":0,
					"limit":20,
					"filter":{}
				},
				request_only=True,
				response_only=False
			),
			OpenApiExample(
				'Suggested values are returned',
				summary='Autocomplete for enslaved names related to enslavers',
				description='Here, we see the first 20 names like "sal" for enslaved people through the enslaver model.',
				value={
					"varname": "aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__documented_name",
					"querystr": "sal",
					"offset": 0,
					"limit": 20,
					"filter": {},
					"suggested_values": [{"value": "? (Sally's), child"},{"value": "?, Sally"},{"value": "?field, Sally"},{"value": "Abissala"},{"value": "Abissalah"},{"value": "Absalon"},{"value": "Achasaloh"},{"value": "Adesalar"},{"value": "Adosalah"},{"value": "Afosalah"},{"value": "Ahdaisaloo"},{"value": "Ahdasalee"},{"value": "Ahlarsalah"},{"value": "Ahmesallah"},{"value": "Ahsalah"},{"value": "Ahsalla"},{"value": "Ahsally"},{"value": "Ahsaloe"},{"value": "Alasalhee"},{"value": "Alasallagee"}]
				},
				request_only=False,
				response_only=True
			)
		]
	)
	def post(self,request):
		st=time.time()
		queryset=EnslaverIdentity.objects.all()
		print("ENSLAVER CHAR FIELD AUTOCOMPLETE+++++++\nusername:",request.auth.user)
		
		options=Enslaver_options
		
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
				auto_prefetch=False
			)
			final_vals=autocomplete_req(queryset,varname,querystr,offset,max_offset,limit)
		
		print("Internal Response Time:",time.time()-st,"\n+++++++")
		
		resp=dict(rdata)
		resp['suggested_values']=final_vals
		
		read_serializer=autocompleteresponseserializer(resp)
		serialized=read_serializer.data
		
		return JsonResponse(serialized,safe=False)


#LONG-FORM TABULAR ENDPOINT
class EnslaverList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=EnslaverSerializer
	def post(self,request):
		'''
		This endpoint returns a list of highly nested objects, each of which contains all the available information on named individuals we know to have participated in the slave trade.
		
		This people-oriented data dramatically changes the nature of our dataset. While Voyages data has always been relational, the complexity of interpersonal connections in this dataset makes it graph-like and pushes the boundaries of the underlying system (Python Django).
		
		Before 2022, the project had only recorded ship captains and ship owners. We now have a much more robust accounting of individuals, sometimes recorded under different names, participating in multiple voyages, and operating in a range of different roles, from investors to brokers to buyers and sellers of enslaved people. In some cases, we know the names of these enslavers' spouses, and the amounts of money they willed to their descendants upon their death. We are very much looking forward to linking this network of enslavers into other public datasets such as Stanford's Kindred network in order to map the economic legacy of these ill-gotten gains.
		
		You can filter on any field by 1) using double-underscore notation to concatenate nested field names and 2) conforming your filter to request parser rules for numeric, short text, global search, and geographic types.
		'''

		print("ENSLAVER LIST+++++++\nusername:",request.auth.user)
		st=time.time()
		queryset=EnslaverIdentity.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=True
		)
		paginated_queryset=paginate_queryset(queryset,request)
		if len(error_messages)==0:
			headers={"total_results_count":results_count}
			read_serializer=EnslaverSerializer(paginated_queryset,many=True)
			serialized=read_serializer.data
			outputs=[]
			outputs=serialized
			## now let's add some flattened enslavement relations
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(outputs,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)



# Basic statistics
## takes a numeric variable
## returns its sum, average, max, min, and stdv@extend_schema(exclude=True)
@extend_schema(exclude=True)
class EnslavedAggregations(generics.GenericAPIView):
# 	serializer_class=EnslavedSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		try:
			st=time.time()
			print("ENSLAVED AGGREGATIONS+++++++\nusername:",request.auth.user)
			params=dict(request.data)
			aggregations=params.get('aggregate_fields')
			print(aggregations)
			queryset=Enslaved.objects.all()
			aggregation,selected_fields,results_count,error_messages=post_req(
				queryset,
				self,
				request,
				Enslaved_options
			)
			output_dict={}
			if len(error_messages)==0:
				for a in aggregation:
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
				print("failed\n+++++++")
				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
		except:
			return JsonResponse({'status':'false','message':'bad request'}, status=400)


# # Basic statistics
# ## takes a numeric variable
# ## returns its sum, average, max, min, and stdv@extend_schema(exclude=True)
@extend_schema(exclude=True)
class EnslaverAggregations(generics.GenericAPIView):
# 	serializer_class=EnslaverSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("ENSLAVER AGGREGATIONS+++++++\nusername:",request.auth.user)
		try:
			params=dict(request.data)
			aggregations=params.get('aggregate_fields')
			queryset=EnslaverIdentity.objects.all()
			aggregation,selected_fields,results_count,error_messages=post_req(
				queryset,
				self,
				request,
				Enslaver_options
			)
			output_dict={}
			if len(error_messages)==0:
				for a in aggregation:
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
				print("failed\n+++++++")
				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
		except:
			return JsonResponse({'status':'false','message':'bad request'}, status=400)
			
@extend_schema(exclude=True)
class EnslavedDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("ENSLAVED DATA FRAMES+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.data)
		queryset=Enslaved.objects.all()
# 		queryset=queryset.filter(enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__name='Mozambique')
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Enslaved_options,
			auto_prefetch=True
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
@extend_schema(exclude=True)
class EnslaverDataFrames(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.data)
		queryset=EnslaverIdentity.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			Enslaver_options,
			auto_prefetch=True
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
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			enslavementrelationoptions,
			auto_prefetch=True
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

@extend_schema(exclude=True)
class EnslaverGeoTreeFilter(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("ENSLAVER GEO TREE FILTER+++++++\nusername:",request.auth.user)
		st=time.time()
		reqdict=dict(request.data)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		queryset=EnslaverIdentity.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			reqdict,
			Enslaver_options
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

@extend_schema(exclude=True)
class EnslavedGeoTreeFilter(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("ENSLAVED GEO TREE FILTER+++++++\nusername:",request.auth.user)
		st=time.time()
		reqdict=dict(request.data)
		geotree_valuefields=reqdict['geotree_valuefields']
		del(reqdict['geotree_valuefields'])
		queryset=Enslaved.objects.all()
		queryset,selected_fields,results_count,error_messages=post_req(
			queryset,
			self,
			reqdict,
			Enslaved_options
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
		queryset,selected_fields,results_count,error_messages=post_req(
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


