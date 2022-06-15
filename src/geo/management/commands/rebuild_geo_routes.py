import itertools
from geo.models import *
from voyage.models import *
from django.db.models import Avg,Sum,Min,Max,Count,Q
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os
import re
from math import sqrt
import networkx as nx



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
		
		def make_geojson_from_adjacency_ids(fname,adj_keychain,adjacencies):

			routes_featurecollection={"type":"FeatureCollection","features":[]}

			for adj_id in adj_keychain:
				a=adjacencies.filter(**{'id':adj_id})[0]
				sv=a.source
				tv=a.target
				sv_longlat=(str(sv.longitude),str(sv.latitude))
				tv_longlat=(str(tv.longitude),str(tv.latitude))
		
				routes_featurecollection['features'].append({
					"type":"Feature",
					"geometry":{
						"type":"LineString",
						"coordinates":[sv_longlat,tv_longlat]
					},
					"properties":{}
				})
	
			print(fname)
	
			d=open(fname,'w')
			d.write(json.dumps(routes_featurecollection))
			d.close()
		
		adjacencies=Adjacency.objects.all()
		for i in ['source','target','source__location_type']:
			adjacencies=adjacencies.prefetch_related(i)
		locations=Location.objects.all()
		for i in ['location_type']:
			locations=locations.select_related(i)
		
		qobjstrs=["Q(%s='%s')" %('location_type__name',endpoint_type) for endpoint_type in ["Port","Region","Broad Region"]]
		voyage_endpoints=locations.filter(eval('|'.join(qobjstrs)))
		
		G=nx.Graph()
		
		for dataset in [0,1]:
			
			for l in locations:
				G.add_node(l.id)
			for a in adjacencies.filter(**{'dataset':dataset}):
				sv_id=a.source.id
				tv_id=a.target.id
				G.add_edge(sv_id,tv_id,edge_id=a.id)
		
			print(G)
		
			for st in itertools.combinations(voyage_endpoints,2):
				s,t=st
				print(s,t)
				if s!=t:
					s_id=s.id
					t_id=t.id
					try:
						sp=nx.shortest_path(G,s_id,t_id)
					except:
						sp=[]
					
					if len(sp)>0:
						
						adjacency_ids=[]
						
						for idx in range(1,len(sp)):
							a=sp[idx]
							b=sp[idx-1]
							e_id=G[a][b]['edge_id']
							#print(a,b,e_id)
							adjacency_ids.append(e_id)
						
						route=Route(source=s,target=t,shortest_route=json.dumps(adjacency_ids),dataset=dataset)
						route.save()
						
						#make_geojson_from_adjacency_ids('tmp/'+str(s)+'__'+str(t)+'.json',adjacency_ids,adjacencies)