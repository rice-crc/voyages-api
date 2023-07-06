import time
from flask import Flask,jsonify,request,abort
import pandas as pd
import numpy as np
import json
import math
import requests
from localsettings import *
from index_vars import *
import re

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def load_long_df(endpoint,variables):
	headers={'Authorization':DJANGO_AUTH_KEY}
	r=requests.options(url=DJANGO_BASE_URL+'voyage/dataframes?hierarchical=False',headers=headers)
	options=json.loads(r.text)
	print("OPTIONS----->",r.status_code)
		
	r=requests.post(
		url=DJANGO_BASE_URL+endpoint,
		headers=headers,
		data={'selected_fields':variables}
	)
	j=json.loads(r.text)
	df=pd.DataFrame.from_dict(j)
	#coerce datatypes based on options call
	for varname in variables:
		optionsvar=options[varname]
		vartype=optionsvar['type']
		if vartype in [
			"<class 'rest_framework.fields.IntegerField'>",
			"<class 'rest_framework.fields.FloatField'>",
			"<class 'rest_framework.fields.DecimalField'>"
		]:
			df[varname]=pd.to_numeric(df[varname])
			
	print(df)
	
	return(df)

registered_caches=[
	voyage_bar_and_donut_charts,
# 	voyage_maps,
# 	enslaved_maps,
	voyage_summary_statistics,
	voyage_pivot_tables,
	voyage_xyscatter
]

#on initialization, load every index as a dataframe, via a call to the django api
st=time.time()
for rc in registered_caches:
# 	try:
	endpoint=rc['endpoint']
	variables=rc['variables']
	rc['df']=load_long_df(endpoint,variables)
# 	except:
# 		print("failed on cache:",rc['name'])
print("finished building stats indices in %d seconds" %int(time.time()-st))

#we need to make the indices' contents visible
@app.route('/get_indices/')
def get_indices():
	resp={}
	for rc in registered_caches:
		resp[rc['name']]=rc['variables']
	return json.dumps(resp)

@app.route('/groupby/',methods=['POST'])
def groupby():

	'''
	Implements the pandas groupby function and returns the sparse summary.
	Excellent for bar & pie charts.
	'''
	st=time.time()
	rdata=request.json
	dfname=rdata['cachename'][0]
	ids=rdata['ids']
	groupby_by=rdata['groupby_by'][0]
	groupby_cols=rdata['groupby_cols']
	agg_fn=rdata['agg_fn'][0]
	df=eval(dfname)['df']
	df2=df[df['id'].isin(ids)]
	print(df2,df2[groupby_cols[0]].unique())
	ct=df2.groupby(groupby_by,group_keys=True)[groupby_cols].agg(agg_fn)
# 	ct=ct.fillna(0)
	resp={groupby_by:list(ct.index)}
	for gbc in groupby_cols:
		resp[gbc]=list(ct[gbc])
	return json.dumps(resp)

#https://stackoverflow.com/questions/26033301/make-pandas-dataframe-to-a-dict-and-dropna
class NotNanDict(dict):
	@staticmethod
	def is_nan(v):
		if isinstance(v, dict):
			return False
		return np.isnan(v)

	def __new__(self, a):
		return {k: v for k, v in a if not self.is_nan(v) and v!={}} 



@app.route('/crosstabs_maps/',methods=['POST'])
def crosstabs_maps():
	
	'''
	Implements the pandas crosstab function and returns the sparse summary.
	Excellent for pivot tables and maps (e.g., Origin/Destination pairs for voyages with summary values for those pairs)
	'''

# 	try:
	st=time.time()
	rdata=request.json
	dfname=rdata['cachename'][0]

	#it must have a list of ids (even if it's all of the ids)
	ids=rdata['ids']

	df=eval(dfname)['df']
	df=df.fillna('null')
	df2=df[df['id'].isin(ids)]
	idxvar=rdata['idx'][0]
	
	colvars=rdata['cols']
	
	valvar=rdata['value_field'][0]
	
	colsdf=[df2[c] for c in colvars]
	
	idxdf=df2[idxvar]
	
	valdf=df2[valvar]
	
	fn=rdata['agg_fn'][0]
	
	if fn=='count':
		aggfunc='count'
	else:
		aggfunc=eval("np."+fn)
	
	#from https://stackoverflow.com/questions/42150769/pandas-multi-index-dataframe-to-nested-dictionary
	def createDictFromPandas(thisdf):
		if (thisdf.index.nlevels==1):
			return thisdf.to_dict(into=NotNanDict)
		dict_f = {}
		for level in thisdf.index.levels[0]:
			if (level in thisdf.index):
				res=createDictFromPandas(thisdf.xs(level))
				dict_f[level]=createDictFromPandas(thisdf.xs(level))
		return dict_f
	
	ct=pd.crosstab(
		colsdf,
		idxdf,
		values=valdf,
		aggfunc=aggfunc
	)
	
	ct2=createDictFromPandas(ct)
	
	return jsonify(ct2)








@app.route('/crosstabs/',methods=['POST'])
def crosstabs():
	
	'''
	Implements the pandas crosstab function and returns the sparse summary.
	Excellent for pivot tables and maps (e.g., Origin/Destination pairs for voyages with summary values for those pairs)
	'''

# 	try:
	st=time.time()
	rdata=request.json
	dfname=rdata['cachename'][0]

	#it must have a list of ids (even if it's all of the ids)
	ids=rdata['ids']

	#and a 2ple for groupby_fields to give us rows & columns (maybe expand this later)
	columns=rdata['columns']
	rows=rdata['rows']
	val=rdata['value_field'][0]
	fn=rdata['agg_fn'][0]

	normalize=rdata.get('normalize')
	if normalize is not None:
		normalize=normalize[0]
	if normalize not in ["columns","index"]:
		normalize=False

	df=eval(dfname)['df']
	
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
# 	except:
# 		abort(400)

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