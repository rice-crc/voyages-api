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
	
	#currently, enslaver aliases are "in front" of enslaver identities
	#which means we need the aliases to connect identities to relations
	#but also that we get duplicate identities back
	enslaver_alias_map={}
	
	for dfname in ['enslaved','enslavers','voyages','enslavement_relations']:
		df=j[dfname]
		for row_idx in range(len(df['id'])):
			id=df['id'][row_idx]
			uid=str(uuid.uuid4())
			
			#currently, enslaver aliases are "in front" of enslaver identities
			#which means we need the aliases to connect identities to relations
			#but also that we get duplicate identities back
			if dfname=='enslavers':
				alias_id=df['alias_id'][row_idx]
				enslaver_alias_map[alias_id]=id
				if id in idmap[dfname]:
					#wanted to retain the alias ids but this is slow as hell.
					#an alternative method would be to add an extra dataframe call connecting aliases to identities
					#but i don't see the value here as we can always get the aliases on a call to the identity-based enslaver list endpoint
					
					# enslaver_node_id=[n for n in 
# 						search_nodes(G, {"==": [('id',), id]})
# 					][0]
# 					enslaver_node=G.nodes[enslaver_node_id]
# 					print("APPENDING",id,enslaver_node)
# 					enslaver_node['alias_ids'].append(alias_id)
					pass
				else:
# 					print("adding",id)
					idmap[dfname][id]=uid
					alias_ids=[alias_id]
					obj={k:df[k][row_idx] for k in list(df.keys()) if k!= 'alias_id'}
# 					obj['alias_ids']=alias_ids
					obj['node_class']=dfname
					obj['uuid']=uid
					G.add_node(uid, **obj)
			else:
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
		#currently, enslaver aliases are "in front" of enslaver identities
		#which means we need the aliases to connect identities to relations
		#but also that we get duplicate identities back
		identity_id=enslaver_alias_map[obj['enslaver_alias']]
		enslaver_uuid=idmap['enslavers'][identity_id]
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