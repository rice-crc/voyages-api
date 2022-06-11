from geo.models import *
from voyage.models import *
from django.db.models import Avg,Sum,Min,Max,Count,Q
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os
import re
from math import sqrt

class Command(BaseCommand):
	help = '\
		# Given a flat routes file in the legacy sv format of https://github.com/rice-crc/voyages/blob/develop/voyages/sitemedia/maps/js/routeNodes.js \
		# This script will \
		## first: wipe out all adjacencies and Oceanic Waypoint type objects from the db \
		## second: extract the network\'s nodes and edges \
		### And then write those to the new geo app in the format of \
		### node --> Location with lat, long, and location type of "Oceanic Waypoint" \
		### edge --> adjacency btw source and target \
		## third: connect each port location to its closest Oceanic Waypoint neighbor \
		### using euclidean distance here, which obvs has issues \
	'
	def handle(self, *args, **options):
		base_path='geo/management/commands/'
		
		#oceanic waypoint location codes will be very, very high to avoid collisions
		newlocationcode=1000000000
		
		networks={
			"iam":{
				"fname":"intra_am_routeNodes.js",
				"dataset":0
			},
			"tatl":{
				"fname":"trans_atl_routeNodes.js",
				"dataset":1
			}
		
		}
		locations=Location.objects.all()

		print('+++++++++++++++++\ndeleting all existing oceanic waypoints')
		oceanic_waypoints=locations.filter(**{'location_type__name':'Oceanic Waypoint'})
		for oceanic_waypoint in oceanic_waypoints:
			#print("deleting:",oceanic_waypoint.name,oceanic_waypoint.id)
			oceanic_waypoint.delete()
		

		print('+++++++++++++++++\ndeleting all existing edges in the graph')
		## clear out all adjacencies
		adjacencies=Adjacency.objects.all()
		locations=Location.objects.all()
		
		
	
		for adjacency in adjacencies:
			#print("deleting",adjacency)
			adjancency.delete()
		
		for network_name in networks:
			c=0
			print("\n\n++++++++++++++++",network_name,"++++++++++++++++")
			network=networks[network_name]
			network_fname=network['fname']
			dataset=network['dataset']
			
			d=open(os.path.join(base_path,network_fname),'r')
			t=d.read()
			d.close()

			groups=re.findall("\[.*?\]",t,re.S)

			nodes_block=groups[0]
			edges_block=groups[1]

			routenodes_coordinates=[eval(i) for i in re.findall("\([-|0-9|.]+.*?[-|0-9|.]+\)",nodes_block)]

			route_edges=[(int(i[0]),int(i[1])) for i in re.findall("([0-9]+).*?([0-9]+)",edges_block)]

			routes_featurecollection={"type":"FeatureCollection","features":[]}

			print(len(route_edges),"edges")
			print(len(routenodes_coordinates),"nodes")
		
			#for a quick visualization you can use the geoson file dumped out here.
			#in the future, this should have 2 options: first, to load it from routes.js
			#but second, to load it from the sort of geojson I'm outputting below
			for edge in route_edges:
				sv,tv=edge
				sv_latlong=routenodes_coordinates[sv]
				sv_longlat=(sv_latlong[1],sv_latlong[0])
				tv_latlong=routenodes_coordinates[tv]
				tv_longlat=(tv_latlong[1],tv_latlong[0])
				routes_featurecollection['features'].append({
					"type":"Feature",
					"geometry":{
						"type":"LineString",
						"coordinates":[sv_longlat,tv_longlat]
					},
					"properties":{}
				})
	
			d=open(os.path.join(base_path,'extracted_network_%s.json' %network_name),'w')
			d.write(json.dumps(routes_featurecollection))
			d.close()
		
			location_types=LocationType.objects.all()
				
			print("+++++++\nlocation types")
			for location_type in location_types:
				print(location_type.name,location_type.id)
			
			oceanic_waypoint_location_type=location_types.filter(**{'name':'Oceanic Waypoint'})[0]
		
			routenode_js_to_db_map={}
			
			print('+++++++\nhighways: creating new oceanic waypoints and edges based on %s oceanic graph (routeNodes.js)' %network_name)
			print('--->oceanic waypoints')
			
			for routenode in routenodes_coordinates:
			
				latitude,longitude=routenode
			
				payload={
					"longitude":longitude,
					"latitude":latitude
				}
			
				#print("creating",payload)
			
				location=Location(name="ocean waypt %d" %newlocationcode,longitude=longitude,latitude=latitude,location_type=oceanic_waypoint_location_type,value=newlocationcode,dataset=dataset)
			
				newlocationcode+=1
			
				location.save()
			
				locations=Location.objects.all()
			
				new_location_id=locations.aggregate(Max('id'))['id__max']
			
				routenode_js_to_db_map[c]=new_location_id
			
				c+=1
		
		
			print('--->oceanic network')
			## Using a trick here that will make route-finding super easy
			## At the cost of making this an undirected network
			for routeedge in route_edges:
				sv=min(routeedge)
			
				tv=max(routeedge)
			
				sv_k=routenode_js_to_db_map[sv]
			
				source_location=locations.filter(**{"id":sv_k})[0]
			
				tv_k=routenode_js_to_db_map[tv]
			
				target_location=locations.filter(**{"id":tv_k})[0]
			
				#print("creating",source_location,target_location)
			
				adjacency=Adjacency(source=source_location,target=target_location,dataset=dataset)
				adjacency.save()
		
		
			locations=Location.objects.all()
			
			
			print('+++++++\non-ramps: connecting ports, regions, and broad regions to oceanic waypoint network')
			
			location_types_names=["Port","Region","Broad Region"]
			
			for location_type_name in location_types_names:
				print('--->%ss' %location_type_name)
				location_type=location_types.filter(**{'name':location_type_name})[0]
		
				these_locations=locations.filter(**{'location_type':location_type,'show_on_voyage_map':1})
		
				waypoint_location_type=location_types.filter(**{'name':'Oceanic Waypoint'})[0]
		
				waypoints=locations.filter(**{'location_type':waypoint_location_type,'dataset':dataset})
		
				for location in these_locations:
					if location.longitude!=None and location.latitude!= None:
						distances=[(sqrt((location.longitude-waypoint.longitude)**2+(location.latitude-waypoint.latitude)**2),waypoint) for waypoint in waypoints]
						closest_neighbor=sorted(distances, key=lambda tup: tup[0])[0][1]
						#print("linking",location,"to",closest_neighbor)
						if location.id < closest_neighbor.id:
							source=location
							target=closest_neighbor
						else:
							source=closest_neighbor
							target=location
						adjacency=Adjacency(source=source,target=target,dataset=dataset)
						adjacency.save()