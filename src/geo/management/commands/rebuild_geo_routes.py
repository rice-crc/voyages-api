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
	#qobjstrs.append('Q(latitude__isnull=False)')
	#qobjstrs.append('Q(longitude__isnull=False)')
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
	routes={}
	for groupby_pair in groupby_pairs:
		print(groupby_pair)
		#pull all the a/b value pairs
		#on all these a/b variable pairs
		alice,bob=groupby_pair
		
		
		data={
			'selected_fields':groupby_pair,
			'dataset':[dataset,dataset],
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
					start_point, mid_point, end_point = points[i-1], points[i], points[i]
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
			
			badpair=False
			if abpair in [[2404, 2401], [2404, 2402], [2404, 2404], [2404, 2474], [2405, 2405], [2406, 2401], [2406, 2402], [2406, 2404], [2406, 2405], [2406, 2406], [2408, 2402], [2409, 2408], [2411, 2408], [2411, 2409], [2411, 2410], [2412, 2407], [2412, 2408], [2413, 2412], [2414, 2402], [2414, 2404], [2414, 2407], [2414, 2408], [2414, 2409], [2414, 2412], [2414, 2414], [2414, 2471], [2415, 2408], [2415, 2409], [2415, 2411], [2415, 2412], [2415, 2414], [2416, 2401], [2416, 2408], [2416, 2409], [2416, 2412], [2416, 2414], [2416, 2415], [2417, 2409], [2417, 2412], [2417, 2414], [2417, 2415], [2417, 2416], [2418, 2408], [2418, 2409], [2418, 2412], [2418, 2414], [2418, 2415], [2418, 2416], [2419, 2401], [2419, 2402], [2419, 2404], [2419, 2408], [2419, 2409], [2419, 2410], [2419, 2411], [2419, 2412], [2419, 2414], [2419, 2415], [2419, 2416], [2419, 2419], [2420, 2402], [2420, 2408], [2420, 2409], [2420, 2410], [2420, 2411], [2420, 2412], [2420, 2414], [2420, 2416], [2420, 2419], [2420, 2471], [2421, 2408], [2421, 2409], [2421, 2412], [2421, 2414], [2422, 2412], [2422, 2414], [2423, 2412], [2423, 2422], [2424, 2408], [2424, 2409], [2424, 2412], [2424, 2414], [2424, 2416], [2425, 2412], [2425, 2419], [2426, 2419], [2427, 2427], [2428, 2428], [2429, 2427], [2430, 2426], [2430, 2427], [2430, 2428], [2430, 2429], [2430, 2430], [2431, 2405], [2431, 2414], [2431, 2416], [2431, 2419], [2433, 2412], [2433, 2414], [2433, 2433], [2434, 2404], [2434, 2407], [2434, 2408], [2434, 2409], [2434, 2410], [2434, 2411], [2434, 2412], [2434, 2414], [2434, 2415], [2434, 2416], [2434, 2419], [2434, 2422], [2434, 2423], [2434, 2425], [2434, 2433], [2434, 2434], [2434, 2471], [2435, 2402], [2435, 2408], [2435, 2414], [2435, 2416], [2436, 2401], [2436, 2408], [2436, 2409], [2436, 2414], [2436, 2419], [2436, 2423], [2437, 2408], [2437, 2409], [2437, 2410], [2437, 2411], [2437, 2414], [2437, 2416], [2437, 2419], [2437, 2425], [2437, 2471], [2438, 2401], [2438, 2402], [2438, 2403], [2438, 2404], [2438, 2408], [2438, 2409], [2438, 2410], [2438, 2411], [2438, 2414], [2438, 2415], [2438, 2416], [2438, 2419], [2438, 2423], [2438, 2434], [2438, 2435], [2438, 2437], [2438, 2438], [2438, 2471], [2438, 2474], [2439, 2401], [2439, 2402], [2439, 2403], [2439, 2404], [2439, 2408], [2439, 2409], [2439, 2410], [2439, 2411], [2439, 2412], [2439, 2414], [2439, 2415], [2439, 2416], [2439, 2418], [2439, 2419], [2439, 2420], [2439, 2434], [2439, 2435], [2439, 2436], [2439, 2437], [2439, 2438], [2439, 2439], [2439, 2471], [2439, 2474], [2440, 2401], [2440, 2402], [2440, 2404], [2440, 2408], [2440, 2409], [2440, 2410], [2440, 2412], [2440, 2413], [2440, 2414], [2440, 2416], [2440, 2418], [2440, 2419], [2440, 2420], [2440, 2425], [2440, 2434], [2440, 2435], [2440, 2436], [2440, 2437], [2440, 2438], [2440, 2439], [2440, 2468], [2441, 2401], [2441, 2402], [2441, 2404], [2441, 2406], [2441, 2407], [2441, 2408], [2441, 2409], [2441, 2410], [2441, 2411], [2441, 2412], [2441, 2414], [2441, 2415], [2441, 2416], [2441, 2418], [2441, 2419], [2441, 2420], [2441, 2423], [2441, 2425], [2441, 2434], [2441, 2435], [2441, 2437], [2441, 2439], [2441, 2440], [2441, 2441], [2441, 2471], [2442, 2401], [2442, 2404], [2442, 2406], [2442, 2407], [2442, 2408], [2442, 2409], [2442, 2411], [2442, 2414], [2442, 2415], [2442, 2416], [2442, 2419], [2442, 2420], [2442, 2422], [2442, 2423], [2442, 2425], [2442, 2434], [2442, 2441], [2442, 2442], [2442, 2474], [2443, 2405], [2443, 2406], [2443, 2408], [2443, 2419], [2443, 2420], [2443, 2441], [2443, 2442], [2444, 2406], [2444, 2409], [2444, 2412], [2444, 2414], [2444, 2415], [2444, 2417], [2444, 2419], [2444, 2422], [2444, 2423], [2444, 2425], [2444, 2438], [2444, 2439], [2444, 2441], [2444, 2442], [2444, 2443], [2444, 2444], [2444, 2474], [2445, 2419], [2445, 2441], [2446, 2408], [2446, 2412], [2447, 2404], [2447, 2419], [2447, 2426], [2454, 2404], [2454, 2412], [2454, 2414], [2454, 2415], [2454, 2417], [2454, 2419], [2454, 2434], [2455, 2434], [2466, 2408], [2468, 2404], [2468, 2419], [2469, 2419], [2469, 2435], [2469, 2436], [2470, 2434], [2471, 2408], [2471, 2409], [2471, 2415], [2471, 2416], [2472, 2408], [2472, 2409], [2472, 2414], [2472, 2419], [2472, 2434], [2472, 2474], [2473, 2434], [2474, 2401], [2474, 2412], [2474, 2419], [2474, 2434], [2474, 2437], [2475, 2430], [2475, 2493], [2481, 2428], [2481, 2434], [2483, 2409], [2483, 2412], [2483, 2414], [2483, 2416], [2483, 2419], [2483, 2434], [2483, 2472], [2484, 2419], [2484, 2434], [2484, 2445], [2485, 2405], [2485, 2406], [2485, 2407], [2485, 2408], [2485, 2409], [2485, 2412], [2485, 2414], [2485, 2416], [2485, 2417], [2485, 2419], [2485, 2422], [2485, 2423], [2485, 2425], [2485, 2427], [2485, 2434], [2485, 2446], [2485, 2454], [2485, 2472], [2485, 2473], [2485, 2474], [2485, 2476], [2485, 2483], [2485, 2485], [2491, 2491]]:
				badpair=True
			
			route_edge_ids=[]
			
			s_id,t_id=abpair
			
			s=locations.get(pk=s_id)
			t=locations.get(pk=t_id)
			if s.latitude is not None and t.latitude is not None and s.longitude is not None and t.longitude is not None:
			
				try:	
					sp=nx.shortest_path(G,s_id,t_id,'weight')
				except:
					sp=[s_id,t_id]
			
				if len(sp)<=2:
				
					wpa=list(edges[s_id].keys())[0]
					wpb=list(edges[t_id].keys())[0]
					
					if wpa!=wpb:
						sp=[s_id,wpa,wpb,t_id]
					else:
						sp=[s_id,wpa,t_id]
				
			
				sname=s.name
				tname=t.name
			
				waypoints=[]
			
				c=0
			
				for p_id in sp:
					l=locations.get(pk=p_id)
					waypoints.append([float(l.latitude),float(l.longitude)])				
					
					if c!=0:
						route_edge_ids.append(edges[sp[c-1]][p_id])
					c+=1
				
				route=calControlPoint_new(waypoints,route_edge_ids)
				# if badpair:
# 					print("++++",sname,tname,route)
# 				else:
# 					print(sname,tname,route)
				
				
				if badpair:
					print(s_id,t_id,route)
				
				if s_id not in routes:
					routes[s_id]={t_id:route}
				else:
					routes[s_id][t_id]=route
				
				
			#else:
				#print("lat or long is null for one of these locations:",s_id,t_id)
				## update geo_location set longitude=Null,latitude=Null where longitude<.1 and longitude>-.1 and latitude<.1 and latitude>-.1 and location_type_id<5;
			
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
			["voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__id",
			"voyage_itinerary__imp_principal_region_slave_dis__geo_location__id"
			],
			["voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__id",
"voyage_itinerary__imp_principal_port_slave_dis__geo_location__id"
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
		blank={}
		d.write(json.dumps(blank))
		d.close()
		
		def update_routes(newroutes,dataset):
			print("...adding to cache...")
			
			d=open(fpath,'r')
			t=d.read()
			routes=json.loads(t)
			d.close()
			
			if dataset not in routes:
				routes[dataset]={}
			
			n=0
			for s in routes[dataset]:
				for t in routes[dataset][s]:
					n+=1
			
			c=0
			
			if dataset not in routes:
				routes[dataset]={}
			
			for s_id in newroutes:
				for t_id in newroutes[s_id]:
					#print(s_id,t_id)
					v=newroutes[s_id][t_id]
					if s_id not in routes[dataset]:
						routes[dataset][s_id]={t_id:v}
					else:
						routes[dataset][s_id][t_id]=v
					
					#and reverse directions as well just in case?????
					
					vk=list(v.keys())
					vk.reverse()
					rv={i:v[i] for i in vk}
					if t_id not in routes[dataset]:
						routes[dataset][t_id]={s_id:rv}
					else:
						routes[dataset][t_id][s_id]=rv
					
					c+=1
			
			n=0
			
			for s in routes[dataset]:
				for t in routes[dataset][s]:
					n+=1
			
			print("total nodes post-add:", n)
			
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