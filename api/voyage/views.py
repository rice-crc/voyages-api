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
import collections
import gc
from .serializers import *
from voyages3.localsettings import *
import re

try:
	voyage_options=options_handler('voyage/voyage_options.json',hierarchical=False)
except:
	print("WARNING. BLANK VOYAGE OPTIONS.")
	voyage_options={}

# #LONG-FORM TABULAR ENDPOINT. PAGINATION IS A NECESSITY HERE!
class VoyageList(generics.GenericAPIView):
	# serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def options(self,request):
		j=options_handler('voyage/voyage_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		print("VOYAGE LIST+++++++\nusername:",request.auth.user)
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=False)
		if len(error_messages)==0:
			st=time.time()
			headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
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
		print("+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		aggregations=params.get('aggregate_fields')
		print("aggregations:",aggregations)
		queryset=Voyage.objects.all()
		aggregation,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
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
		u2=FLASK_BASE_URL+'get_indices/'
		r=requests.get(url=u2,headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)
	def options(self,request):
		u2=FLASK_BASE_URL+'get_indices/'
		r=requests.get(url=u2,headers={"Content-type":"application/json"})
		return JsonResponse(json.loads(r.text),safe=False)

class VoyageCrossTabs(generics.GenericAPIView):
	'''
	Think of this as a pivot table (but it will generalize later)
	This view takes:
		a groupby tuple (row, col)
		a value field tuple (cellvalue,aggregationfunction)
		any search parameters you want!
	'''
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
	serializer_class=VoyageSerializer
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		st=time.time()
		print("+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		print(params)
		groupby_by=params.get('groupby_by')
		groupby_cols=params.get('groupby_cols')
		value_field_tuple=params.get('value_field_tuple')
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		ids=[i[0] for i in queryset.values_list('id')]
		u2=FLASK_BASE_URL+'groupby/'
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
		print("+++++++\nusername:",request.auth.user)
		st=time.time()
		params=dict(request.POST)
		retrieve_all=True
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(
			queryset,
			self,
			request,
			voyage_options,
			auto_prefetch=False,
			retrieve_all=True
		)
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

#This will only accept one field at a time
#Should only be a text field
#And it will only return max 10 results
#It will therefore serve as an autocomplete endpoint
#I should make all text queries into 'or' queries
class VoyageTextFieldAutoComplete(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	def post(self,request):
		print("+++++++\nusername:",request.auth.user)
# 		try:
		st=time.time()
		params=dict(request.POST)
		k=params.get('ac_field')
		v=params.get('ac_val')
		if k is None or v is None:
			return JsonResponse(
				{
					'status':'false',
					'message':'ac_field and ac_val params are required'
				},
				status=400
			)
		else:
			k=k[0]
			v=v[0]
		
		print("voyage/autocomplete",k,v)
		queryset=Voyage.objects.all()
		kstub=re.sub("__[^__]+?$","",k)
		if '__' in k:
			k_id_field=kstub+"__id"
		else:
			k_id_field="id"
		queryset=queryset.prefetch_related(kstub)
		kwargs={'{0}__{1}'.format(k, 'icontains'):v}
		queryset=queryset.filter(**kwargs)
		queryset=queryset.order_by(k)
		total_results_count=queryset.count()
		candidates=[]
		fetchcount=30
		## Have to use this ugliness b/c we're not in postgres
		## https://docs.djangoproject.com/en/4.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct
		for v in queryset.values_list(k_id_field,k).iterator():
			if v not in candidates:
				candidates.append(v)
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
		print("+++++++\nusername:",request.auth.user)
		params=dict(request.POST)
		zoom_level=params.get('zoom_level')
		queryset=Voyage.objects.all()
		queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,voyage_options,retrieve_all=True)
		
		
		voys=queryset.values_list(
			'id',
# 			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id',
# 			'voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name',
# 			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__id',
# 			'voyage_itinerary__imp_principal_port_slave_dis__geo_location__name',
# 			'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id',
# 			'voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__name',
# 			'voyage_itinerary__imp_principal_region_slave_dis__geo_location__id',
# 			'voyage_itinerary__imp_principal_region_slave_dis__geo_location__name'
		)
		ids=[i[0] for i in list(voys)]
		print("fetch id time",time.time()-st)
		ids=[i[0] for i in queryset.values_list('id')]
		u2=FLASK_BASE_URL+'crosstabs_maps/'
		d2=params
		d2['ids']=ids
		r=requests.post(url=u2,data=json.dumps(d2),headers={"Content-type":"application/json"})
		print(r.text)
		j=json.loads(r.text)
		print(type(j))
		if r.ok:
			print("Internal Response Time:",time.time()-st,"\n+++++++")
			return JsonResponse(j,safe=True)
		else:
			return JsonResponse({'status':'false','message':'bad groupby request'}, status=400)



# 
# 			abpairs={int(float(k)):{int(float(v)):j[k][v] for v in j[k]} for k in j}
# 			dataset=int(params['dataset'][0])
# 
# 			routes=[]
# 			node_ids=[]
# 
# 			def calControlPoint(points, smoothing=0.3):
# 				#if i passed this function
# 				##not just (x,y) tuples
# 				##but (x,y,id) triples
# 				###where id was unique for each AB BC CD edge
# 				###could we reformat the output to look like [n node_ids],[n-1 edge_ids],[(n-1)*2 control points]
# 				### or {edge_id:[[[Ax,Ay],[Bx,By]],[[ctrl1x,ctrl1y],[ctrl2x,ctrl2y]]]}
# 				A, B, C=points[:3]
# 				Controlx = B[0] + smoothing*(A[0]-C[0])
# 				Controly = B[1] + smoothing*(A[1]-C[1])
# 				result = [A, [[Controlx, Controly], B]]
# 				for i in range(2, len(points)):
# 					if i == len(points)-1:
# 						start_point, mid_point, end_point = points[i-1], points[i], points[i]
# 					else:
# 						start_point, mid_point, end_point = points[i-1], points[i], points[i+1]
# 					next_Controlx1 = start_point[0]*2 - Controlx
# 					next_Controly1 = start_point[1]*2 - Controly
# 
# 					next_Controlx2 = mid_point[0] + smoothing*(start_point[0] - end_point[0])
# 					next_Controly2 = mid_point[1] + smoothing*(start_point[1] - end_point[1])
# 
# 					result.append([[next_Controlx1, next_Controly1], [next_Controlx2, next_Controly2], mid_point])
# 					Controlx, Controly = next_Controlx2, next_Controly2
# 				return result
# 
# 
# 			route_legs={}
# 			route_weights={}
# 
# 			failedroutes=[]
# 
# 			for s_id in abpairs:
# 				node_ids.append(s_id)
# 				for t_id in abpairs[s_id]:
# 					node_ids.append(t_id)
# 					w=int(abpairs[s_id][t_id])
# 					try:
# 						route=voyage_routes[str(dataset)][str(s_id)][str(t_id)]
# 						##Currently suppressing any straight-line routes
# 						##As that typically means they've got bad geo data so shouldn't be shown anyways
# 						###BUT I need to go back and fix it
# 	
# 						for e_id in route:
# 		
# 							if type(e_id)==list:
# 								print(s_id,t_id)
# 		
# 							if e_id not in route_legs:
# 								route_legs[e_id]=[route[e_id]]
# 							else:
# 								route_legs[e_id].append(route[e_id])
# 
# 
# 							if e_id not in route_weights:
# 								route_weights[e_id]=w
# 							else:
# 								route_weights[e_id]+=w
# 					except:
# 						#LOTS OF FAILED ROUTES CURRENTLY
# 						if [s_id,t_id] not in failedroutes:
# 							failedroutes.append([s_id,t_id])
# 			
# 			locations=Location.objects.all()
# 			
# 			verbose_mode=params.get('verbose_mode') or 'f'
# 			if verbose_mode.lower() in ['t','true']:
# 				print('******\nfailed routes:')
# 				for r in failedroutes:
# 					s_id,t_id=r
# 					s=locations.get(pk=s_id)
# 					t=locations.get(pk=t_id)
# 					print("{0} ({1},{2}) --> {3} ({4},{5})".format(s.name,s.latitude,s.longitude,t.name,t.latitude,t.longitude))
# 				print('******')
# 			else:
# 				print("failed routes (probably nulled lat/longs):",failedroutes)
# 
# 			routes=[]
# 
# 			for e_id in route_legs:
# 
# 				legs=route_legs[e_id]
# 				
# 
# 				controls_x1=[leg[1][0][0] for leg in legs]
# 				controls_x2=[leg[1][1][0] for leg in legs]
# 
# 				controls_y1=[leg[1][0][1] for leg in legs]
# 				controls_y2=[leg[1][1][1] for leg in legs]
# 
# 
# 				controls_x1=sum(controls_x1)/len(controls_x1)
# 				controls_y1=sum(controls_y1)/len(controls_y1)
# 				controls_x2=sum(controls_x2)/len(controls_x2)
# 				controls_y2=sum(controls_y2)/len(controls_y2)
# 
# 				control1=[controls_x1,controls_y1]
# 				control2=[controls_x2,controls_y2]
# 
# 				consolidated_leg=[[legs[0][0][0],legs[0][0][1]],[control1,control2],route_weights[e_id]]
# 
# 				routes.append(consolidated_leg)
# 
# 			node_ids=list(set(node_ids))
# 
# 			geojson={"type": "FeatureCollection", "features": []}
# 
# 			node_ids=list(set(node_ids))
# 
# 			
# 			nodes=locations.filter(pk__in=node_ids)
# 			for node in nodes:
# 				node_id=node.id
# 				longitude=node.longitude
# 				latitude=node.latitude
# 				if longitude is not None and latitude is not None:
# 					name=node.name
# 
# 					geojsonfeature={
# 						"type": "Feature",
# 						"id":node_id,
# 						"geometry": {"type":"Point","coordinates": [longitude,latitude]},
# 						"properties":{"name":name}
# 					}
# 
# 					geojson['features'].append(geojsonfeature)
# 
# 			output={"points":geojson,"routes":routes}
# 
# 			print("Internal Response Time:",time.time()-st,"\n+++++++")
		return JsonResponse(output,safe=False)
# 		except:
# 			print("failed\n+++++++")
# 			return JsonResponse({'status':'false','message':'bad request'}, status=400)