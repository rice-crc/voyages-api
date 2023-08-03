from math import sqrt
import networkx as nx
from localsettings import *
import requests
import json
from networkx_query import search_nodes, search_edges
import uuid
import time


def load_graph():
	url=DJANGO_BASE_URL+'common/past_graph/'
	headers={'Authorization':DJANGO_AUTH_KEY}

	G=nx.DiGraph()
	
	r=requests.post(
		url=url,
		headers=headers
	)

	j=json.loads(r.text)
	
# 	g.add_node('node1', **optional_attrs)
	
# 	for k in list(j.keys()):
# 		for i in list(j[k].keys()):
# 			print(k,i,len(j[k][i]))
# 			time.sleep(.5)
	
	idmap={
		'enslaved':{},
		'enslavers':{},
		'voyages':{},
		'enslaved_in_relation':{},
		'enslavers_in_relation':{},
		'enslavement_relations':{}
	}
	
	for dfname in ['enslaved','enslavers','voyages','enslavement_relations']:
		df=j[dfname]
		for row_idx in range(len(df['id'])):
			id=df['id'][row_idx]
			uid=str(uuid.uuid4())
			idmap[dfname][uid]=uid
			obj={k:df[k][row_idx] for k in list(df.keys())}
			G.add_node(uid, **obj)
	
	print(G)