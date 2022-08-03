import time
from flask import Flask,jsonify,request,abort
import pandas as pd
import numpy as np
import json
import math
import requests
from localsettings import *
import re

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def load_long_df(idx_url):
	r=requests.get(idx_url)
	j=json.loads(r.text)
	
	voyage_url=re.sub("/static/","/voyage/?hierarchical=False",DJANGO_STATIC_URL)
	r=requests.options(url=voyage_url,headers=headers)
	voyage_options=json.loads(r.text)
	colnames=j['ordered_keys']
	d2={h:[] for h in colnames}
	for h in colnames:
		for item in j['items']:
			thisitem=j['items'][item][colnames.index(h)]
			if "DecimalField" in voyage_options[h]['type'] and thisitem is not None:
				thisitem=float(thisitem)
			d2[h].append(thisitem)
	df=pd.DataFrame.from_dict(d2)
	
	return(df)

#on initialization, load every index as a dataframe, via a call to the django api's static assets

registered_caches=[
	'voyage_bar_and_donut_charts',
	'voyage_maps',
	'voyage_summary_statistics',
	'voyage_pivot_tables',
	'voyage_xyscatter',
	'voyage_export'
]

for rc in registered_caches:
	print("loading %s" %rc)
	xl="%s=load_long_df(\"" %rc + DJANGO_STATIC_URL + "customcache/%s.json\")" %rc
	exec(xl)

@app.route('/groupby/',methods=['POST'])
def groupby():
	
	'''
	Implements the pandas groupby function and returns the sparse summary.
	Excellent for bar & pie charts.
	'''
	
	try:
		st=time.time()
		rdata=request.json
		dfname=rdata['cachename'][0]
		ids=rdata['ids']
		groupby_fields=rdata['groupby_fields']
		groupby_row=groupby_fields[0]
		groupby_cols=groupby_fields[1:len(groupby_fields)]
		agg_fn=rdata['agg_fn'][0]
		df=eval(dfname)
		df2=df[df['id'].isin(ids)]
		ct=df2.groupby(groupby_row)[groupby_cols].agg(agg_fn)
		#js doesn't like nulls/nan's
		#changing at Zhihao's request
		ct=ct.fillna(0)
		ctd=ct.to_dict()
		return jsonify(ctd)
	except:
		abort(400)

@app.route('/crosstabs/',methods=['POST'])
def crosstabs():
	
	'''
	Implements the pandas crosstab function and returns the sparse summary.
	Excellent for pivot tables and maps (e.g., Origin/Destination pairs for voyages with summary values for those pairs)
	'''

	try:
		st=time.time()
		rdata=request.json
		dfname=rdata['cachename'][0]

		#it must have a list of ids (even if it's all of the ids)
		ids=rdata['ids']

		#and a 2ple for groupby_fields to give us rows & columns (maybe expand this later)
		columns,rows=rdata['groupby_fields']
		val,fn=rdata['value_field_tuple']

		normalize=rdata.get('normalize')
		if normalize is not None:
			normalize=normalize[0]
		if normalize not in ["columns","index"]:
			normalize=False

		df=eval(dfname)

		df2=df[df['id'].isin(ids)]

		bins=rdata.get('bins')
		if bins is not None:
			binvar,nbins=[bins[0],int(bins[1])]
			df2=pd.cut(df2[binvar],nbins)
		ct=pd.crosstab(
			df2[columns],
			df2[rows],
			values=df2[val],
			aggfunc=eval("np."+fn),
			normalize=normalize,
		)
		ctd={col: ct[col].dropna().to_dict() for col in ct.columns}
		return jsonify(ctd)
	except:
		abort(400)

@app.route('/dataframes/',methods=['POST'])
def dataframes():
	
	'''
	Allows you to select long-format columns of data on any (indexed) selected field.
	Excellent for a data export or any general dataframe use-case.
	'''
	
	try:
		st=time.time()
	
		rdata=request.json
	
		dfname=rdata['cachename'][0]
		df=eval(dfname)
		ids=rdata['ids']
		df2=df[df['id'].isin(ids)]
		columns=list(set(rdata['selected_fields']+['id']))
		df2=df2[[c for c in columns]]
		df3=df2.set_index('id')
		df3=df3.reindex(ids)
		df3=df3.fillna(0)
		j3=df3.to_dict()
	
		return jsonify(j3)
	except:
		abort(400)