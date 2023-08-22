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
	we're now giving back 1 hop (but passing through some intermediary nodes (see utils.py))
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
				print("getting node",n)
				nodes_dict,edges=add_predecessors(G,nodes_dict,n,edges)
				nodes_dict,edges=add_successors(G,nodes_dict,n,edges)

	nodes=[nodes_dict[k] for k in nodes_dict]
	
	print("elapsed time:",time.time()-st)
	output={
		"nodes":nodes,
		"edges":edges
	}

	st=time.time()
	rdata=request.json
	
	return jsonify(output)