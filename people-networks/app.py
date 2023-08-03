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
import time

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

standoff_base=4
standoff_count=0

st=time.time()
G=load_graph()
# while True:
# 	failed=False
# 	try:
# 		G=load_graph()
# 	except:
# 		failed=True
# 	if failed:
# 		standoff_time=standoff_base**standoff_count
# 		print("retrying after %d seconds" %(standoff_time))
# 		time.sleep(standoff_time)
# 		standoff_count+=1
# 	else:
# 		break
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
	
	st=time.time()
	rdata=request.json
	
	return jsonify({})