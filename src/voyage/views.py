from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
import urllib
import json
import requests
import time
from .models import *
import pprint
from tools.nest import *
from tools.reqs import *
from tools.timer import timer
import collections
import gc
from .serializers import *
from voyages2021.localsettings import *

pp = pprint.PrettyPrinter(indent=4)


voyage_options=options_handler('voyage/voyage_options.json',hierarchical=False)
geo_options=options_handler('voyage/geo_options.json',hierarchical=False)


from django import http


class CorsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (request.method == "OPTIONS"  and "HTTP_ACCESS_CONTROL_REQUEST_METHOD" in request.META):
            response = http.HttpResponse()
            response["Content-Length"] = "0"
            response["Access-Control-Max-Age"] = 86400
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "DELETE, GET, OPTIONS, PATCH, POST, PUT"
        response["Access-Control-Allow-Headers"] = "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with"
        return response


#LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
##HAVE NOT YET BUILT IN ORDER-BY FUNCTIONALITY
class VoyageList(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		t=timer('FETCHING...',[])
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			#read_serializer=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
			t=timer('building query',t)
			read_serializer=VoyageSerializer(queryset,many=True)
			t=timer('sql execution',t)
			serialized=read_serializer.data
			t=timer('serializing',t)

			#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
			if selected_fields==[]:
				selected_fields=list(voyage_options.keys())
			else:
				selected_fields=[i for i in selected_fields if i in list(voyage_options.keys())]
			
			outputs=[]
		
			hierarchical=request.POST.get('hierarchical')
			if str(hierarchical).lower() in ['false','0','f','n']:
				hierarchical=False
			else:
				hierarchical=True
		
			if hierarchical==False:
				for s in serialized:
					d={}
					for selected_field in selected_fields:
						#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
						#not badly -- you just get some repeat, nested data -- but that's unhelpful
						#The fix will be to make it a through table relationship
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			else:
				outputs=serialized
			t=timer('flattening',t,done=True)
			print("^^^----VOYAGES POST----^^^")
			return JsonResponse(outputs,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
			print("^^^----VOYAGES POST----^^^")


class SingleVoyage(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	def get(self,request,voyage_id):
		thisvoyage=Voyage.objects.get(pk=voyage_id)
		serialized=VoyageSerializer(thisvoyage,many=False).data
		return JsonResponse(serialized,safe=False)

class SingleVoyageVar(generics.GenericAPIView):
	def get(self,request,voyage_id,varname):
		thisvoyage=Voyage.objects.get(pk=voyage_id)
		serialized=VoyageSerializer(thisvoyage,many=False).data
		keychain=varname.split('__')
		bottomval=bottomout(serialized,list(keychain))
		var_options=voyage_options[varname]
		output={
			'voyage_id':voyage_id,
			'variable_api_name':varname,
			'variable_label':var_options['flatlabel'],
			'variable_type':var_options['type'],
			'value':bottomval
		}
		return JsonResponse(output,safe=False)

# Basic statistics
## takes a numeric variable
## returns its sum, average, max, min, and stdv
class VoyageAggregations(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		#print("username:",request.auth.user)
		params=dict(request.POST)
		aggregations=params.get('aggregate_fields')
		print("aggregations:",aggregations)
		queryset=Voyage.objects.all()
		
		aggregation,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		output_dict={}
		if len(error_messages)==0 and type(aggregation)==list:
			for a in aggregation:
				for k in a:
					v=a[k]
					fn=k.split('__')[-1]
					varname=k[:-len(fn)-2]
					if varname in output_dict:
						output_dict[varname][fn]=a[k]
					else:
						output_dict[varname]={fn:a[k]}
			return JsonResponse(output_dict,safe=False)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

#Django really did not like running pandas inside of itself
#Maybe I'm wrong and there's a way to do it
#But in the meantime, we're going to use Flask as a pandas sidecar for complex statistical operations
#Currently running on port 5000. just hardcoding this for dev w docker-compose, obviously needs to be changed for production
##It's fast as hell :)
#data={
#    'voyage_itinerary__imp_principal_region_slave_dis__region':[
#        'Barbados',
#        'Jamaica'
#    ],
#    'groupby_fields':['voyage_itinerary__principal_port_of_slave_dis__place','voyage_itinerary__imp_principal_place_of_slave_purchase__place'],
#    'value_field_tuple':['voyage_slaves_numbers__imp_total_num_slaves_disembarked','sum']
#}
#r=requests.post(url='http://127.0.0.1:8000/voyage/groupby',headers=headers,data=data)
#j=json.loads(r.text)

class VoyageGroupBy(generics.GenericAPIView):
	'''
	Think of this as a pivot table (but it will generalize later)
	This view takes:
		a groupby tuple (row, col)
		a value field tuple (cellvalue,aggregationfunction)
		any search parameters you want!
	'''
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		params=dict(request.POST)
		groupby_fields=params.get('groupby_fields')
		value_field_tuple=params.get('value_field_tuple')
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			u2=FLASK_BASE_URL+'groupby/'
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			if r.ok:
				return JsonResponse(json.loads(r.text),safe=False)
			else:
				return JsonResponse({'status':'false','message':'bad groupby request'}, status=400)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)


class VoyageCaches(generics.GenericAPIView):
	'''
	This view takes:
		All the search arguments you can pass to dataframes or voyage list endpoints
		A specified "cachename" argument -- currently valid values are:
			"voyage_export" --> for csv exports -- cached 67 variables
			"voyage_animation" --> for the timelapse animation -- cached 11 variables
			"voyage_maps" --> for aggregating some geo & numbers vars
			"voyage_pivot_tables"
			"voyage_summary_statistics"
			"voyage_xyscatter"
		And returns a dataframes-style response -- a dictionary with:
			keys are fully-qualified var names
			values are equal-length arrays, each corresponding to a single entity
				(use voyage_id or id column as your index if you're going to load it into pandas)
		List view is highly inefficient because of the repetitive var names for each voyage
	'''
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		params=dict(request.POST)
		u2=FLASK_BASE_URL + 'dataframes/'
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		voyageobjects=Voyage.objects
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(voyageobjects,self,request,voyage_options,retrieve_all=retrieve_all)
		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			if r.ok:
				return JsonResponse(json.loads(r.text),safe=False,headers={'results_count':results_count})
			else:
				return JsonResponse({'status':'false','message':'bad request to cache'}, status=400)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

#DATAFRAME ENDPOINT (experimental & a resource hog!)
class VoyageDataFrames(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		t=timer("FETCHING...",[])
		params=dict(request.POST)
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,auto_prefetch=False,retrieve_all=retrieve_all)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			if selected_fields==[]:
				sf=list(voyage_options.keys())
			else:
				sf=[i for i in selected_fields if i in list(voyage_options.keys())]
			
			t=timer('building query',t)
			serialized=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
			t=timer('sql execution',t)
			serialized=serialized.data
			t=timer('serialization',t)
			output_dicts={}
			for selected_field in sf:
				keychain=selected_field.split('__')
				for s in serialized:
					bottomval=bottomout(s,list(keychain))
					if selected_field in output_dicts:
						output_dicts[selected_field].append(bottomval)
					else:
						output_dicts[selected_field]=[bottomval]
			t=timer('flattening',t,done=True)
			return JsonResponse(output_dicts,safe=False,headers=headers)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)



#Get data on Places
#Default structure is places::region::broad_region
#By passing it the req param 'inverse=True', you'll get back broad_regions::regions::places
class VoyagePlaceList(generics.GenericAPIView):
	serializer_class=PlaceSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/geo_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		#print("username:",request.auth.user)
		t=timer("FETCHING...",[])
		queryset=Place.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,geo_options,retrieve_all=True)
		if len(error_messages)==0:
			t=timer('building query',t)
			read_serializer=PlaceSerializer(queryset,many=True)
			t=timer('sql execution',t)
			serialized=read_serializer.data
			t=timer('serialization',t)
			params=request.GET
			tree={}
		
			hierarchical=request.POST.get('hierarchical')
			if str(hierarchical).lower() in ['false','0','f','n']:
				hierarchical=False
			else:
				hierarchical=True
		
			if hierarchical:
				for place in serialized:
					broadregion_id=place['region']['broad_region']['id']
					region_id=place['region']['id']
					place_id=place['id']
					minimal_place_dict=dict(place)
					del(minimal_place_dict['region'])
					minimal_region_dict=dict(place['region'])
					del(minimal_region_dict['broad_region'])
					if broadregion_id not in tree:
						tree[broadregion_id]=place['region']['broad_region']
						tree[broadregion_id]['regions']={region_id:minimal_region_dict}
						tree[broadregion_id]['regions'][region_id]['places']={place_id:minimal_place_dict}
					else:
						if region_id not in tree[broadregion_id]['regions']:
							tree[broadregion_id]['regions'][region_id]=minimal_region_dict
							tree[broadregion_id]['regions'][region_id]['places']={place_id:minimal_place_dict}
						else:
							tree[broadregion_id]['regions'][region_id]['places'][place_id]=minimal_place_dict
				tree_list=[]
				for broadregion_id in tree:
					item=dict(tree[broadregion_id])
					item['regions']=[]
					for region_id in tree[broadregion_id]['regions']:
						region=dict(tree[broadregion_id]['regions'][region_id])
						places=[]
						for place_id in region['places']:
							places.append(region['places'][place_id])
						region['places']=places
						item['regions'].append(region)
					tree_list.append(item)						
				outputs=tree_list
			else:
				#if the user hasn't selected any fields (default), then get the fully-qualified var names as the full list
				if selected_fields==[]:
					sf=list(geo_options.keys())
				else:
					sf=[i for i in selected_fields if i in list(geo_options.keys())]
				outputs=[]
				for s in serialized:
					d={}
					for selected_field in sf:
						#In this flattened view, the reverse relationship breaks the references to the outcome variables in the serializer
						#not badly -- you just get some repeat, nested data -- but that's unhelpful
						#The fix will be to make it a through table relationship
						keychain=selected_field.split('__')
						bottomval=bottomout(s,list(keychain))
						d[selected_field]=bottomval
					outputs.append(d)
			
			t=timer('flattening',t,True)
			return JsonResponse(outputs,safe=False)
		else:
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)


#This will only accept one field at a time
#Should only be a text field
#And it will only return max 10 results
#It will therefore serve as an autocomplete endpoint
#I should make all text queries into 'or' queries
class VoyageTextFieldAutoComplete(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		#print("username:",request.auth.user)
		st=time.time()
		params=dict(request.POST)
		k=next(iter(params))
		v=params[k][0]
		retrieve_all=True
		queryset=Voyage.objects.all()		
		kwargs={'{0}__{1}'.format(k, 'icontains'):v}
		queryset=queryset.filter(**kwargs)
		queryset=queryset.prefetch_related(k)
		queryset=queryset.order_by(k)
		results_count=queryset.count()
		fetchcount=20
		vals=[]
		for v in queryset.values_list(k).iterator():
			if v not in vals:
				vals.append(v)
			if len(vals)>=fetchcount:
				break
		def flattenthis(l):
			fl=[]
			for i in l:
				if type(i)==tuple:
					for e in i:
						fl.append(e)
				else:
					fl.append(i)
			return fl
		val_list=flattenthis(l=vals)
		output_dict={
			k:val_list,
			"results_count":results_count
		}
		print("executed in",time.time()-st,"seconds")
		return JsonResponse(output_dict,safe=False)

class DuplicateVoyage(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	def get(self,request):
		params=request.GET
		try:
			voyage_id=int(params['voyage_id'])
		except:
			return JsonResponse({"message":"No voyage ID supplied"},safe=False)
		existing_voyages=Voyage.objects.all()
		kwargs={'voyage_id':voyage_id}
		v_queryset=existing_voyages.filter(**kwargs)
		if len(v_queryset)==0:
			return JsonResponse({"message":"Error: Voyage %d does not exist" %voyage_id})
		elif len(v_queryset)>1:
			return JsonResponse({"message":"Error: Multiple voyages with id %d -- check your database" %voyage_id})
		else:
			voyage_to_duplicate=v_queryset[0]
		max_voyage_id=existing_voyages.order_by('-voyage_id')[0].voyage_id
		new_voyage_id=max_voyage_id+1
		duplicated_voyage=voyage_to_duplicate
		duplicated_voyage.id=new_voyage_id
		duplicated_voyage.voyage_id=new_voyage_id
		duplicated_voyage.save()
		existing_voyages=Voyage.objects.all()
		kwargs={'voyage_id':new_voyage_id}
		new_voyage=existing_voyages.filter(**kwargs)
		output_dict=VoyageSerializer(duplicated_voyage,many=False).data
		return JsonResponse(output_dict,safe=False)
