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
	print("----------\nthis tag",this_tag)
	print("starting graph state",G)
	e=int(max_edge_id+1)
	for tag_connection in tag_connections:
		connect_tag,as_type,mode=tag_connection
		print("connect tag",this_tag,"to",connect_tag,"as",as_type,"in mode",mode)
		#A node with no attributes keeps sneaking in here...
		for n_id in [n for n in G.nodes if this_tag in G.nodes[n]['tags']]:
			thisnode=G.nodes[n_id]
			comp_node_ids=[
				comp_id for comp_id in G.nodes
				if connect_tag in G.nodes[comp_id]['tags']
			]
			if mode=="closest":
				closest_neighbor,distance=getclosestneighbor(G,n_id,comp_node_ids)
				if as_type=="source":
					concat_tag="_to_".join([this_tag,connect_tag])
					s_id=n_id
					t_id=closest_neighbor
				else:
					s_id=closest_neighbor
					t_id=n_id
					concat_tag="_to_".join([connect_tag,this_tag])
				G.add_edge(s_id,t_id,distance=distance,id=e,tags=[concat_tag])
				e+=1
			elif mode=="all":
				for comp_node_id in comp_node_ids:
					distance=get_geo_edge_distance(n_id,comp_node_id,G)
					if as_type=="source":
						concat_tag="_to_".join([this_tag,connect_tag])
						s_id=n_id
						t_id=comp_node_id
					else:
						concat_tag="_to_".join([connect_tag,this_tag])
						s_id=comp_node_id
						t_id=n_id
					G.add_edge(s_id,t_id,id=e,distance=distance,tags=[concat_tag])
					e+=1
					
	print("ending graph state",G)
	print("-------------")
	return G

def add_non_oceanic_nodes(G,endpoint,graph_params,filter_obj,init_node_id=0):
	graph_name=graph_params['name']
	node_id=init_node_id
	headers={'Authorization':DJANGO_AUTH_KEY}
	ordered_node_classes=graph_params['ordered_node_classes']
	prev_tag=None
	for ordered_node_class in ordered_node_classes:
		## OCEANIC SUBGRAPH COMES FROM A FLATFILE
		tag=ordered_node_class['tag']
		if tag != 'oceanic_waypoint':
			
			# ON THIS GRAPH, SAY, TRANSATLANTIC REGIONAL ROUTES:
			## WE WANT TO GET EACH GEOGRAPHIC NODE'S VALUES
			## AND APPLY ITS TAG, SAY, EMBARK OR DISEMBARK
			thisgraphvl=ordered_node_class['values']
			thisgraphtag=ordered_node_class['tag']
			att_names=[a for a in list(thisgraphvl.keys()) if thisgraphvl[a] is not None]
			vl_var_names=[thisgraphvl[a] for a in att_names]
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
			## PUSH THE UNIQUE NODES (LAT,LONG,UUID,NAME,VALUE...) INTO THE GRAPH
			for row in rows:
				
				## BUT WE HAVE TO BE CAREFUL AND TAG THE NODES
				### (E.G., DID WE FIND THIS AS AN EMBARKATION OR DISEMBARKATION?)
				### (AND IF IT ALREADY EXISTS, THEN WE WANT TO LAYER THAT NEW TAG IN)
				### RATHER THAN DUPLICATING
				att_dict={att_name:row[att_names.index(att_name)] for att_name in att_names}
				
				#WE'VE GOT TO SCREEN OUT AND PROPERLY FORMAT NULL LAT & LONGS...
				#SO THIS IS A GEO-ONLY NETWORK FOR NOW...
				if 'lat' in att_dict and 'lon' in att_dict:
					
					lat=att_dict['lat']
					lon=att_dict['lon']
					if lat is not None and lon is not None:
						if (float(lat) < -.1 or float(lat) > .1) and (float(lon) < -.1 or float(lon) > .1):
							att_dict['lat']=float(lat)
							att_dict['lon']=float(lon)
							query=[{"==": [(k,), att_dict[k]]} for k in att_dict]
							existing_nodes=[n for n in 
								search_nodes(G, {"and":query})
							]
							if len(existing_nodes)>0:
								thisnodetags=[G.nodes[n] for n in existing_nodes][0]['tags']
								if tag not in thisnodetags:
									thisnodetags.append(tag)
									G.nodes[existing_nodes[0]]['tags']=thisnodetags
							else:
								att_dict['tags']=[tag]
								rowdict=(node_id,att_dict)
								G.add_nodes_from([rowdict])
								node_id+=1
						else:
							print("BAD NODE-->",att_dict)
					else:
						print("BAD NODE-->",att_dict)
				
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
	s=G.nodes[s_id]
	t=G.nodes[t_id]
	s_lat=s['lat']
	s_lon=s['lon']
	t_lat=t['lat']
	t_lon=t['lon']
	distance=geteuclideandistance(s_lat,s_lon,t_lat,t_lon)
# 	print(s_id,s,t_id,t,distance)
	return(distance)

def getclosestneighbor(G,thisnode_id,comp_nodes_ids):
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
	sorted_distances=sorted(distances, key=lambda tup: tup[0])
	closest_neighbor_distance,closest_neighbor_id=sorted_distances[0]
	return closest_neighbor_id,closest_neighbor_distance

def curvedab(A,B,C,prev_controlXY,smoothing=0.15):
# 	print("curving-->",A,B,C,prev_controlXY)
	## this function takes 4 xy points (the first [prev] or last [C] being nullable)
	## and returns a control point and a next control point for the AB segment
	## why this way? because splines that look forward and back not just to points
	## but to control points are much, much smoother
# 	print("curving",A,B,C,prev_controlXY)
	if prev_controlXY is None:
		#first edge
		ControlX = B[0] + smoothing*(A[0]-C[0])
		ControlY = B[1] + smoothing*(A[1]-C[1])
		Control=[ControlX,ControlY]
		nextControl=Control
	else:
		#last edge
		if C is None:
			C=B
		#all tother edges
		prev_ControlX,prev_ControlY=prev_controlXY
		ControlX = A[0]*2 - prev_ControlX
		ControlY = A[1]*2 - prev_ControlY
		next_ControlX = B[0] + smoothing*(A[0]-C[0])
		next_ControlY = B[1] + smoothing*(A[1]-C[1])
		Control=[ControlX,ControlY]
		nextControl=[next_ControlX,next_ControlY]
	return Control,nextControl
	
def straightab(A,B,ab_id,result):
	midx=(A[0]+B[0])/2
	midy=(A[1]+B[1])/2
	Control=(midx,midy)
	result[ab_id]=[[[A, B], [Control, Control]]]
	isstraight=True
	return result,Control


def retrieve_nodeXY(node):
	nodeX=node['data']['lat']
	nodeY=node['data']['lon']
	return [nodeX,nodeY]

def add_edge_topathdict(edgesdict,s,t,c1,c2,pathweight):
	if 'controls' in edgesdict[s][t]:
		edgesdict[s][t]['controls']['c1'].append({
			'control':c1,
			'weight':pathweight
		})
		edgesdict[s][t]['controls']['c2'].append({
			'control':c2,
			'weight':pathweight
		})
	else:
		edgesdict[s][t]['controls']={
			'c1':[{
				'control':c1,
				'weight':pathweight
			}],
			'c2':[{
				'control':c2,
				'weight':pathweight
			}]
		}
	return edgesdict

def getnodefromdict(node_id,nodesdict,G):
	if str(node_id) in nodesdict:
		node=nodesdict[str(node_id)]
	else:
		
		node=G.nodes[node_id]
		print("failed on",node_id,"data in graph is-->",node)
	return node


def spline_curves(nodes,edges,paths,G):
# 	print("edges",edges)
	for path in paths:
		pathnodes=path['path']
		pathweight=path['weight']
		i=0
# 		print("pathnodes-->",pathnodes)
		if len(pathnodes)>2:
			prev_controlXY=None
			while i<len(pathnodes)-2:
				A=getnodefromdict(pathnodes[i],nodes,G)
				B=getnodefromdict(pathnodes[i+1],nodes,G)
				C=getnodefromdict(pathnodes[i+2],nodes,G)
				A_id=str(A['id'])
				B_id=str(B['id'])
				Axy=retrieve_nodeXY(A)
				Bxy=retrieve_nodeXY(B)
				Cxy=retrieve_nodeXY(C)
				this_control,next_control=curvedab(Axy,Bxy,Cxy,prev_controlXY)
				edges=add_edge_topathdict(edges,A_id,B_id,this_control,next_control,pathweight)
				prev_controlXY=next_control
				i+=1
			A=getnodefromdict(pathnodes[i],nodes,G)
			B=getnodefromdict(pathnodes[i+1],nodes,G)
			C=None
			Axy=retrieve_nodeXY(A)
			Bxy=retrieve_nodeXY(B)
			A_id=str(A['id'])
			B_id=str(B['id'])
			this_control,next_control=curvedab(Axy,Bxy,C,prev_controlXY)
			edges=add_edge_topathdict(edges,A_id,B_id,this_control,next_control,pathweight)
			
		elif len(pathnodes)==2:
			A=getnodefromdict(pathnodes[0],nodes,G)
			B=getnodefromdict(pathnodes[1],nodes,G)
			Axy=retrieve_nodeXY(A)
			Bxy=retrieve_nodeXY(B)
			A_id=str(A['id'])
			B_id=str(B['id'])
			midx=(Axy[0]+Bxy[0])/2;
			midy=(Axy[1]+Bxy[1])/2;
			Control=[midx,midy]
			edges=add_edge_topathdict(edges,A_id,B_id,Control,Control,pathweight)
		else:
			print("bad path -- only one node?",path)
	
	def weightedaverage(controlpoints):
		
		denominator=sum([wxy['weight'] for wxy in controlpoints])
		if denominator!=0:
			numeratorX=sum([wxy['weight']*wxy['control'][0] for wxy in controlpoints])
			numeratorY=sum([wxy['weight']*wxy['control'][1] for wxy in controlpoints])
			finalX=numeratorX/denominator
			finalY=numeratorY/denominator
		else:
			denominator=len(controlpoints)
			numeratorX=sum([denominator*wxy['control'][0] for wxy in controlpoints])
			numeratorY=sum([denominator*wxy['control'][1] for wxy in controlpoints])
			finalX=numeratorX/denominator
			finalY=numeratorY/denominator
		
		return [finalX,finalY]
		
	for s in edges:
		for t in edges[s]:
			controls=edges[s][t]['controls']
			try:
				updatedc1=weightedaverage(controls['c1'])
				updatedc2=weightedaverage(controls['c2'])
				edges[s][t]['controls']=[updatedc1,updatedc2]
			except:
				print("FAILED CURVING",nodes[s],nodes[t],edges[s][t])
	
	return edges
			
	
