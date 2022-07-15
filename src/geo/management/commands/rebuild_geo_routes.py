import requests
import itertools
from geo.models import *
from voyage.models import *
from past.models import *
from django.db.models import Avg,Sum,Min,Max,Count,Q
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os
import re
from math import sqrt
import pprint
import networkx as nx
from .app_secrets import headers

def make_networks(dataset,groupby_pairs,url,extra_search_params=[]):
	print("dataset",dataset)

	#BUILD THE NETWORK TO WALK
	print("building network for dataset",dataset)
	adjacencies=Adjacency.objects.all()
	adjacencies=adjacencies.filter(**{'dataset':dataset})
	for i in ['source','target']:
		adjacencies=adjacencies.prefetch_related(i)
	locations=Location.objects.all()		

	##we get all the voyage endpoints (port, region, broad_region)
	##and let's also make sure that "places" with no long or lat are not in our results
	qobjstrs=["Q(%s='%s')" %('location_type__name',endpoint_type) for endpoint_type in ["Port","Region","Broad Region"]]
	qobjstrs.append('Q(latitude__isnull=False)')
	qobjstrs.append('Q(longitude__isnull=False)')
	voyage_endpoints=locations.filter(eval('|'.join(qobjstrs)))

	##we then feed those into a networkx graph:
	## nodes (waypoints and endpoints)
	## edges (adjacencies)
	G=nx.Graph()
	for l in locations:
		G.add_node(l.id)
	
	edges={}
	for a in adjacencies:
		sv_id=a.source.id
		tv_id=a.target.id
		aw=a.distance
		edge_id=a.id
		G.add_edge(sv_id,tv_id,weight=aw,edge_id=edge_id)
		if sv_id not in edges:
			edges[sv_id]={tv_id:edge_id}
		else:
			edges[sv_id][tv_id]=edge_id
		if tv_id not in edges:
			edges[tv_id]={sv_id:edge_id}
		else:
			edges[tv_id][sv_id]=edge_id
	print(G)
	for groupby_pair in groupby_pairs:
		routes=[]
		#pull all the a/b value pairs
		#on all these a/b variable pairs
		alice,bob=groupby_pair
		data={
			'selected_fields':groupby_pair,
			'dataset':[dataset,dataset]
		}
		for sp in extra_search_params:
			data[sp]=extra_search_params[sp]
		r=requests.post(url=url,headers=headers,data=data)
		columns=json.loads(r.text)
		#this will return all the a/b value pairs, excluding the nulls
		#print(columns)
		rows=[
			sorted([
				columns[alice][k],
				columns[bob][k]
			])
			for k in range(len(columns[alice])) if
			columns[alice][k] is not None and
			columns[bob][k] is not None
		]
		
		#now dedupe
		
		abpairs=[]
		for row in rows:
			if row not in abpairs:
				abpairs.append(row)
		
		print("unique a/b pairs",len(abpairs))
		
		#now find shortest path in the network for each unique alice/bob pair
		
		routes={}
		
		print("finding routes")
		
		def calControlPoint_new(points, edge_ids, smoothing=0.15):
			#edge_ids = [i for i in range(len(points)-1)]
			A, B, C=points[:3]
			Controlx = B[0] + smoothing*(A[0]-C[0])
			Controly = B[1] + smoothing*(A[1]-C[1])
			result={}
			result[edge_ids[0]] = [[A, B], [[Controlx, Controly], [Controlx, Controly]]]
			for i in range(2, len(points)):
				if i == len(points)-1:
					start_point, mid_point, mid_point = points[i-1], points[i], points[i]
				else:
					start_point, mid_point, end_point = points[i-1], points[i], points[i+1]
				next_Controlx1 = start_point[0]*2 - Controlx
				next_Controly1 = start_point[1]*2 - Controly
		
				next_Controlx2 = mid_point[0] + smoothing*(start_point[0] - end_point[0])
				next_Controly2 = mid_point[1] + smoothing*(start_point[1] - end_point[1])
		
				#result.append([[next_Controlx1, next_Controly1], [next_Controlx2, next_Controly2], mid_point])
				result[edge_ids[i-1]] = [[start_point, mid_point], [[next_Controlx1, next_Controly1], [next_Controlx2, next_Controly2]]]
				Controlx, Controly = next_Controlx2, next_Controly2
	
			return result
		
		for abpair in abpairs:
			
			route_edge_ids=[]
			
			s_id,t_id=abpair
			try:	
				sp=nx.shortest_path(G,s_id,t_id,'weight')
			except:
				print('no path between',s_id,t_id)
			
			waypoints=[]
			
			c=0
			
			for p_id in sp:
				l=locations.get(pk=p_id)
				waypoints.append([float(l.latitude),float(l.longitude)])				
				
				if c!=0:
					route_edge_ids.append(edges[sp[c-1]][p_id])
				c+=1
			
			if len(waypoints)>3:
				#print(waypoints)
				route=calControlPoint_new(waypoints,route_edge_ids)
			
				#source_location=locations.filter(**{'id':s_id})[0]
				#target_location=locations.filter(**{'id':t_id})[0]
				'''for k in route:
					r2=route[k]
					r2.append(10)
					print(r2)'''
				#route=Route(source=source_location,target=target_location,dataset=dataset,shortest_route=json.dumps(waypoints))
				#route.save()
				if s_id not in routes:
					routes[s_id]={t_id:route}
				else:
					routes[s_id][t_id]=route
	return routes




class Command(BaseCommand):
	
	help = '\
	Given a bimodal network of:\
		ports,regions,& broadregions to oceanic waypoints\
		oceanic waypoints to one another\
		(all made available by custom django command "rebuild_geo_network")\
	This django command will try to find the shortest path from all of the non-waypoint locations to one another, through the oceanic networks.\
	I say "networkS" because we have not yet unified the IAM and TAST databases\' routes.\
	Which distinction is hard-coded in here with the datasest=0,1 filters\
	'
	def handle(self, *args, **options):
		st=time.time()
		pp = pprint.PrettyPrinter(indent=4)
		print("deleting all existing routes...")
		locations=Location.objects.all()
		routes=Route.objects.all()
		routes.delete()
		#for route in routes:
		#	print(route)
		#	route.delete()
		
		print("rebuilding routes...")
		
		#start with a list of paired __geo_location__id variables
		#hard-coding the valid pairings below, for now.
		'''imp_begin=[
			"voyage_itinerary__imp_port_voyage_begin__geo_location__id",
			"voyage_itinerary__imp_region_voyage_begin__geo_location__id",
			"voyage_itinerary__imp_broad_region_voyage_begin__geo_location__id"
		]

		imp_purchase=[
			"voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_broad_region_of_slave_purchase__geo_location__id"
		]

		imp_dis=[
			"voyage_itinerary__imp_principal_port_slave_dis__geo_location__id",
			"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id",
			"voyage_itinerary__imp_broad_region_slave_dis__geo_location__id"
		]
		
		groupby_pairs=[]
		
		for a in imp_begin:
			for b in imp_purchase:
				groupby_pairs.append([a,b])
		
		for a in imp_purchase:
			for b in imp_dis:
				groupby_pairs.append([a,b])'''
		
		groupby_pairs=[
			["voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_principal_port_slave_dis__geo_location__id"
			],
			["voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id"
			]
		]
		
		groupby_pairs=[
			["voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id"
			]
		]
		
		pp.pprint(groupby_pairs)
		
		#and of course we need to separate the datasets' for voyages and adjacencies
		datasets=[0,1]
		
		#for each of those paired variables, we're going to need the unique tuple values for each voyage
		##i don't THINK we need to do this for people, as their itineraries are based on voyages but i could be wrong...
		
		url='http://voyages-django:8000/voyage/dataframes'
		base_filepath='static/customcache'
		os.makedirs(base_filepath,exist_ok=True)
		fpath=os.path.join(base_filepath,'routes.json')
		d=open(fpath,'w')
		d.write(json.dumps({}))
		d.close()
		
		def update_routes(newroutes,dataset):
			print("...adding to cache...")
			
			d=open(fpath,'r')
			t=d.read()
			routes=json.loads(t)
			d.close()
			
			if dataset not in routes:
				routes[dataset]={}
			
			for s_id in newroutes:
				for t_id in newroutes[s_id]:
					v=newroutes[s_id][t_id]
					if s_id not in routes[dataset]:
						routes[dataset][s_id]={t_id:v}
					else:
						routes[dataset][s_id][t_id]=v
					
					#and reverse directions as well just in case?????
					
					vk=list(v.keys())
					vk.reverse()
					rv=[v[i] for i in vk]
					if t_id not in routes[dataset]:
						routes[dataset][t_id]={s_id:rv}
					else:
						routes[dataset][t_id][s_id]=rv
					
			d=open(fpath,'w')
			d.write(json.dumps(routes))
			d.close()

		
		for dataset in datasets:
			newroutes=make_networks(dataset,groupby_pairs,url)
			update_routes(newroutes,dataset)
		
		##NOW DO INLAND IAM ENSLAVED GROUPBY PAIRS
		
		'''url='http://voyages-django:8000/past/enslaved/dataframes'
		
		groupby_pairs=[
			[
				'post_disembark_location__geo_location__id',
				'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__id'
			]
		]
		
		newroutes=make_networks(0,groupby_pairs,url,extra_search_params={'id':[1,499999]})
		update_routes(newroutes,0)
		newroutes=make_networks(1,groupby_pairs,url,extra_search_params={'id':[500000,1000000]})
		update_routes(newroutes,1)'''
		
		print("finished in %d minutes" %int((time.time()-st)/60))