import time
from flask import Flask,jsonify,request,abort
import json
import math
import requests
from localsettings import *
from utils import *
import networkx as nx
from networkx_query import search_nodes, search_edges
import re
import time

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

standoff_base=4
standoff_count=0

st=time.time()
# G=load_graph()
while True:
	failed=False
	try:
		G=load_graph()
	except:
		failed=True
	if failed:
		standoff_time=standoff_base**standoff_count
		print("retrying after %d seconds" %(standoff_time))
		time.sleep(standoff_time)
		standoff_count+=1
	else:
		break
print("finished building graphs in %d seconds" %int(time.time()-st))


@app.route('/',methods=['POST'])
def network_maps():
	
	'''
	accepts id (database pk) arrays for:
		enslaved
		enslavers
		voyages
		enslavement_relations
	returns nodes and edges with attributes
	i think we should give back 1 hop to start
	'''
	print("received",request.json)

	
	nodes_dict={}
	edges=[]
	st=time.time()
	
	for nodeclass in ['enslaved','enslavers','voyages','enslavement_relations']:
		node_id_list=request.json.get(nodeclass)
		print("fetching",nodeclass)
		if node_id_list is not None:
			node_id_int_list=[int(i) for i in node_id_list]
			gquery=[{"==":[('node_class',),nodeclass]},{":=":[('id',),node_id_int_list]}]
			querynodes=search_nodes(G, {"and":gquery})
			for n in querynodes:
				nodes_dict[n]=G.nodes[n]
				predecessors=G.predecessors(n)
				for p in predecessors:
					e={'source':p,'target':n,'data':G.edges[p,n]}
					if e not in edges:
						edges.append(e)
					nodes_dict[p]=G.nodes[p]
					for pp in G.predecessors(p):
						e={'source':pp,'target':p,'data':G.edges[pp,p]}
						if e not in edges:
							edges.append(e)
						nodes_dict[pp]=G.nodes[pp]
					for ps in G.successors(p):
						e={'source':p,'target':ps,'data':G.edges[p,ps]}
						if e not in edges:
							edges.append(e)
						nodes_dict[ps]=G.nodes[ps]
				successors=G.successors(n)
				for s in successors:
					e={'source':n,'target':s,'data':G.edges[n,s]}
					if e not in edges:
						edges.append(e)
					nodes_dict[s]=G.nodes[s]
					for ss in G.successors(s):
						e={'source':s,'target':ss,'data':G.edges[s,ss]}
						if e not in edges:
							edges.append(e)
						nodes_dict[ss]=G.nodes[ss]
					for sp in G.predecessors(s):
						e={'source':sp,'target':s,'data':G.edges[sp,s]}
						if e not in edges:
							edges.append(e)
						nodes_dict[sp]=G.nodes[sp]
	nodes=[nodes_dict[k] for k in nodes_dict]
	
	print("elapsed time:",time.time()-st)
	output={
		"nodes":nodes,
		"edges":edges
	}

	st=time.time()
	rdata=request.json
	
	return jsonify(output)