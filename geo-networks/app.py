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
# 			try:
			graph,graph_name,shortest_paths=load_graph(endpoint,graph_params)
			rc['graphs'][graph_name]={
				'graph':graph,
				'shortest_paths':shortest_paths
			}
# 			except:
# 				failures_count+=1
# 				print("failed on cache:",rc['name'])
# 				break
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
	## NOTE -- "TRANSPORTATION" IS SPECIAL (YES, HARD-CODED)
	## IT FORCES SELF-LOOPS TO ENTER INTO THE OCEANIC NETWORK AND THEN FIND A PATH HOME
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
		"data":{},
# 		"prev_nodes":{},
# 		"next_nodes":{}
		} for k in payload for i in k.split('__') if i != "None"
	}
	
	classedabweights={}
	for k in payload:
		w=payload[k]
		uuids=k.split('__')
		#nodes
		if "None" not in uuids:
			for idx in range(len(uuids)):
				nodelabel=nodelabels[idx]
				uuid=uuids[idx]
				nodes[uuid]['weights'][nodelabel]+=w
			#edges
			abpairs=[(uuids[i],uuids[i+1]) for i in range(len(uuids)-1)]
			for idx in range(len(linklabels)):
				abpair=abpairs[idx]
				linklabel=linklabels[idx]
				if linklabel not in classedabweights:
					classedabweights[linklabel]={}
				if "None" not in abpair:
					a,b=abpair
					if a not in classedabweights[linklabel]:
						classedabweights[linklabel][a]={b:w}
					else:
						if b not in classedabweights[linklabel][a]:
							classedabweights[linklabel][a][b]=w
						else:
							classedabweights[linklabel][a][b]+=w
	
	edges={}
	
	shortest_path_times=0
	
	shortest_paths=[]
	
	for linklabel in linklabels:
		abweights=classedabweights[linklabel]
		for s_uuid in abweights:
			sourcenodematch=[n for n in search_nodes(graph,{"==":["uuid",s_uuid]})]
			# currently, i'm only getting errors on nodes that had no lat or long
			## and therefore were not added into the network
			
			if len(sourcenodematch)!=0:
				s_id=sourcenodematch[0]
				#drop the networkx node tags
				##we want dynamic multi-classed scores on each node
				##BUT DO NOT TOUCH THE GRAPH ITSELF
				sourcenode=dict(graph.nodes[s_id])
				if 'tags' in sourcenode:
					del sourcenode['tags']
				nodes[s_uuid]['data']=sourcenode
				for t_uuid in abweights[s_uuid]:
					targetnodematch=[n for n in search_nodes(graph,{"==":["uuid",t_uuid]})]
					
					if len(targetnodematch)!=0:
						t_id=targetnodematch[0]
						
						if s_id==t_id and linklabel=='transportation':
 							#TRANSPORTATION SELF-LOOP
							selfloop=True
							successor_id=[
								n_id for n_id in graph.successors(s_id)
								if 'onramp' in graph.nodes[n_id]['tags']
							][0]
							
						else:
							selfloop=False
						w=classedabweights[linklabel][s_uuid][t_uuid]
						targetnode=dict(graph.nodes[t_id])
						
						if 'tags' in targetnode:
							del targetnode['tags']
						nodes[t_uuid]['data']=targetnode
						
						shortest_path_st=time.time()
						try:
							if selfloop:
								sp=nx.shortest_path(graph,successor_id,t_id,'distance')
								sp.insert(0,s_id)
							else:
								sp=nx.shortest_path(graph,s_id,t_id,'distance')
							
						except:
							print("---\nNO PATH")
							print("from",sourcenode)
							print("to",targetnode,"\n---")
							sp=[]
						shortest_path_times+=time.time()-shortest_path_st
									
						if len(sp)>1:
							sp_export=list(sp)
							sp_export=sp_export[1:-1]
							sp_export=[s_uuid]+sp_export+[t_uuid]
							shortest_paths.append({
								"path":sp_export,
								"weight":w
							})
							abpairs=[(sp[i],sp[i+1]) for i in range(len(sp)-1)]
							for a,b in abpairs:
								
								anode=graph.nodes[a]
								bnode=graph.nodes[b]
								
								if 'uuid' not in anode:
									a_id=str(a)
								else:
									a_id=anode['uuid']
								if 'uuid' not in bnode:
									b_id=str(b)
								else:
									b_id=bnode['uuid']
								
								#edges
								if a_id not in edges:
									edges[a_id]={b_id:{'w':w,'type':linklabel}}
								else:
									if b_id not in edges[a_id]:
										edges[a_id][b_id]={'w':w,'type':linklabel}
									else:
										edges[a_id][b_id]['w']+=w
								#add oceanic nodes (although we prob don't need to?)
								if a_id not in nodes:
									nodes[a_id]={
										'data':anode,
										'id':a_id,
										'weights':{}
									}
								if b_id not in nodes:
									nodes[b_id]={
										'data':bnode,
										'id':b_id,
										'weights':{}
									}
	
	print("shortest path times=",shortest_path_times)
	
	splined=True
	
	if splined:
		edges=spline_curves(nodes,edges,shortest_paths)
	
	edgesflat=[]
	for s in edges:
		for t in edges[s]:
			edge=edges[s][t]
			thisedge={'source':s,'target':t,'weight':edge['w'],'type':edge['type'], 'controls': edge['controls']}
			edgesflat.append(thisedge)
	outputs={
		"nodes":[nodes[k] for k in nodes],
		"edges":edgesflat,
		"paths":shortest_paths
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