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
	
	for groupby_pair in groupby_pairs:
		print("vars",groupby_pair)
	
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
		
		#print("unique a/b pairs",len(abpairs))
		
		#now find shortest path in the network for each unique alice/bob pair
		
		#routes={}
		
		print("finding routes")
		for abpair in abpairs:
			s_id,t_id=abpair
			try:
				sp=nx.shortest_path(G,s_id,t_id)
			
				edge_ids=[]
				for idx in range(1,len(sp)):
						a=sp[idx]
						b=sp[idx-1]
						e_id=G[a][b]['edge_id']
						edge_ids.append(e_id)
			except:
				print('error w following nodes -- drawing a straight line',s_id,t_id)
				edge_ids=[]
			
			source_location=locations.filter(**{'id':s_id})[0]
			target_location=locations.filter(**{'id':t_id})[0]
			
			route=Route(source=source_location,target=target_location,dataset=dataset,shortest_route=json.dumps(edge_ids))
			route.save()




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
		imp_begin=[
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
				groupby_pairs.append([a,b])
		
		#pp.pprint(groupby_pairs)
		
		#and of course we need to separate the datasets' for voyages and adjacencies
		datasets=[0,1]
		
		#for each of those paired variables, we're going to need the unique tuple values for each voyage
		##i don't THINK we need to do this for people, as their itineraries are based on voyages but i could be wrong...
		
		url='http://voyages-django:8000/voyage/dataframes'

		for dataset in datasets:
			make_networks(dataset,groupby_pairs,url)
		
		##NOW DO INLAND IAM ENSLAVED GROUPBY PAIRS
		
		url='http://voyages-django:8000/past/enslaved/dataframes'
		
		groupby_pairs=[
			[
				'post_disembark_location__geo_location__id',
				'voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__id'
			]
		]
		
		make_networks(0,groupby_pairs,url,extra_search_params={'id':[1,499999]})
		make_networks(1,groupby_pairs,url,extra_search_params={'id':[500000,1000000]})
		
		
		print("finished in %d minutes" %int((time.time()-st)/60))