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
import pandas as pd
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
# 		for node in graph.nodes:
# 			print(node)
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
# 			try:
			graph,oceanic_subgraph_view,graphname=load_graph(dataframe_endpoint,graph_params)
# 				rc['graphs'][graphname]={
# 					'graph':graph,
# 					'oceanic_subgraph_view':oceanic_subgraph_view
# 				}
# 			except:
# 				failures_count+=1
# 				print("failed on cache:",rc['name'])
# 	print('CACHING ROUTES')
# 	for rcname in rcnames:
# 		rc=registered_caches[rcname]
# 		dataframe_endpoint=rc['endpoint']
# # 		for graphname in ['region','place']:
# 		for graphname in ['region']:
# 			print("caching",rcname,graphname)
# 			graphs=rc['graphs'][graphname]
# 			graph=graphs['graph']
# 			oceanic_subgraph_view=graphs['oceanic_subgraph_view']
			linklabels=rc['indices']['linklabels']
			nodelabels=rc['indices']['nodelabels']
# 			oceanic_subgraph_view=rc['graphs'][graphname]['oceanic_subgraph_view']
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
			if graphname not in rc['graphs']:
				rc['graphs'][graphname]={'index':graph_index}
			else:	
				rc['graphs'][graphname]['index']=graph_index
	print("failed on %d of %d caches" %(failures_count,len(rcnames)))
	if failures_count>=len(rcnames):
		standoff_time=standoff_base**standoff_count
		print("retrying after %d seconds" %(standoff_time))
		time.sleep(standoff_time)
		standoff_count+=1
	else:
		break
print("finished building graphs in %d seconds" %int(time.time()-st))


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
	
	nodes=registered_caches[cachename]['graphs'][graphname]['index']['nodes']
	edges=registered_caches[cachename]['graphs'][graphname]['index']['edges']
	nodesdata=registered_caches[cachename]['graphs'][graphname]['index']['nodesdata']
	edgesdata=registered_caches[cachename]['graphs'][graphname]['index']['edgesdata']
	
	aggnodes=nodes[nodes['pk'].isin(pks)].drop(columns=(['pk'])).groupby('id').agg('sum')
	
	finalnodes=[
		{	
			'id':row_id,
			'data':nodesdata[row_id],
			'weights':{
				'origin':row['origin'],
				'embarkation':row['embarkation'],
				'disembarkation':row['disembarkation'],
				'post-disembarkation':row['post-disembarkation']
			}
		}
		for row_id,row in aggnodes.iterrows()
		##nodes that i screened out for lack of good lat/lng are reappearing and breaking this iterator?
		if 'lat' in nodesdata[row_id]
	]
	
# 	totalweight=sum(edges[edges['pk'].isin(pks)][['pk','weight']].groupby('pk').agg('mean')['weight'].to_list())
	
	print(edges)
	aggedges=edges.copy()
	
	aggedges['c1x']=aggedges['c1x']*aggedges['weight']
	aggedges['c2x']=aggedges['c2x']*aggedges['weight']
	aggedges['c1y']=aggedges['c1y']*aggedges['weight']
	aggedges['c2y']=aggedges['c2y']*aggedges['weight']
	
	aggedges=aggedges.drop(columns=(['pk'])).groupby(['source','target']).agg('sum').reset_index()
	
	print(aggedges[['weight','c1x']])
	
	aggedges['c1x']=aggedges['c1x']/aggedges['weight']
	aggedges['c2x']=aggedges['c2x']/aggedges['weight']
	aggedges['c1y']=aggedges['c1y']/aggedges['weight']
	aggedges['c2y']=aggedges['c2y']/aggedges['weight']
	
	print(aggedges[['weight','c1x']])
	
	finaledges=[
		{
			'source':row['source'],
			'target':row['target'],
			'weight':edgesdata['__'.join([str(row['source']),str(row['target'])])]['weight'],
			'controls':[[row['c1x'],row['c1y']],[row['c2x'],row['c2y']]],
			'type':edgesdata['__'.join([str(row['source']),str(row['target'])])]['type']
		} for row_id,row in aggedges.iterrows()
	]
	
	return(jsonify({'nodes':finalnodes,'edges':finaledges}))

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