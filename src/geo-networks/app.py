import time
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify,send_file
import json
import math
import requests
from localsettings import *
from index_vars import *
from utils import *
import networkx as nx
from networkx_query import search_nodes, search_edges
import re
import pickle
import os
import pandas as pd
from flask_login import login_user,LoginManager,UserMixin,login_required

app = Flask(__name__,template_folder='./templates/')
app.config['JSON_SORT_KEYS'] = False
app.config.from_object(__name__)
app.secret_key = FLASK_SECRET_KEY
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active
    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return True

@login_manager.user_loader
def load_user(userid):
	return USERS.get(int(userid))

login_manager.setup_app(app)

def load_index(rcname,graphname):
	rc=registered_caches[rcname]
	dataframe_endpoint=rc['endpoint']
	if 'graphs' not in rc:
		rc['graphs']={}
	if not os.path.exists(TMP_PATH):
		os.makedirs(TMP_PATH)

	picklefilepath=f'{TMP_PATH}/{rcname}__{graphname}.pickle'
	graph_params=[gp for gp in registered_caches[rcname]['graph_params'] if gp['name']==graphname][0]
	if os.path.exists(picklefilepath):
		with open(picklefilepath, 'rb') as f:
			graph_index = pickle.load(f)
	else:
		graph,oceanic_subgraph_view,graphname=load_graph(dataframe_endpoint,graph_params,rc)
		linklabels=rc['indices']['linklabels']
		nodelabels=rc['indices']['nodelabels']
		graph_idx=rc['indices'][graphname]
		pk_var=graph_idx['pk']
		itinerary_vars=graph_idx['itinerary']
		weight_vars=graph_idx['weight']
		graph_index=build_index(
			dataframe_endpoint,
			graph,
			oceanic_subgraph_view,
			pk_var,
			itinerary_vars,
			weight_vars,
			linklabels,
			nodelabels
		)
		with open(picklefilepath, 'wb') as f:
			pickle.dump(graph_index, f, pickle.HIGHEST_PROTOCOL)
	if graphname not in rc['graphs']:
		rc['graphs'][graphname]={'index':graph_index}
	else:	
		rc['graphs'][graphname]['index']=graph_index
# 	print("test node record-->",graph_index['nodes'].loc[[0,2]].to_dict())
# 	print("test edge record-->",graph_index['edges'].loc[[0,2]].to_dict())

def kickoff():
	standoff_base=4
	standoff_count=0
	st=time.time()
	while True:
		failures_count=0
		print('BUILDING GRAPHS')
		for rcname in rcnames:
			for graph_params in registered_caches[rcname]['graph_params']:
				graphname=graph_params['name']
				load_index(rcname,graphname)
		print("failed on %d of %d caches" %(failures_count,len(rcnames)))
		if failures_count>=len(rcnames):
			standoff_time=standoff_base**standoff_count
			print("retrying after %d seconds" %(standoff_time))
			time.sleep(standoff_time)
			standoff_count+=1
		else:
			break
	print("finished building graphs in %d seconds" %int(time.time()-st))

#on initialization, load every index as a graph, via a call to the django api
registered_caches={
	'ao_maps':ao_maps,
	'voyage_maps':voyage_maps,
	'estimate_maps':estimate_maps
}

rcnames=list(registered_caches.keys())
kickoff()

@app.route('/network_maps/',methods=['POST'])
def network_maps():
	
	'''
	Accepts itineraries of UUID's with weights attached
	Returns weighted and classed nodes and edges
	'''
	
	st=time.time()
	rdata=request.json
	cachename=rdata['cachename']
	graphname=rdata['graphname']
	
	pks=rdata['pks']
	
	nodes=registered_caches[cachename]['graphs'][graphname]['index']['nodes']
	aggedges=registered_caches[cachename]['graphs'][graphname]['index']['edges'].copy()
	nodesdata=registered_caches[cachename]['graphs'][graphname]['index']['nodesdata']
	edgesdata=registered_caches[cachename]['graphs'][graphname]['index']['edgesdata']
	
	aggnodes=nodes[nodes['pk'].isin(pks)].drop(columns=(['pk'])).groupby('id').agg('sum')
	
	finalnodes=[
		{	
			'id':row_id,
			'data':nodesdata[row_id],
			'weights':{
				'origin':int(row['origin']),
				'embarkation':int(row['embarkation']),
				'disembarkation':int(row['disembarkation']),
				'post_disembarkation':int(row['post-disembarkation'])
			}
		}
		for row_id,row in aggnodes.iterrows()
		if row_id in nodesdata
	]
	
	## HAVE TO DROP EDGES WHERE WEIGHT IS ZERO BEFORE I DO THE BELOW:
	
	aggedges=aggedges[aggedges['weight']>0]
	aggedges=aggedges[aggedges['pk'].isin(pks)]
	
# 	print("unique pks",len(aggedges['pk'].unique()))
	
	aggedges['c1x']=aggedges['c1x']*aggedges['weight']
	aggedges['c2x']=aggedges['c2x']*aggedges['weight']
	aggedges['c1y']=aggedges['c1y']*aggedges['weight']
	aggedges['c2y']=aggedges['c2y']*aggedges['weight']
	
	aggedges=aggedges.drop(columns=(['pk'])).groupby(['source','target']).agg('sum').reset_index()
	
	aggedges['c1x']=aggedges['c1x']/aggedges['weight']
	aggedges['c2x']=aggedges['c2x']/aggedges['weight']
	aggedges['c1y']=aggedges['c1y']/aggedges['weight']
	aggedges['c2y']=aggedges['c2y']/aggedges['weight']
	
	finaledges=[
		{
			'source':row['source'],
			'target':row['target'],
			'weight':row['weight'],
			'controls':[[row['c1x'],row['c1y']],[row['c2x'],row['c2y']]],
			'type':edgesdata['__'.join([str(row['source']),str(row['target'])])]['type']
		} for row_id,row in aggedges.iterrows()
	]
	
# 	for node in finalnodes:
# 		print(node)
	
	return(jsonify({'nodes':finalnodes,'edges':finaledges}))

@app.route('/rebuild_indices/<indexname>', methods=['GET'])
@login_required
def rebuild_index(indexname):
	
	if not os.path.exists(TMP_PATH):
		os.makedirs(TMP_PATH)
	
	picklepath=f"{TMP_PATH}/{indexname}.pickle"
# 	"tmp/"+indexname+".pickle"
	if os.path.exists(picklepath):
		os.remove(picklepath)
	rcname,graphname=indexname.split("__")
	load_index(rcname,graphname)
	time.sleep(2)
	return redirect('/displayindices')

@app.route('/displayindices', methods=['GET'])
@login_required
def displayindices():
	if not os.path.exists(TMP_PATH):
		os.makedirs(TMP_PATH)

	indices=[
		[
			'__'.join([rcname,graph_params['name']]),
			os.path.exists(TMP_PATH+"/"+'__'.join([rcname,graph_params['name']])+".pickle")
		] for rcname in rcnames
		for graph_params in registered_caches[rcname]['graph_params']
	]
	return render_template(
		'displayindices.html',
		indices=indices
	)
    # Here we use a class of some kind to represent and validate our

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		pw = request.form['password']
		if pw == PW and username in USER_NAMES:
			# Login and validate the user.
			# user should be an instance of your `User` class
			login_user(USER_NAMES[username])
			flash('Logged in successfully.')
			return redirect('/displayindices')
	return render_template('login.html')