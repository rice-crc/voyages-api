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
		
		#HARD CODED DATASETS INDICES
		## 1 = iam
		## 2 = tast
		##THESE FILES ARE MADE IN THE LEGACY MAP NETWORK EDITOR
		##SO THIS IS COMPATIBLE WITH SOME OF THE OLD MIDDLEWARE
		networks=[
			{	"name":"iam",
				"fname":"intra_am_routeNodes.js",
				"dataset":1
			},
			{	"name":"tatl",
				"fname":"trans_atl_routeNodes.js",
				"dataset":0
			}
		]
		
		locations=Location.objects.all()
		
		## DELETE ALL EXISTING WAYPOINTS
		print('+++++++++++++++++\ndeleting all existing oceanic waypoints')
		oceanic_waypoints=locations.filter(**{'location_type__name':'Oceanic Waypoint'})
		for oceanic_waypoint in oceanic_waypoints:
			oceanic_waypoint.delete()
		

		print('+++++++++++++++++\ndeleting all existing edges in the graph')
		## DELETE ALL EXISTING ADJACENCIES
		adjacencies=Adjacency.objects.all()
		locations=Location.objects.all()
		
		for adjacency in adjacencies:
			adjacency.delete()
		
		#REBUILD THE "HIGHWAYS"
		#THESE ARE THE WAYPOINT NETWORKS
		for network in networks:
			c=0
			network_name=network['name']
			network_fname=network['fname']
			dataset=network['dataset']
			print("\n\n++++++++++++++++",network_name,"++++++++++++++++")
			
			#LOAD NETWORK FROM JS FILE
			d=open(os.path.join(base_path,network_fname),'r')
			t=d.read()
			d.close()
			
			#ERIK ENGQUIST: "WHEN YOU SOLVE A PROBLEM WITH REGULAR EXPRESSIONS, YOU HAVE TWO PROBLEMS"
			##IN OTHER WORDS THIS COULD BE DONE BETTER. I'M PARSING IT AS A TEXT FILE INSTEAD OF READING THE JS IN PYTHON
			groups=re.findall("\[.*?\]",t,re.S)
			nodes_block=groups[0]
			edges_block=groups[1]
			#NODES ARE EXPRESSED AS AN ARRAY OF LATLONG DECIMAL PAIRS
			routenodes_coordinates=[eval(i) for i in re.findall("\([-|0-9|.]+.*?[-|0-9|.]+\)",nodes_block)]
			#EDGES ARE EXPRESSED AS SOURCE,TARGET ("START","END") PAIRS
			#WHERE THE VALUES ARE INDICES IN THE NODE ARRAY (ABOVE)
			route_edges=[(int(i[0]),int(i[1])) for i in re.findall("([0-9]+).*?([0-9]+)",edges_block)]
			
			#for a quick visualization/sanity check you can use the geoson file dumped out here.
			#in the future, this should have 2 options: first, to load it from routes.js
			#but second, to load it from the sort of geojson I'm outputting below
			routes_featurecollection={"type":"FeatureCollection","features":[]}
			print(len(route_edges),"edges")
			print(len(routenodes_coordinates),"nodes")
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
			
			#NOW WE GET DOWN TO BUSINESS.
			########
			#0. GET THE TYPE FOR OCEANIC WAYPOINTS SO THESE CAN BE CODED PROPERLY
			location_types=LocationType.objects.all()
			print("+++++++\nlocation types")
			for location_type in location_types:
				print(location_type.name,location_type.id)
			oceanic_waypoint_location_type=location_types.filter(**{'name':'Oceanic Waypoint'})[0]
			
			# 1. CREATE OCEANIC WAYPOINTS IN DB BASED ON JS FILE NODES
			
			## and along the way save the index of each node from the js file
			## because the edges' source/target values are keyed against these indices
			routenode_js_to_db_map={}
			print('+++++++\nhighways: creating new oceanic waypoints and edges based on %s oceanic graph (%s)' %(network_name,network_fname))
			print('--->oceanic waypoints')
			for routenode in routenodes_coordinates:
				latitude,longitude=routenode
				payload={
					"longitude":longitude,
					"latitude":latitude
				}
				location=Location(name="ocean waypt %d" %newlocationcode,longitude=longitude,latitude=latitude,location_type=oceanic_waypoint_location_type,value=newlocationcode,dataset=dataset)
				newlocationcode+=1
				location.save()
				locations=Location.objects.all()
				new_location_id=locations.aggregate(Max('id'))['id__max']
				routenode_js_to_db_map[c]=new_location_id
				c+=1
			
			print('--->oceanic network')
			# 2. CONNECT OCEANIC WAYPOINTS IN DB BASED ON JS FILE EDGES
			
			## using a trick here that will make route-finding super easy
			## at the cost of making this an undirected network
			## i.e., the "source" is always the node with the lower pk
			for routeedge in route_edges:
				sv,tv=routeedge
				sv_k=routenode_js_to_db_map[sv]
				source_location=locations.filter(**{"id":sv_k})[0]
				tv_k=routenode_js_to_db_map[tv]
				target_location=locations.filter(**{"id":tv_k})[0]
				source_lat=source_location.latitude
				source_long=source_location.longitude
				target_lat=target_location.latitude
				target_long=target_location.longitude
				distance=sqrt((target_lat-source_lat)**2+(target_long-source_long)**2)
				adjacency=Adjacency(
					source=source_location,
					target=target_location,
					dataset=dataset,
					distance=distance)
				adjacency.save()
			
			# 3. CONNECT NON-WAYPOINTS TO THESE OCEANIC NETWORKS
			
			## a. we run through all the ports, regions, and broad regions
			## b. then IN THAT DATASET (IAM OR TAST) we find the closest waypoint
			### --> note: currently just using euclidean distance. not technically correct.
			## c. and create an adjacency between these. i'm calling these "on-ramps" and "off-ramps"
			# so the result is that each region, broad region, and port will have an adjacency to each oceanic network
			locations=Location.objects.all()
			print('+++++++\non-ramps: connecting ports, regions, and broad regions to oceanic waypoint network')
			location_types_names=["Port","Region","Broad Region"]
			waypoint_location_type=location_types.filter(**{'name':'Oceanic Waypoint'})[0]
			for location_type_name in location_types_names:
				print('--->%ss' %location_type_name)
				location_type=location_types.filter(**{'name':location_type_name})[0]
				these_locations=locations.filter(**{'location_type':location_type})
				
				
				
				waypoints=locations.filter(
					**{'location_type':waypoint_location_type,'dataset':dataset}
				)
		
				for location in these_locations:
					
					# if location.id in [3227,2799,3470,2823,3415]:
# 						print("BAD NODES!!!",location,location.id)
					
					if location.longitude!=None and location.latitude!= None:

						distances=[
							(
								sqrt(
									(location.longitude-waypoint.longitude)**2+
									(location.latitude-waypoint.latitude)**2
								),waypoint
							) 
							for waypoint in waypoints
							]
						closest_neighbor=sorted(distances, key=lambda tup: tup[0])[0][1]
						distance=min([i[0] for i in distances])
						
						
						#if location.id in [3227,2799,3470,2823,3415]:
# 							print(closest_neighbor)
						
						
						##create an on ramp and an off ramp
						
						adjacency=Adjacency(
							source=location,
							target=closest_neighbor,
							dataset=dataset,
							distance=distance
						)
						
						adjacency.save()
						
						adjacency=Adjacency(
							source=closest_neighbor,
							target=location,
							dataset=dataset,
							distance=distance
						)
						
						adjacency.save()
				