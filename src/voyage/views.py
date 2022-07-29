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
import networkx as nx
import urllib
import json
import requests
import time
from .models import *
from geo.models import *
import pprint
from tools.nest import *
from tools.reqs import *
import collections
import gc
from .serializers import *
from voyages2021.localsettings import *
import re

pp = pprint.PrettyPrinter(indent=4)

try:
	voyage_options=options_handler('voyage/voyage_options.json',hierarchical=False)
except:
	print("WARNING. BLANK VOYAGE OPTIONS.")
	voyage_options={}

try:
	voyage_routes=options_handler('static/customcache/routes.json',hierarchical=False)
except:
	print("WARNING. BLANK VOYAGE ROUTES.")
	voyage_routes={}		



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
		print("+++++++\nusername:",request.auth.user)
# 		try:
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options)
		if len(error_messages)==0:
			st=time.time()
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			#read_serializer=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
			read_serializer=VoyageSerializer(queryset,many=True)
			serialized=read_serializer.data
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
		
			resp=JsonResponse(outputs,safe=False,headers=headers)
			resp.headers['total_results_count']=headers['total_results_count']
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return resp
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)
# 		except:
# 			pass

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
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
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
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

class VoyageCrossTabs(generics.GenericAPIView):
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
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		groupby_fields=params.get('groupby_fields')
		value_field_tuple=params.get('value_field_tuple')
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			u2=FLASK_BASE_URL+'crosstabs/'
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
	'''
	Given
	1. an aggregation function
	2. a list of fields
	2a. the first of which is the field you want to group by
	2b. the following of which is/are the field(s) you want to get the summary stats on
	returns
	Dictionaries, organized by the numeric fields' names, with its' children being k/v pairs of
	--> k = value of grouped var
	--> v = aggregated value of numeric var for that grouped var val
	'''
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
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
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				return JsonResponse(json.loads(r.text),safe=False)
			else:
				print("failed\n+++++++")
				return JsonResponse({'status':'false','message':'bad crosstabs request'}, status=400)
		else:
			print("failed\n+++++++")
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
		print("+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.POST)
		u2=FLASK_BASE_URL + 'dataframes/'
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		voyageobjects=Voyage.objects
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(voyageobjects,self,request,voyage_options,retrieve_all=retrieve_all,selected_fields_exception=True)
		if len(error_messages)==0:
			ids=[i[0] for i in queryset.values_list('id')]
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			if r.ok:
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				return JsonResponse(json.loads(r.text),safe=False,headers={'results_count':results_count})
			else:
				print("failed\n+++++++")
				return JsonResponse({'status':'false','message':'bad request to cache'}, status=400)
		else:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=400)

#DATAFRAME ENDPOINT (A resource hog -- internal use only!!)
class VoyageDataFrames(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.POST)
		retrieve_all=True
		if 'results_per_page' in params:
			retrieve_all=False
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,auto_prefetch=False,retrieve_all=retrieve_all,selected_fields_exception=True)
		if len(error_messages)==0:
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
			if selected_fields==[]:
				sf=list(voyage_options.keys())
			else:
				sf=[i for i in selected_fields if i in list(voyage_options.keys())]
			
			serialized=VoyageSerializer(queryset,many=True,selected_fields=selected_fields)
			serialized=serialized.data
			output_dicts={}
			for selected_field in sf:
				keychain=selected_field.split('__')
				for s in serialized:
					bottomval=bottomout(s,list(keychain))
					if selected_field in output_dicts:
						output_dicts[selected_field].append(bottomval)
					else:
						output_dicts[selected_field]=[bottomval]
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dicts,safe=False,headers=headers)
		else:
			print("failed\n+++++++")
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
		print("+++++++\nusername:",request.auth.user)
		try:
			st=time.time()
			params=dict(request.POST)
			k=next(iter(params))
			v=params[k][0]
			retrieve_all=True
			queryset=Voyage.objects.all()
			#print("------->",k,v,re.sub("\\\\+","",v),"<---------")
			v=re.sub("\\\\+","",v)
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
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output_dict,safe=False)
		except:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':'bad autocomplete request'}, status=400)

class VoyageAggRoutes(generics.GenericAPIView):
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		try:
			st=time.time()
			print("+++++++\nusername:",request.auth.user)
			params=dict(request.POST)
			groupby_fields=params.get('groupby_fields')
			value_field_tuple=params.get('value_field_tuple')
			queryset=Voyage.objects.all()
			queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
			ids=[i[0] for i in queryset.values_list('id')]

			u2=FLASK_BASE_URL+'crosstabs/'
			d2=params
			d2['ids']=ids
			r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
			j=json.loads(r.text)

			abpairs={int(float(k)):{int(float(v)):j[k][v] for v in j[k]} for k in j}
			dataset=int(params['dataset'][0])

			routes=[]
			node_ids=[]

			def calControlPoint(points, smoothing=0.3):
				#if i passed this function
				##not just (x,y) tuples
				##but (x,y,id) triples
				###where id was unique for each AB BC CD edge
				###could we reformat the output to look like [n node_ids],[n-1 edge_ids],[(n-1)*2 control points]
				### or {edge_id:[[[Ax,Ay],[Bx,By]],[[ctrl1x,ctrl1y],[ctrl2x,ctrl2y]]]}
				A, B, C=points[:3]
				Controlx = B[0] + smoothing*(A[0]-C[0])
				Controly = B[1] + smoothing*(A[1]-C[1])
				result = [A, [[Controlx, Controly], B]]
				for i in range(2, len(points)):
					if i == len(points)-1:
						start_point, mid_point, end_point = points[i-1], points[i], points[i]
					else:
						start_point, mid_point, end_point = points[i-1], points[i], points[i+1]
					next_Controlx1 = start_point[0]*2 - Controlx
					next_Controly1 = start_point[1]*2 - Controly

					next_Controlx2 = mid_point[0] + smoothing*(start_point[0] - end_point[0])
					next_Controly2 = mid_point[1] + smoothing*(start_point[1] - end_point[1])

					result.append([[next_Controlx1, next_Controly1], [next_Controlx2, next_Controly2], mid_point])
					Controlx, Controly = next_Controlx2, next_Controly2
				return result


			route_legs={}
			route_weights={}

			failedroutes=[]

			for s_id in abpairs:
				node_ids.append(s_id)
				for t_id in abpairs[s_id]:
					node_ids.append(t_id)
					w=int(abpairs[s_id][t_id])
					try:
						route=voyage_routes[str(dataset)][str(s_id)][str(t_id)]
						##Currently suppressing any straight-line routes
						##As that typically means they've got bad geo data so shouldn't be shown anyways
						###BUT I need to go back and fix it
	
						for e_id in route:
		
							if type(e_id)==list:
								print(s_id,t_id)
		
							if e_id not in route_legs:
								route_legs[e_id]=[route[e_id]]
							else:
								route_legs[e_id].append(route[e_id])


							if e_id not in route_weights:
								route_weights[e_id]=w
							else:
								route_weights[e_id]+=w
					except:
						#LOTS OF FAILED ROUTES CURRENTLY
						if [s_id,t_id] not in failedroutes:
							failedroutes.append([s_id,t_id])

			print("failed routes (probably nulled lat/longs):",failedroutes)

			routes=[]

			for e_id in route_legs:

				legs=route_legs[e_id]

				#print(legs)

				controls_x1=[leg[1][0][0] for leg in legs]
				controls_x2=[leg[1][1][0] for leg in legs]

				controls_y1=[leg[1][0][1] for leg in legs]
				controls_y2=[leg[1][1][1] for leg in legs]


				controls_x1=sum(controls_x1)/len(controls_x1)
				controls_y1=sum(controls_y1)/len(controls_y1)
				controls_x2=sum(controls_x2)/len(controls_x2)
				controls_y2=sum(controls_y2)/len(controls_y2)

				control1=[controls_x1,controls_y1]
				control2=[controls_x2,controls_y2]

				consolidated_leg=[[legs[0][0][0],legs[0][0][1]],[control1,control2],route_weights[e_id]]

				routes.append(consolidated_leg)

			node_ids=list(set(node_ids))

			geojson={"type": "FeatureCollection", "features": []}

			node_ids=list(set(node_ids))

			locations=Location.objects.all()
			nodes=locations.filter(pk__in=node_ids)
			for node in nodes:
				node_id=node.id
				longitude=node.longitude
				latitude=node.latitude
				if longitude is not None and latitude is not None:
					name=node.name

					geojsonfeature={
						"type": "Feature",
						"id":node_id,
						"geometry": {"type":"Point","coordinates": [longitude,latitude]},
						"properties":{"name":name}
					}

					geojson['features'].append(geojsonfeature)

			output={"points":geojson,"routes":routes}

			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(output,safe=False)
		except:
			print("failed\n+++++++")
			return JsonResponse({'status':'false','message':'bad request'}, status=400)