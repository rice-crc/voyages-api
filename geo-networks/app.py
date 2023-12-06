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
import pickle
import os
import pandas as pd

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

registered_caches={
	'ao_maps':ao_maps,
	'voyage_maps':voyage_maps
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
			graphname=graph_params['name']
			picklefilepath='tmp/%s__%s.pickle' %(rcname,graphname)
			
			if os.path.exists(picklefilepath):
				with open(picklefilepath, 'rb') as f:
					graph_index = pickle.load(f)
			else:
				graph,oceanic_subgraph_view,graphname=load_graph(dataframe_endpoint,graph_params,rc)
				linklabels=rc['indices']['linklabels']
				nodelabels=rc['indices']['nodelabels']
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
				with open(picklefilepath, 'wb') as f:
					pickle.dump(graph_index, f, pickle.HIGHEST_PROTOCOL)
			
			if graphname not in rc['graphs']:
				rc['graphs'][graphname]={'index':graph_index}
			else:	
				rc['graphs'][graphname]['index']=graph_index
# 			except:
# 				failures_count+=1
# 				print("failed on cache:",rc['name'])
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
	aggedges=registered_caches[cachename]['graphs'][graphname]['index']['edges'].copy()
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
		if row_id in nodesdata
	]
	
	
	for node in finalnodes:
		if 'name' in node['data']:
			if node['data']['name']=="Sierra Leone":
				print(node)
	
	
	## HAVE TO DROP EDGES WHERE WEIGHT IS ZERO BEFORE I DO THE BELOW:
	
	aggedges=aggedges[aggedges['weight']>0]
	
	aggedges['c1x']=aggedges['c1x']*aggedges['weight']
	aggedges['c2x']=aggedges['c2x']*aggedges['weight']
	aggedges['c1y']=aggedges['c1y']*aggedges['weight']
	aggedges['c2y']=aggedges['c2y']*aggedges['weight']
	
	aggedges=aggedges.drop(columns=(['pk'])).groupby(['source','target']).agg('sum').reset_index()
	
	aggedges['c1x']=aggedges['c1x']/aggedges['weight']
	aggedges['c2x']=aggedges['c2x']/aggedges['weight']
	aggedges['c1y']=aggedges['c1y']/aggedges['weight']
	aggedges['c2y']=aggedges['c2y']/aggedges['weight']
	
	finaledges=[
		{
			'source':row['source'],
			'target':row['target'],
			'weight':row['weight'],
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