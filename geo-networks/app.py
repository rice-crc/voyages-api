import time
from flask import Flask,jsonify,request,abort
import json
import math
import requests
from localsettings import *
from index_vars import *
from utils import *
import networkx as nx
from networkx_query import search_nodes, search_edges
import re
from maps import rnconversion

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def load_graph(endpoint,graph_params):
	graph_name=graph_params['name']
	print("loading network:",graph_name)
	headers={'Authorization':DJANGO_AUTH_KEY}
	G=nx.DiGraph()
	if rc['type']=='oceanic':
		# FIRST, ADD THE OCEANIC NETWORK FROM THE APPROPRIATE JSON FLATFILE
		## AS POINTED TO IN THE INDEX_VARS.PY FILE
		oceanic_network_file=rc['oceanic_network_file']
		oceanic_network=rnconversion.main(oceanic_network_file)
# 		d=open(oceanic_network_file,'r')
# 		t=d.read()
# 		d.close()
# 		oceanic_network=json.loads(t)
		G,max_node_id=add_oceanic_network(G,oceanic_network,init_node_id=0)
		print("created oceanic network",G)
		# THEN ITERATE OVER THE GEO VARS IN THE INDEX
		## AND ADD THE RESULTING UNIQUE NODES TO THE NETWORK
		filter_obj=rc['filter']
		G,max_node_id=add_non_oceanic_nodes(G,endpoint,graph_params,filter_obj,init_node_id=max_node_id+1)
		print("added non-oceanic network nodes")
		#then link across the ordered node classes
		ordered_node_classes=graph_params['ordered_node_classes']
		prev_tag=None
		for ordered_node_class in ordered_node_classes:
			tag=ordered_node_class['tag']
			if 'tag_connections' in ordered_node_class:
				tag_connections=ordered_node_class['tag_connections']
				G=connect_to_tags(G,tag,tag_connections)
		print("connected all remaining network edges (non-oceanic --> (non-oceanic & oceanic)) following index_vars.py file ruleset")
	elif rc['type']=='people':
		pass
	return G,graph_name,None

registered_caches={
	'voyage_maps':voyage_maps,
	'ao_maps':ao_maps
}

#on initialization, load every index as a graph, via a call to the django api
rcnames=list(registered_caches.keys())
standoff_base=4
standoff_count=0
st=time.time()

while True:
	failures_count=0
	for rcname in rcnames:
		rc=registered_caches[rcname]
		endpoint=rc['endpoint']
		if 'graphs' not in rc:
			rc['graphs']={}

		for graph_params in rc['graph_params']:
			try:
				graph,graph_name,shortest_paths=load_graph(endpoint,graph_params)
				rc['graphs'][graph_name]={
					'graph':graph,
					'shortest_paths':shortest_paths
				}
			except:
				failures_count+=1
				print("failed on cache:",rc['name'])
				break
		registered_caches[rcname]=rc
	print("failed on %d of %d caches" %(failures_count,len(rcnames)))
	if failures_count==len(rcnames):
		standoff_time=standoff_base**standoff_count
		print("retrying after %d seconds" %(standoff_time))
		time.sleep(standoff_time)
		standoff_count+=1
	else:
		break
# print("finished building graphs in %d seconds" %int(time.time()-st))

def add_stripped_node_to_dict(graph,n_id,nodesdict):
	node=dict(graph.nodes[n_id])
	if 'uuid' in node:
		#if it has a uuid from the database
		#then its id will be like b3199d76-bf58-40fb-8eeb-be3986df6113
		n_uuid=node['uuid']
	else:
		#else, its id in the nodesdict is the string representation
		#of its id in the networkx graph, which was assigned at service instantiation
		#as an auto-increment
		n_uuid=str(n_id)
	if 'tags' in node:
		del node['tags']
	nodesdict[n_uuid]['data']=node
	return nodesdict

@app.route('/network_maps/',methods=['POST'])
def network_maps():
	
	'''
	Accepts itineraries of UUID's with weights attached
	Returns weighted and classed nodes and edges
	'''
	
	st=time.time()
	rdata=request.json
	
	
	# I'd like to unite the different caches
	## all we * really * need is a single oceanic network to plug everything into
	cachename=rdata['cachename']
	# 1-level kvpair dict in the form of
	## keys: double-underscored node uuid's of length N (with "None" as the null value)
	## values: integers
	## e.g. "None__b3199d76-bf58-40fb-8eeb-be3986df6113__6e66dc3f-b124-446d-ba28-dee1f3e1fe6b__6e66dc3f-b124-446d-ba28-dee1f3e1fe6b": 404,
	payload=rdata['payload']
	# linklabels are an array (length N-1)
	## that classify the edges
	## e.g., in the AO map, ['origination','transportation','disposition']
	## NOTE -- "TRANSPORTATION" IS SPECIAL
	## IT EXPANDS THE PATH BY TRAVERSING THE OCEANIC NETWORK (IF THE GRAPH WAS BUILT PROPERLY)
	## AND ON SELF-LOOPS IT ENTERS INTO THE OCEANIC NETWORK AND THEN FINDS A PATH BACK
	linklabels=rdata['linklabels']
	# nodelabels are N long
	nodelabels=rdata['nodelabels']
	## and classify the nodes
	graphname=rdata['graphname']
	graph=registered_caches[cachename]['graphs'][graphname]['graph']
	
	
	##somebody help me -- is there a faster pythonic way to do this?
	nodes={i:{
		"id":i,
		"weights":{
			nl:0 for nl in nodelabels
		},
		"data":{}
		} for k in payload for i in k.split('__') if i != "None"
	}
	
	paths=[]
	
	edges={}
	
	#iterate over the paths
	for k in payload:
		weight=payload[k]
		uuids=k.split('__')
		# because, for now, the paths are all the same length, N, e.g.
		## people: [origin,embarkation,disembarkation,disposition]
		## voyages: [embarkation,disembarkation]
		# and each (nullable) position in the path carries semantic value
		# to apply the weight of this path across all the affected nodes
		# while retaining that semantic value
		for idx in range(len(uuids)):
			uuid=uuids[idx]
			if uuid not in [None,'None']:
				nodelabel=nodelabels[idx]
				nodes[uuid]['weights'][nodelabel]+=weight
		#similarly for linklabels, which are N-1 long
		abpairs=[(uuids[i],uuids[i+1]) for i in range(len(uuids)-1)]
		thispath={"nodes":[],"weight":weight}
# 		print("abpairs",abpairs)
		for idx in range(len(linklabels)):
			abpair=abpairs[idx]
			linklabel=linklabels[idx]
# 			print(abpair)
			if "None" in abpair or None in abpair:
				#if we hit a break in the path then we want to reset
				#but still record the discontinuous segments
				if len(thispath['nodes'])>0:
					paths.append(thispath)
					thispath={"nodes":[],"weight":weight}
			else:
				a_uuid,b_uuid=abpair
				amatch=next(iter([n for n in search_nodes(graph,{"==":["uuid",a_uuid]})]),None)
				bmatch=next(iter([n for n in search_nodes(graph,{"==":["uuid",b_uuid]})]),None)
# 				print("A",a_uuid,amatch)
# 				print("B",b_uuid,bmatch)
				#the db can still return path node uuid's for places that don't have good geo data (nulled or zeroed lat/long)
				#so we have to screen those out, as they have been excluded from the networkx graph db
				if amatch is not None and bmatch is not None:
					a_id=amatch
# 					if len(thispath['nodes'])==0:
# 						thispath['nodes'].append(a_uuid)
					b_id=bmatch
# 					print("-->",a_id,b_id)
					nodes=add_stripped_node_to_dict(graph,a_id,nodes)
					nodes=add_stripped_node_to_dict(graph,b_id,nodes)
					
# 					print(nodes)
					
					#get the shortest path from a to b, according to the graph
					
					#but also handle transportation self-loops...
					spfail=False
					selfloop=False
					if a_id==b_id and linklabel=='transportation':
						#transportation self-loop
						selfloop=True
						successor_ids=[
							n_id for n_id in graph.successors(a_id)
							if 'onramp' in graph.nodes[n_id]['tags']
						]
						if len(successor_ids)==0:
							spfail=True
						else:
							successor_id=successor_ids[0]
					else:
						selfloop=False
					
					if not spfail:
						try:
							if selfloop:
								sp=nx.shortest_path(graph,successor_id,b_id,'distance')
								sp.insert(0,a_id)
							else:
								sp=nx.shortest_path(graph,a_id,b_id,'distance')
						except:
							spfail=True
					
					#if all our shortest path work has failed, then return a straight line
					## but log it!
					if spfail:
						print("---\nNO PATH")
						print("from",amatch,graph.nodes[amatch])
						print("to",bmatch,graph.nodes[bmatch]," -- drawing straight line.\n---")
						sp=[a_id,b_id]
					
					#retrieve the uuid's where applicable
					sp_export=[graph.nodes[x]['uuid'] if 'uuid' in graph.nodes[x] else x for x in list(sp)]
# 					print("spexport",sp_export)
					#update the full path with this a, ... , b walk we've just performed
					#after trimming the first entry in this walk ** if this is not our first walk
					#otherwise, we get overlaps / false self-loops in our path
					#this crops up in paths that are more than 1 hop long
					if len(thispath['nodes'])>0:
						if thispath['nodes'][-1]==sp_export[0]:
							thispath['nodes']+=sp_export[1:]
					else:
						thispath['nodes']+=sp_export
					
					#update the nodes dictionary with any new nodes
					for n_id in sp_export:
						if n_id not in nodes:
							newnode_data=dict(graph.nodes[n_id])
							nodes[str(n_id)]={
								'data':newnode_data,
								'id':n_id,
								'weights':{}
							}
					#update the edges dictionary with this a, ..., b walk data
					sp_DC_pairs=[(sp_export[i],sp_export[i+1]) for i in range(len(sp_export)-1)]
					for sp_DC_pair in sp_DC_pairs:
						s,t=[str(i) for i in sp_DC_pair]
						if s not in edges:
							edges[s]={t:{
								'weight':weight,
								'type':linklabel,
								'source':s,
								'target':t
							}}
						elif t not in edges[s]:
							edges[s][t]={
								'weight':weight,
								'type':linklabel,
								'source':s,
								'target':t
							}
						else:
							edges[s][t]['weight']+=weight
						
# 						
# 						sp_DC_pair_key='__'.join([str(i) for i in sp_DC_pair])
# 						
# 						
# 						
# 						if sp_DC_pair_key in edges:
# 							edges[sp_DC_pair_key]['weight']+=weight
# 						else:
# 							edges[sp_DC_pair_key]={
# 								'weight':weight,
# 								'type':linklabel,
# 								'source':str(sp_DC_pair[0]),
# 								'target':str(sp_DC_pair[1])
# 							}
		if len(thispath['nodes'])>0:
			paths.append(thispath)
			thispath={"nodes":[],"weight":weight}
			
	splined=True
	
	if splined:
		edges=spline_curves(nodes,edges,paths,graph)
	
	edgesvals=[edges[k] for k in edges]
	
	edgesflat=[]
	for s in edges:
		for t in edges[s]:
			edge=edges[s][t]
			thisedge={'source':s,'target':t,'weight':edge['weight'],'type':edge['type']}
			if 'controls' in edge:
				thisedge['controls']= edge['controls']
			edgesflat.append(thisedge)
	outputs={
		"nodes":[nodes[k] for k in nodes],
		"edges":edgesflat,
		"paths":paths
	}
	
	return jsonify(outputs)

#GEOJSON
@app.route('/simple_map/<cachename>',methods=['GET'])
# @app.route('/simple_map',methods=['GET'])
def simple_map(cachename):

	st=time.time()
	cachegraphs=registered_caches[cachename]['graphs']
	
	resp=[]
	for graphname in cachegraphs:
		featurecollection={
			"type": "FeatureCollection",
			"features": [
			]
		}
		graphcachedict=cachegraphs[graphname]
		graph=graphcachedict['graph']	
		features=[]
		for n in graph.nodes:
			node=(graph.nodes[n])
# 			print(node)
			feature={
				"type": "Feature",
				"properties": {},
				"geometry": {
					"coordinates": [],
					"type": "Point"
				}
			}
			feature['properties']['name']=node['name']

			if 'lat' in node and 'lon' in node:
				lat=node['lat']
				lon=node['lon']
				if lat is not None and lon is not None:
					feature['geometry']['coordinates']=[
						float(lon),
						float(lat)
					]
					if 'uuid' in node:
						feature['properties']['uuid']=node['uuid']
					if 'tags' in node:
						feature['properties']['tags']=node['tags']
					featurecollection['features'].append(feature)
		for e in graph.edges:
			feature={
			  "type": "Feature",
			  "properties": {},
			  "geometry": {
				"coordinates": [],
				"type": "LineString"
			  }
			}
			s_id,t_id=e
			edge=graph.edges[[s_id,t_id]]
# 			print(edge)
			edge_id=edge['id']
			edge_tags=edge['tags']
			s=graph.nodes[s_id]
			t=graph.nodes[t_id]
			s_coords=[s['lon'],s['lat']]
			t_coords=[t['lon'],t['lat']]
			feature['geometry']['coordinates']=[s_coords,t_coords]
			feature['properties']['tags']=edge_tags
			feature['properties']['id']=edge_id
			featurecollection['features'].append(feature)
		resp.append(featurecollection)
		d=open("tmp/%s__%s.json" %(cachename,graphname),'w')
		d.write(json.dumps(featurecollection))
		d.close()
	print("Internal Response Time:",time.time()-st,"\n+++++++")
	return jsonify(resp)