from math import sqrt
import networkx as nx
from localsettings import *
import requests
import json
from networkx_query import search_nodes, search_edges

def geteuclideandistance(Ay,Ax,By,Bx):
	distance=sqrt(
		(Ay-By)**2 +
		(Ax-Bx)**2
	)
	return distance

def connect_to_tags(G,this_tag,tag_connections):
	max_edge_id=max([G.edges[e[0],e[1]]['id'] for e in G.edges])
# 	max_edge_id=max([G.edges(e[0],e[1])['id'] for e in G.edges])
	print("----------\nthis tag",this_tag)
	print("starting graph state",G)
	e=int(max_edge_id)
	for tag_connection in tag_connections:
		connect_tag,as_type,mode=tag_connection
		print("connect tag",this_tag,"to",connect_tag,"as",as_type,"in mode",mode)
		
# 		print(,tag)
		for n_id in G.nodes:
			thisnode=G.nodes[n_id]
			
			comp_node_ids=[
				comp_id for comp_id in G.nodes
				if connect_tag in G.nodes[comp_id]['tags']
			]
			if mode=="closest":
# 				print("closest")
				closest_neighbor,distance=getclosestneighbor(G,n_id,comp_node_ids)
				if as_type=="source":
					G.add_edge(n_id,closest_neighbor,distance=distance,id=e,tag=connect_tag)
				else:
					G.add_edge(closest_neighbor,n_id,distance=distance,id=e,tag=connect_tag)
				e+=1
			elif mode=="all":
				lat=G.nodes[n_id]['lat']
				lon=G.nodes[n_id]['lon']
	
				for comp_node_id in comp_node_ids:
					distance=get_geo_edge_distance(n_id,comp_node_id,G)
					if as_type=="source":
						G.add_edge(n_id,comp_node_id,id=e,distance=distance,tag=this_tag)
					else:
						G.add_edge(comp_node_id,n_id,id=e,distance=distance,tag=this_tag)
					e+=1
	print("ending graph state",G)
	print("-------------")
	return G

def floatnotnull(x):
	try:
		return float(x)
	except:
		return 0

def add_non_oceanic_nodes(G,endpoint,graph_params,filter_obj,init_node_id=0):
	graph_name=graph_params['name']
	node_id=init_node_id
	headers={'Authorization':DJANGO_AUTH_KEY}
	ordered_node_classes=graph_params['ordered_node_classes']
	prev_tag=None
	for ordered_node_class in ordered_node_classes:
# 		print("ordered node value list",ordered_node_class)
		## OCEANIC SUBGRAPH COMES FROM A FLATFILE
		tag=ordered_node_class['tag']
		if tag != 'oceanic_waypoint':
			
			# ON THIS GRAPH, SAY, TRANSATLANTIC REGIONAL ROUTES:
			## WE WANT TO GET EACH GEOGRAPHIC NODE'S VALUES
			## AND APPLY ITS TAG, SAY, EMBARK OR DISEMBARK
			thisgraphvl=ordered_node_class['values']
			thisgraphtag=ordered_node_class['tag']
			att_names=[a for a in list(thisgraphvl.keys()) if thisgraphvl[a] is not None]
# 				print("-->attnames",att_names)
			vl_var_names=[thisgraphvl[a] for a in att_names]
# 				print('-->vl_varnames',vl_var_names)
			payload={'selected_fields':vl_var_names}
			
			## MAKE SURE YOU APPLY THE FILTER TO THE QUERY
			### E.G., ARE WE AFTER TRANSATLANTIC OR INTRA-AMERICAN VOYAGES?
			for f in filter_obj:
				payload[f]=filter_obj[f]
				
			## MAKE A DATAFRAME CALL ON ALL THE VARIABLES ENUMERATED FOR THIS NODE
			r=requests.post(
				url=DJANGO_BASE_URL+endpoint,
				headers=headers,
				data=payload
			)
			
			## TRANSFORM THE RESPONSE INTO ROWS AND DEDUPE
			results=json.loads(r.text)
			rows=[]
			for i in range(len(results[vl_var_names[0]])):
				row=[]
				for vl_var_name in vl_var_names:
					row.append(results[vl_var_name][i])
				if row not in rows:
					rows.append(row)
			
			## PUSH THE UNIQUE NODES (LAT,LONG,PK,NAME,VALUE...) INTO THE GRAPH
			for row in rows:
				
				## BUT WE HAVE TO BE CAREFUL AND TAG THE NODES
				### (E.G., DID WE FIND THIS AS AN EMBARKATION OR DISEMBARKATION?)
				### (AND IF IT ALREADY EXISTS, THEN WE WANT TO LAYER THAT NEW TAG IN)
				### RATHER THAN DUPLICATING
				att_dict={att_name:row[att_names.index(att_name)] for att_name in att_names}
				
				if 'lat' in att_dict:
					att_dict['lat']=floatnotnull(att_dict['lat'])
				if 'lon' in att_dict:
					att_dict['lon']=floatnotnull(att_dict['lon'])

				
				existing_nodes=[n for n in 
					search_nodes(G, {"==": [(k,), att_dict[k]] for k in att_dict})
				]
				
				if len(existing_nodes)>0:
# 					print("------>",[[G.nodes[n],n] for n in existing_nodes])
					thisnodetags=[G.nodes[n] for n in existing_nodes][0]['tags']
					if tag not in thisnodetags:
						thisnodetags.append(tag)
						G.nodes[existing_nodes[0]]['tags']=thisnodetags
# 						print("added tag:--->",tag,[G.nodes[n] for n in existing_nodes])
				else:
					att_dict['tags']=[tag]
					rowdict=(node_id,att_dict)
					G.add_nodes_from([rowdict])
					node_id+=1
				
	return G,node_id

def add_oceanic_network(G,oceanic_network,init_node_id=0):
	nodes=oceanic_network['nodes']
	links=oceanic_network['links']
	n_id=init_node_id
	#add in the nodes
	oceanic_node_ids=[]
	for node in nodes:
		latitude,longitude=node
		lat=float(latitude)
		lon=float(longitude)
		tags=["oceanic_waypoint"]
		G.add_node(n_id,lat=lat,lon=lon,tags=tags,name=None)
		oceanic_node_ids.append(n_id)
		n_id+=1
	e_id=0
	#link them (directionally)
	for link in links:
		s_id,t_id=[int(n) for n in link]
		distance=get_geo_edge_distance(s_id,t_id,G)
		G.add_edge(s_id,t_id,distance=distance,id=e_id,tags=["oceanic_leg"])
		e_id+=1
	#layer in the onramp/offramp tags
	
	for n_id in oceanic_node_ids:
		ntags=G.nodes[n_id]['tags']
		successors=[o for o in G.successors(n_id)]
		predecessors=[o for o in G.predecessors(n_id)]
		if len(successors)>0:
			ntags.append('onramp')
		if len(predecessors)>0:			
			ntags.append('offramp')
		G.nodes[n_id]['tags']=ntags
	max_node_id=max(oceanic_node_ids)
	return(G,max_node_id)

def get_geo_edge_distance(s_id,t_id,G):
	s_lat=G.nodes[s_id]['lat']
	s_lon=G.nodes[s_id]['lon']
	t_lat=G.nodes[t_id]['lat']
	t_lon=G.nodes[t_id]['lon']
	distance=geteuclideandistance(s_lat,t_lat,s_lon,t_lon)
	return(distance)

def getclosestneighbor(G,thisnode_id,comp_nodes_ids):	
# 	print(thisnode_id,"closestneighborfrom-->",comp_nodes_ids)
	distances=[
		(
			get_geo_edge_distance(
				thisnode_id,
				t_id,
				G
			)
			,t_id
		)
		for t_id in comp_nodes_ids
	]
	
	distances=[d for d in distances if d is not None]
	
	closest_neighbor=sorted(distances, key=lambda tup: tup[0])[0][1]
	distance=min([i[0] for i in distances])
	return closest_neighbor,distance

def curvedab(A,B,C,ab_id,prev_controlXY,result,smoothing=0.15):
	##next: smoothing should handled dynamically
	####--> based on this segment's length relative to previous segment
	####--> but this is a look-forward function, so should probably be handled outside of this...
	if prev_controlXY is None:
		#first edge
		ControlX = B[0] + smoothing*(A[0]-C[0])
		ControlY = B[1] + smoothing*(A[1]-C[1])
		Control=(ControlX,ControlY)
		result[ab_id]=[[[A, B], [Control, Control]]]
		return result,Control
	else:
		#last edge
		if C is None:
			C=B
		#all tother edges
		prev_ControlX,prev_ControlY=prev_controlXY
		ControlX = A[0]*2 - prev_ControlX
		ControlY = A[1]*2 - prev_ControlY
# 					ControlX = A[0]*2 - prev_ControlX
# 					ControlY = A[1]*2 - prev_ControlY
		next_ControlX = B[0] + smoothing*(A[0]-C[0])
		next_ControlY = B[1] + smoothing*(A[1]-C[1])
		result[ab_id]=[[[A, B],[[ControlX,ControlY],[next_ControlX,next_ControlY]]]]
		return result,(next_ControlX,next_ControlY)
	
def straightab(A,B,ab_id,result):
	midx=(A[0]+B[0])/2
	midy=(A[1]+B[1])/2
	Control=(midx,midy)
	result[ab_id]=[[[A, B], [Control, Control]]]
	isstraight=True
	return result,Control