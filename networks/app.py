import time
from flask import Flask,jsonify,request,abort
import json
import math
import requests
from localsettings import *
from index_vars import *
from utils import *
import networkx as nx
import re

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
# 		print("Network file----->",oceanic_network_file)
		d=open(oceanic_network_file,'r')
		t=d.read()
		d.close()
		oceanic_network=json.loads(t)
		G,max_node_id=add_oceanic_network(G,oceanic_network,init_node_id=0)
		print("created oceanic network",G)
# 		for n in G.nodes:
# 			print("node-->",G.nodes[n])
		# THEN ITERATE OVER THE GEO VARS IN THE INDEX
		## AND ADD THE RESULTING UNIQUE NODES TO THE NETWORK
		filter_obj=rc['filter']
		G,max_node_id=add_non_oceanic_nodes(G,endpoint,graph_params,filter_obj,init_node_id=max_node_id+1)
		print("added non-oceanic network nodes")
# 		for n in G.nodes:
# 			print("node-->",G.nodes[n])
		#then link across the ordered node classes
		ordered_node_classes=graph_params['ordered_node_classes']
		prev_tag=None
		for ordered_node_class in ordered_node_classes:
			tag=ordered_node_class['tag']
			if 'tag_connections' in ordered_node_class:
				tag_connections=ordered_node_class['tag_connections']
				G=connect_to_tags(G,tag,tag_connections)
		print("connected all remaining network edges (non-oceanic --> (non-oceanic & oceanic)) following index_vars.py file ruleset")
	return G,graph_name,None

registered_caches={
	'transatlantic_maps':transatlantic_maps,
	'intraamerican_maps':intraamerican_maps,
	'ao_maps':ao_maps
}

#on initialization, load every index as a graph, via a call to the django api

rcnames=list(registered_caches.keys())

for rcname in rcnames:
	st=time.time()
	rc=registered_caches[rcname]
# 	try:
	endpoint=rc['endpoint']
	if 'graphs' not in rc:
		rc['graphs']={}

	for graph_params in rc['graph_params']:
# 		print("INITIALIZING",endpoint,graph_params)
		graph,graph_name,shortest_paths=load_graph(endpoint,graph_params)
		rc['graphs'][graph_name]={
			'graph':graph,
			'shortest_paths':shortest_paths
		}
	registered_caches[rcname]=rc
	print("finished building graphs in %d seconds" %int(time.time()-st))
	
# 	except:
# 		print("failed on cache:",rc['name'])

@app.route('/simple_map/<cachename>',methods=['GET'])
# @app.route('/simple_map',methods=['GET'])
def simple_map(cachename):
# def simple_map():
	'''
	Implements the pandas groupby function and returns the sparse summary.
	Excellent for bar & pie charts.
	'''
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
					if 'pk' in node:
						feature['properties']['pk']=node['pk']
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
# 		d=open("tmp/%s__%s.json" %(cachename,graphname),'w')
# 		d.write(json.dumps(featurecollection))
# 		d.close()
	print("Internal Response Time:",time.time()-st,"\n+++++++")
	return jsonify(resp)





# 
# 
# 
# #we need to make the indices' contents visible
# @app.route('/get_indices/')
# def get_indices():
# 	resp={}
# 	for rc in registered_caches:
# 		resp[rc['name']]=rc['variables']
# 	return json.dumps(resp)
# 
# @app.route('/groupby/',methods=['POST'])
# def groupby():
# 
# 	'''
# 	Implements the pandas groupby function and returns the sparse summary.
# 	Excellent for bar & pie charts.
# 	'''
# 	st=time.time()
# 	rdata=request.json
# 	dfname=rdata['cachename'][0]
# 	ids=rdata['ids']
# 	groupby_by=rdata['groupby_by'][0]
# 	groupby_cols=rdata['groupby_cols']
# 	agg_fn=rdata['agg_fn'][0]
# 	df=eval(dfname)['df']
# 	df2=df[df['id'].isin(ids)]
# 	ct=df2.groupby(groupby_by,group_keys=True)[groupby_cols].agg(agg_fn)
# # 	ct=ct.fillna(0)
# 	resp={groupby_by:list(ct.index)}
# 	for gbc in groupby_cols:
# 		resp[gbc]=list(ct[gbc])
# 	return json.dumps(resp)
# 
# @app.route('/crosstabs/',methods=['POST'])
# def crosstabs():
# 	
# 	'''
# 	Implements the pandas crosstab function and returns the sparse summary.
# 	Excellent for pivot tables and maps (e.g., Origin/Destination pairs for voyages with summary values for those pairs)
# 	'''
# 
# 	try:
# 		st=time.time()
# 		rdata=request.json
# 		dfname=rdata['cachename'][0]
# 
# 		#it must have a list of ids (even if it's all of the ids)
# 		ids=rdata['ids']
# 
# 		#and a 2ple for groupby_fields to give us rows & columns (maybe expand this later)
# 		columns,rows=rdata['groupby_fields']
# 		val=rdata['value_field'][0]
# 		fn=rdata['agg_fn'][0]
# 
# 		normalize=rdata.get('normalize')
# 		if normalize is not None:
# 			normalize=normalize[0]
# 		if normalize not in ["columns","index"]:
# 			normalize=False
# 
# 		df=eval(dfname)['df']
# 
# 		df2=df[df['id'].isin(ids)]
# 
# 		bins=rdata.get('bins')
# 		if bins is not None:
# 			binvar,nbins=[bins[0],int(bins[1])]
# 			df2=pd.cut(df2[binvar],nbins)
# 		ct=pd.crosstab(
# 			df2[columns],
# 			df2[rows],
# 			values=df2[val],
# 			aggfunc=eval("np."+fn),
# 			normalize=normalize,
# 		)
# 		ctd={col: ct[col].dropna().to_dict() for col in ct.columns}
# 		return jsonify(ctd)
# 	except:
# 		abort(400)
# 
# @app.route('/dataframes/',methods=['POST'])
# def dataframes():
# 	
# 	'''
# 	Allows you to select long-format columns of data on any (indexed) selected field.
# 	Excellent for a data export or any general dataframe use-case.
# 	'''
# 	
# 	try:
# 		st=time.time()
# 	
# 		rdata=request.json
# 	
# 		dfname=rdata['cachename'][0]
# 		df=eval(dfname)
# 		ids=rdata['ids']
# 		df2=df[df['id'].isin(ids)]
# 		columns=list(set(rdata['selected_fields']+['id']))
# 		df2=df2[[c for c in columns]]
# 		df3=df2.set_index('id')
# 		df3=df3.reindex(ids)
# 		df3=df3.fillna(0)
# 		j3=df3.to_dict()
# 	
# 		return jsonify(j3)
# 	except:
# 		abort(400)