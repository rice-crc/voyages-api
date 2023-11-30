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
import gc
from maps import rnconversion

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def load_graph(endpoint,graph_params):
	graphname=graph_params['name']
	print("loading network:",graphname)
	headers={'Authorization':DJANGO_AUTH_KEY}
	G=nx.DiGraph()
	if rc['type']=='oceanic':
		# FIRST, ADD THE OCEANIC NETWORK FROM THE APPROPRIATE JSON FLATFILE
		## AS POINTED TO IN THE INDEX_VARS.PY FILE
		oceanic_network_file=rc['oceanic_network_file']
		oceanic_network=rnconversion.main(oceanic_network_file)
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
		def oceanic_edge_filter(s,t):
			edgetags=G[s][t].get("tags")
			if "oceanic_leg" in edgetags or "embarkation_to_onramp" in edgetags or "offramp_to_disembarkation" in edgetags:
				return True
			else:
				return False
		oceanic_subgraph_view=nx.subgraph_view(G,filter_edge=oceanic_edge_filter)
	return G,oceanic_subgraph_view,graphname

registered_caches={
	'voyage_maps':voyage_maps,
# 	'ao_maps':ao_maps
}

#on initialization, load every index as a graph, via a call to the django api
rcnames=list(registered_caches.keys())
standoff_base=4
standoff_count=0
st=time.time()

while True:
	failures_count=0
	print('BUILDING GRAPHS')
	for rcname in rcnames:
		rc=registered_caches[rcname]
		dataframe_endpoint=rc['endpoint']
		if 'graphs' not in rc:
			rc['graphs']={}
		for graph_params in rc['graph_params']:
			try:
				graph,oceanic_subgraph_view,graphname=load_graph(dataframe_endpoint,graph_params)
				rc['graphs'][graphname]={
					'graph':graph,
					'oceanic_subgraph_view':oceanic_subgraph_view
				}
			except:
				failures_count+=1
				print("failed on cache:",rc['name'])
	print('CACHING ROUTES')
	for rcname in rcnames:
		rc=registered_caches[rcname]
		dataframe_endpoint=rc['endpoint']
# 		for graphname in ['region','place']:
		for graphname in ['region']:
			print("caching",rcname,graphname)
			graphs=rc['graphs'][graphname]
			graph=graphs['graph']
			oceanic_subgraph_view=graphs['oceanic_subgraph_view']
			
			linklabels=rc['indices']['linklabels']
			nodelabels=rc['indices']['nodelabels']
			
			oceanic_subgraph_view=rc['graphs'][graphname]['oceanic_subgraph_view']
			graph_idx=rc['indices'][graphname]
			pk_var=graph_idx['pk']
			itinerary_vars=graph_idx['itinerary']
			weight_vars=graph_idx['weight']
			graph_index=build_index(
				dataframe_endpoint,
				graph,
				oceanic_subgraph_view,
				pk_var,
				itinerary_vars,
				weight_vars,
				linklabels,
				nodelabels
			)
			rc['graphs'][graphname]['index']=graph_index
			del(rc['graphs'][graphname]['graph'])
	print("failed on %d of %d caches" %(failures_count,len(rcnames)))
	if failures_count>=len(rcnames):
		standoff_time=standoff_base**standoff_count
		print("retrying after %d seconds" %(standoff_time))
		time.sleep(standoff_time)
		standoff_count+=1
	else:
		break
print("finished building graphs in %d seconds" %int(time.time()-st))




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
	cachename=rdata['cachename']
	graphname=rdata['graphname']
	pks=rdata['pks']
	
	#first we get our index, which consists of the full weighted routes
	#keyed to each entity, whether that be a voyage or an enslaved person
	
	routes_index=registered_caches[cachename]['graphs'][graphname]['index']
	
	#then we subset the index (which are nodes and paths)
	#according to the entities that have been requested
	routes_subset=[routes_index[pk] for pk in pks]
	
	#now we add up the various weights of each node
	#this is super fast
	st=time.time()
	aggregated_nodes={}
	for r in routes_subset:
		for n_id in r['nodes']:
			node=r['nodes'][n_id]
			if n_id in aggregated_nodes:
				for wk in node['weights']:
					aggregated_nodes[n_id]['weights'][wk]+=node['weights'][wk]
			else:
				aggregated_nodes[n_id]=node
	nodesflat=[aggregated_nodes[n_id] for n_id in aggregated_nodes]
	print("time aggregating nodes:",time.time()-st)
	
	#edges, however, remain tricky
	
	paths_subset=[r['edges'] for r in routes_subset]
	#first we aggregate the weights and gather the control points
	st=time.time()
	aggregated_paths={}
	for path in paths_subset:
		for s in path:
			for t in path[s]:
				edge=path[s][t]
				edgecontrols=edge['controls']
				edgeweight=edge['weight']
				if s in aggregated_paths:
					if t in aggregated_paths[s]:
						aggregated_paths[s][t]['weight']+=edgeweight
						aggregated_paths[s][t]['controls'].append(
							{
								'weight':edgeweight,
								'control':edgecontrols
							}
						)
					else:
						edge['controls']=[
							{
								'weight':edgeweight,
								'control':edgecontrols
							}
						]
						aggregated_paths[s][t]=edge
				else:
					edge['controls']=[
						{
							'weight':edgeweight,
							'control':edgecontrols
						}
					]
					aggregated_paths[s]={t:edge}
	print("aggregating edge weights time:",time.time()-st)
	del(paths_subset)
	st = time.time()
	edgesflat=[]
	for s in aggregated_paths:
		for t in aggregated_paths[s]:
			edge=aggregated_paths[s][t]
			thisedge={'source':s,'target':t,'weight':edge['weight'],'type':edge['type']}
			if 'controls' in edge:
				final_edge=weightedaverage_tuple(edge['controls'])
				thisedge['controls']=final_edge
			edgesflat.append(thisedge)
	print("flattening & control weighted averages time:",time.time()-st)
	
	outputs= {'nodes':nodesflat,'edges':edgesflat}
	
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