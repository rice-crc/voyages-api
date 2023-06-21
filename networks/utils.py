from math import sqrt
import networkx as nx
from localsettings import *
import requests
import json
from networkx_query import search_nodes, search_edges

def add_non_oceanic_nodes(G,endpoint,graph_params,filter_obj,init_node_id=0):
	graph_name=graph_params['name']
	node_id=init_node_id
	headers={'Authorization':DJANGO_AUTH_KEY}
	ordered_nodes=graph_params['ordered_nodes']
	for ordered_node in ordered_nodes:
		print("ordered node value list",ordered_node)
		## OCEANIC SUBGRAPH COMES FROM A FLATFILE
		if ordered_node != 'OCEANIC':
			
			# ON THIS GRAPH, SAY, TRANSATLANTIC REGIONAL ROUTES:
			## WE WANT TO GET EACH GEOGRAPHIC NODE'S VALUES
			## AND APPLY ITS TAG, SAY, EMBARK OR DISEMBARK
			thisgraphvl=ordered_node['values']
			thisgraphtag=ordered_node['tag']
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
				existing_nodes=[n for n in 
					search_nodes(G, {"==": [(k,), att_dict[k]] for k in att_dict})
				]
				
				if len(existing_nodes)>0:
# 					print("------>",[[G.nodes[n],n] for n in existing_nodes])
					thisnodetags=[G.nodes[n] for n in existing_nodes][0]['tags']
					if thisgraphtag not in thisnodetags:
						thisnodetags.append(thisgraphtag)
						G.nodes[existing_nodes[0]]['tags']=thisnodetags
# 						print("added tag:--->",thisgraphtag,[G.nodes[n] for n in existing_nodes])
				else:
					att_dict['tags']=[thisgraphtag]
					rowdict=(node_id,att_dict)
					G.add_nodes_from([rowdict])
					node_id+=1
			print("vl nodes added",G)
		else:
			print("skipping oceanic.")
	return G,node_id

def add_oceanic_network(G,oceanic_network,init_node_id=0):
	nodes=oceanic_network['nodes']
	links=oceanic_network['links']
	n_id=init_node_id
	for node in nodes:
		latitude,longitude=node
		lat=float(latitude)
		lon=float(longitude)
		tags=["oceanic_waypoint"]
		G.add_node(n_id,lat=lat,lon=lon,tags=tags,name=None)
		n_id+=1
	e_id=0
	for link in links:
		s_id,t_id=[int(n) for n in link]
		distance=get_geo_edge_distance(s_id,t_id,G)
		G.add_edge(s_id,t_id,distance=distance,id=e_id,tag="oceanic_leg")
		e_id+=1
	return(G,n_id)

def geteuclideandistance(Ay,Ax,By,Bx):
	distance=sqrt(
		(Ay-By)**2 +
		(Ax-Bx)**2
	)
	return distance

def get_geo_edge_distance(s_id,t_id,G):
	
	s_lat=G.nodes[s_id]['lat']
	s_lon=G.nodes[s_id]['lon']
	t_lat=G.nodes[t_id]['lat']
	t_lon=G.nodes[t_id]['lon']
	distance=geteuclideandistance(s_lat,t_lat,s_lon,t_lon)
	return(distance)

def getclosestneighbor(latlong,comp_nodes):
	a_lat,a_long=latlong
	distances=[
		(
			geteuclideandistance(
				a_lat,
				a_long,
				comp_nodes[n][0],
				comp_nodes[n][1]
			)
			,n
		)
		for n in comp_nodes
	]
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