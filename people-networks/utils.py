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
	
# STRUCTURE	
# 		relation_map={
# 			'enslaved':enslaved_people_df,
# 			'enslavers':enslaver_aliases_df,
# 			'voyages':voy_df,
# 			'enslavement_relations':enslavementrelation_df,
# 			'enslaved_in_relation':enslaved_in_relation_df,
# 			'enslavers_in_relation':enslaver_in_relation_df	
# 		}
	
	idmap={
		'enslaved':{},
		'enslavers':{},
		'voyages':{},
		'enslavement_relations':{}
	}
	
	for dfname in ['enslaved','enslavers','voyages','enslavement_relations']:
		df=j[dfname]
		for row_idx in range(len(df['id'])):
			id=df['id'][row_idx]
			uid=str(uuid.uuid4())
			idmap[dfname][id]=uid
			obj={k:df[k][row_idx] for k in list(df.keys())}
			obj['node_class']=dfname
			obj['uuid']=uid
			G.add_node(uid, **obj)
			
	
	eir = j['enslaved_in_relation']
	for row_idx in range(len(eir['relation'])):
		obj={k:eir[k][row_idx] for k in list(eir.keys())}
		enslaved_uuid=idmap['enslaved'][obj['enslaved']]
		relation_uuid=idmap['enslavement_relations'][obj['relation']]
		G.add_edge(enslaved_uuid,relation_uuid)
	
	eir = j['enslavers_in_relation']
	for row_idx in range(len(eir['relation'])):
		obj={k:eir[k][row_idx] for k in list(eir.keys())}
		enslaver_uuid=idmap['enslavers'][obj['enslaver_alias']]
		relation_uuid=idmap['enslavement_relations'][obj['relation']]
		G.add_edge(enslaver_uuid,relation_uuid,role__name=obj['role__name'])
	
	#then once more around to get voyages tied in to relations
	enslavement_relations=[n for n in 
		search_nodes(G, {"==": [('node_class',), 'enslavement_relations']})
	]
	
	for n_id in enslavement_relations:
		voyage_id=G.nodes[n_id]['voyage']
		if voyage_id is not None:
			voyage_uuid=idmap['voyages'][voyage_id]
			G.add_edge(n_id,voyage_uuid)
	
	print(G)
	return G