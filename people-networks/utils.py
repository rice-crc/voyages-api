from math import sqrt
import networkx as nx
from localsettings import *
import requests
import json
import itertools
from networkx_query import search_nodes, search_edges
import uuid
import time

def get_or_create_node(G,data_dict):
	node_class=data_dict['node_class']
	class_id=data_dict["id"]
	node_gquery=[{"==":[('node_class',),node_class]},{"==":[('id',),class_id]}]
	querynodelist=list(search_nodes(G, {"and":node_gquery}))
	if len(querynodelist)==0:
		uid=str(uuid.uuid4())
		G.add_node(uid, **data_dict)
		node=G.nodes[uid]
	elif len(querynodelist)==1:
		uid=querynodelist[0]
		node=G.nodes[uid]
	else:
		print('ruh-roh, we have too many nodes here:',querynodelist)
		node=None
		uid=None
	return node,uid
		
def load_graph():

	G=nx.Graph()

	#GET VOYAGES
	
	selected_fields=[
		'id',
		'voyage_ship__ship_name',
		'voyage_itinerary__imp_principal_place_of_slave_purchase__name',
		'voyage_itinerary__imp_principal_port_slave_dis__name',
		'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year'
	]
	
	
	url=DJANGO_BASE_URL+'voyage/dataframes/'
	payload={
		"selected_fields":selected_fields
	}
	
	headers={'Authorization':DJANGO_AUTH_KEY,'Content-Type': 'application/json'}
	
	G=nx.Graph()
	
	r=requests.post(
		url=url,
		headers=headers,
		data=json.dumps(payload)
	)
	
	voyages_dict={}
	
	j=json.loads(r.text)
	
	for row_idx in range(len(j[selected_fields[0]])):
		rowdict={}
		for sf in selected_fields:
			rowdict[sf]=j[sf][row_idx]
		id=rowdict['id']
		rowdict['node_class']='voyages'
		uid=str(uuid.uuid4())
		G.add_node(uid, **rowdict)
		rowdict['uuid']=uid
		voyages_dict[id]=rowdict
	
	print("WITH VOYAGES--->",G)

	#GET ENSLAVERS
	
	selected_fields=[
		'id',
		'principal_alias'
	]
	
	url=DJANGO_BASE_URL+'past/enslaver/dataframes/'
	payload={
		"selected_fields":selected_fields
	}
	
	r=requests.post(
		url=url,
		headers=headers,
		data=json.dumps(payload)
	)
	
	enslavers_dict={}
	
	j=json.loads(r.text)
	
	for row_idx in range(len(j[selected_fields[0]])):
		rowdict={}
		for sf in selected_fields:
			rowdict[sf]=j[sf][row_idx]
		id=rowdict['id']
		rowdict['node_class']='enslavers'
		uid=str(uuid.uuid4())
		G.add_node(uid, **rowdict)
		rowdict['uuid']=uid
		enslavers_dict[id]=rowdict
	
	print("WITH ENSLAVERS-->",G)
	
	#GET ENSLAVED
	
	selected_fields=[
		'id',
		'documented_name',
		'age',
		'gender'
	]
	
	url=DJANGO_BASE_URL+'past/enslaved/dataframes/'
	payload={
		"selected_fields":selected_fields
	}
	
	r=requests.post(
		url=url,
		headers=headers,
		data=json.dumps(payload)
	)
	
	enslaved_dict={}
	
	j=json.loads(r.text)
	
	for row_idx in range(len(j[selected_fields[0]])):
		rowdict={}
		for sf in selected_fields:
			rowdict[sf]=j[sf][row_idx]
		id=rowdict['id']
		rowdict['node_class']='enslaved'
		uid=str(uuid.uuid4())
		G.add_node(uid, **rowdict)
		rowdict['uuid']=uid
		enslaved_dict[id]=rowdict
	
	print("WITH ENSLAVED--->",G)
		
	##FINALLY, RELATIONS
	
	selected_fields=[
		'id',
		'voyage__id',
		'relation_type__name',
		'enslaved_in_relation__enslaved__id',
		'relation_enslavers__enslaver_alias__identity__id'
	]
	url=DJANGO_BASE_URL+'past/enslavementrelations/dataframes/'
	payload={
		"selected_fields":selected_fields
	}
	
	headers={'Authorization':DJANGO_AUTH_KEY,'Content-Type': 'application/json'}
	
	
	r=requests.post(
		url=url,
		headers=headers,
		data=json.dumps(payload)
	)
	
	relations_dict={}
	
	j=json.loads(r.text)
	
	for row_idx in range(len(j[selected_fields[0]])):
		rowdict={}
		for sf in selected_fields:
			rowdict[sf]=j[sf][row_idx]
		relation_id=rowdict['id']
		if relation_id not in relations_dict:
			relations_dict[relation_id]=[rowdict]
		else:
			relations_dict[relation_id].append(rowdict)
	
	c=1
	
	relation_types=[]
	
	for relation_id in relations_dict:
		relation_connections=relations_dict[relation_id]
		
		relation_type=relation_connections[0]['relation_type__name']
		voyage_uuids=list(set([voyages_dict[rc['voyage__id']]['uuid'] for rc in relation_connections if rc['voyage__id'] is not None]))
		enslaved_uuids=list(set([enslaved_dict[rc['enslaved_in_relation__enslaved__id']]['uuid'] for rc in relation_connections if rc['enslaved_in_relation__enslaved__id'] is not None]))
		enslaver_uuids=list(set([enslavers_dict[rc['relation_enslavers__enslaver_alias__identity__id']]['uuid'] for rc in relation_connections if rc['relation_enslavers__enslaver_alias__identity__id'] is not None]))
		##NOT YET HANDLING ENSLAVER ROLES
		if relation_type=="Marriage":
			#enslaver-to-enslaver marriages
			if len(enslaver_uuids)==2:
				alice,bob=enslaver_uuids
				G.add_edge(alice,bob)
			else:
				print("got more or fewer spouses than anticipated-->",enslaver_uuids,relation_connections)
		elif relation_type=="transportation":
			if len(enslaved_uuids)==0:
				#captain & shipowner/investor relations to voyages
				if len(voyage_uuids)==1:
					voyage_uuid=voyage_uuids[0]
					for enslaver_uuid in enslaver_uuids:
						G.add_edge(enslaver_uuid,voyage_uuid)
				else:
					print('got more or fewer voyages than anticipated-->',relation_connections)
			else:
				rel_uuid=str(uuid.uuid4())
				reldata={
					'uuid':rel_uuid,
					'relation_type__name':relation_type,
					'id':relation_id
				}
				G.add_node(rel_uuid, **rowdict)
				
				if voyage_uuids is not None:
					if len(voyage_uuids)==1:
						voyage_uuid=voyage_uuids[0]
						G.add_edge(rel_uuid,voyage_uuid)
					else:
						print('got more or fewer voyages than anticipated-->',relation_connections)
				if enslaver_uuids is not None:
					for enslaver_uuid in enslaver_uuids:
						G.add_edge(rel_uuid,enslaver_uuid)
				if enslaved_uuids is not None:
					for enslaved_uuids in enslaved_uuids:
						G.add_edge(rel_uuid,enslaved_uuids)
				

	print("WITH CONNECTIONS-->",G)
	return (G)