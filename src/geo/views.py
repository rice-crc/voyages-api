from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.db.models import Q,Prefetch
from django.http import HttpResponse, JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import generics
from rest_framework.metadata import SimpleMetadata
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
import urllib
import json
import requests
import time
from .models import *
from .serializers import *
import pprint
from tools.nest import *
from tools.reqs import *
import collections
import networkx as nx

location_options=options_handler('geo/location_options.json',hierarchical=False)




class LocationList(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer
	def options(self,request):
		j=options_handler('geo/location_options.json',request)
		return JsonResponse(j,safe=False)
	def post(self,request):
		try:
			times=[]
			labels=[]
			#print("+++++++\nusername:",request.auth.user)
			print("+++++++\nGEO")
			st=time.time()
			queryset=Location.objects.all()
			queryset,selected_fields,next_uri,prev_uri,results_count,error_messages=post_req(queryset,self,request,location_options,auto_prefetch=True,retrieve_all=True)
			if len(error_messages)==0:
				headers={"next_uri":next_uri,"prev_uri":prev_uri,"total_results_count":results_count}
				labels.append('building query')
				read_serializer=LocationSerializer(queryset,many=True)
				labels.append('serialization')
				serialized=read_serializer.data
				labels.append('sql execution')
			
				outputs=[]
		
				hierarchical=request.POST.get('hierarchical')
				if str(hierarchical).lower() in ['false','0','f','n']:
					hierarchical=False
				else:
					hierarchical=True
		
				if hierarchical==False:
					if selected_fields==[]:
						selected_fields=[i for i in location_options]
			
					for s in serialized:
						d={}
						for selected_field in selected_fields:
							keychain=selected_field.split('__')
							bottomval=bottomout(s,list(keychain))
							d[selected_field]=bottomval
						outputs.append(d)
				else:
					outputs=serialized
				labels.append('flattening...')
				print("Internal Response Time:",time.time()-st,"\n+++++++")
				for i in range(1,len(times)):
					print(labels[i-1],times[i]-times[i-1])		
				return JsonResponse(outputs,safe=False,headers=headers)
			else:
				return JsonResponse({'status':'false','message':' | '.join(error_messages)}, status=500)
		except:
			return JsonResponse({'status':'false','message':'geo request failed'}, status=500)


class getGeoJsonNetwork(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer	
	def post(self,request):
		try:
			print("+++++++\nFULL GeoJSON Network")
			st=time.time()
			adjacencies=Adjacency.objects.all()
			routes_featurecollection={"type":"FeatureCollection","features":[]}
			prefetch_fields=[
				'source',
				'target'
			]
			for f in prefetch_fields:
				adjacencies=adjacencies.prefetch_related(f)
		
			for adjacency in adjacencies:
				adj_id=adjacency.id
				source=adjacency.source
				target=adjacency.target
				routes_featurecollection['features'].append({
				"type":"Feature",
				"geometry":{
					"id":adj_id,
					"type":"LineString",
					"coordinates":[
						(source.longitude,source.latitude),
						(target.longitude,target.latitude)
					]
				},
				"properties":{"source_id":source.id,"target_id":target.id}
				})
		
			print("Internal Response Time:",time.time()-st,"\n+++++++")
		
			#d=open('routes.json','w')
			#d.write(json.dumps(routes_featurecollection,cls=DjangoJSONEncoder))
			#d.close()
		
			return JsonResponse(routes_featurecollection,safe=False)
		except:
			return JsonResponse({'status':'false','message':'geo request failed'}, status=500)

class getRoutes(generics.GenericAPIView):
	authentication_classes=[TokenAuthentication]
	permission_classes=[IsAuthenticated]
	serializer_class=LocationSerializer	
	def post(self,request):

		print("+++++++\nGeoJSON ROUTES")
		try:
			st=time.time()

			params=dict(request.POST)
			dataset=int(params['dataset'][0])
			##third argument: output_format -- can be either
			####"geojson", which returns just a big featurecollection or
			####"geosankey", which returns a featurecollection of points only, alongside an edges dump as "links.csv" -- following the specifications here: https://github.com/geodesign/spatialsankey
			output_format=params['output_format'][0]
	
			##we fetch all of the adjacencies in specified dataset (trans-atlantic or intra-american)
			##and prefetch all the places referenced by those adjacencies
			adjacencies=Adjacency.objects.all()
			adjacencies=adjacencies.filter(**{'dataset':dataset})
			for i in ['source','target']:
				adjacencies=adjacencies.prefetch_related(i)
			locations=Location.objects.all()		
	
			##we get all the voyage endpoints (port, region, broad_region)
			##and let's also make sure that "places" with no long or lat are not in our results
			##CLEAN UP YOUR DATA, PEOPLE
			qobjstrs=["Q(%s='%s')" %('location_type__name',endpoint_type) for endpoint_type in ["Port","Region","Broad Region"]]
			qobjstrs.append('Q(latitude__isnull=True)')
			qobjstrs.append('Q(longitude__isnull=True)')
			voyage_endpoints=locations.filter(eval('|'.join(qobjstrs)))
	
			##we then feed those into a networkx graph:
			## nodes (waypoints and endpoints)
			## edges (adjacencies)
			G=nx.Graph()
			for l in locations:
				G.add_node(l.id)
			for a in adjacencies:
				sv_id=a.source.id
				tv_id=a.target.id
				G.add_edge(sv_id,tv_id,edge_id=a.id)
	
			## we then get all the pk ids of all the adjacencies
			## and feed these into the networkx graph to find the shortest path between them (live)
			#### we should almost certainly pre-generate these -- I started that in rebuild_geo_routes.py, but now I'm just running it live b/c I don't think I was doing it efficiently enough
			#### and weight the edges in the future so the "shortest path" is the GEOGRAPHICALLY shortest path, not the least-hops shortest path)
			routes_featurecollection={"type":"FeatureCollection","features":[]}
			edge_weights={}
	
			for s_t in abpairs:
				s_id,t_id,w=[int(i) for i in s_t.split(",")]
		
				for p_id in [s_id,t_id]:
					p=locations.filter(**{'id':p_id})[0]
					p_lat=p.latitude
					p_lon=p.longitude
					p_name=p.name
					geojsonfeature={
						"type": "Feature",
						"id":p_id,
						"geometry":{
							"type":"Point",
							"coordinates": [float(p_lon), float(p_lat)]
						},
						"properties":{"name":p_name}
					}
					routes_featurecollection['features'].append(geojsonfeature)
		
				try:
					sp=nx.shortest_path(G,s_id,t_id)
				except:
					sp=[]
		
				if len(sp)>0:
					for idx in range(1,len(sp)):
						a=sp[idx]
						b=sp[idx-1]
						e_id=G[a][b]['edge_id']
						if e_id in edge_weights:
							edge_weights[e_id]+=w
						else:
							edge_weights[e_id]=w
		
			if output_format=="geojson":
				for e in edge_weights:
					w=edge_weights[e]
					a=adjacencies.filter(**{'id':e})[0]
					sv=a.source
					tv=a.target
					sv_longlat=(float(sv.longitude),float(sv.latitude))
					tv_longlat=(float(tv.longitude),float(tv.latitude))
					routes_featurecollection['features'].append({
						"type":"Feature",
						"id":e,
						"geometry":{
							"type":"LineString",
							"coordinates":[sv_longlat,tv_longlat]
						},
						"properties":{"weight":w}
					})
				output=routes_featurecollection
			elif output_format=="geosankey":
				edges=[]
				for e in edge_weights:
					w=edge_weights[e]
					a=adjacencies.filter(**{'id':e})[0]
					sv=a.source
					tv=a.target
					sv_id=sv.id
					tv_id=tv.id
					sv_longlat=(float(sv.longitude),float(sv.latitude))
					tv_longlat=(float(tv.longitude),float(tv.latitude))
					for p in [[sv_id,sv_longlat],[tv_id,tv_longlat]]:
						p_id,p_longlat=p
						geojsonfeature={
							"type":"Feature",
							"id":p_id,
							"geometry":{
								"type":"Point",
								"coordinates":p_longlat
							}
						}
						routes_featurecollection['features'].append(geojsonfeature)
					edges.append([sv_id,tv_id,w])
				output={'links':edges,'nodes':routes_featurecollection}
	
			print("Internal Response Time:",time.time()-st,"\n+++++++")
	
			return JsonResponse(output,safe=False)
		except:
			return JsonResponse({'status':'false','message':'routes request failed'}, status=500)