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
	if r.status_code!=200:
		print("failed on OPTIONS call...")
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

standoff_base=4
standoff_count=0
while True:
	failures_count=0
	for rc in registered_caches:
		endpoint=rc['endpoint']
		variables=rc['variables']
		try:
			rc['df']=load_long_df(endpoint,variables)
		except:
			failures_count+=1
			print("failed on cache:",rc['name'])
	print("failed on %d of %d caches" %(failures_count,len(registered_caches)))
	if failures_count==len(registered_caches):
		standoff_time=standoff_base**standoff_count
		print("retrying after %d seconds" %(standoff_time))
		time.sleep(standoff_time)
		standoff_count+=1
	else:
		break

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
# 	print(df2,df2[groupby_cols[0]].unique())
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

@app.route('/crosstabs/',methods=['POST'])
def crosstabs():
	
	'''
	Implements the pandas crosstab function and returns the sparse summary.
	Excellent for pivot tables and maps (e.g., Origin/Destination pairs for voyages with summary values for those pairs)
	Is my solution below (raw html) elegant? No.
	Is that the point? No! Consider that the slavevoyages tables
		1. aren't true pivot tables (can't group rows)
		2. don't even work right now (row header is wrong)
	Recommend using something like this to paginate the bulky html: https://jsfiddle.net/u9d1ewsh/
	And other on-page jquery handlers for column sorting, sankey & map popups, column & row collapsing, etc.
	Unfortunately, I haven't figured out how to do this for less than 10MB and 5 seconds if I style the html dump at all
	--> so for now at least it'll have to be on-page jquery indexing?
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
	
	print("columns",columns)

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
	
# 	print("splitem",[df2[col] for col in columns])
	
	ct=pd.crosstab(
		[df2[rows[0]]],
		[df2[col] for col in columns],
		values=df2[val].astype('Int64'),
		aggfunc=eval("np."+fn),
		normalize=normalize,
		margins=True
	)
	
# 	print("crosstabs",ct)
	
	if len(columns)==1:
		mlctuples=[[i] for i in list(ct.columns)]
	else:
		mlctuples=list(ct.columns)
	
# 	print("tuples",mlctuples)
	
	def makechild(name,isfield=False,columngroupshow=False,key=None):
		if columngroupshow:
			cgsval="open"
		else:
			cgsval="closed"
		if isfield:
			##N.B. "All" is a reserved column name here, for the margins/totals
			### IN OTHER WORDS, NO VALUE FOR A COLUMN IN THE DF CAN BE "ALL"
			if type(key) in [list,tuple]:
				if key[0]=='All':
					key='All'
				else:
					key='__'.join(key)
			
			child={
				"columnGroupShow":cgsval,
				"headerName":name,
				"field":key,
				"filter": 'agNumberColumnFilter',
				"sort": 'desc'
			}
			if key=='All':
				child['pinned']='right'
		else:
			child={
				"headerName":name,
				"children":[]
			}
		return child
		
	##N.B. "All" is a reserved column name here, for the margins/totals
	### IN OTHER WORDS, NO VALUE FOR A COLUMN IN THE DF CAN BE "ALL"
	def makecolgroups(colgroups,mlct,fullpath):
		k=mlct.pop()
		if k is not None:
			if len(mlct)>0 and k!= 'All':
				headernames=[cg['headerName'] for cg in colgroups]
				if k not in headernames:
					thiscg=makechild(k,isfield=False)
					colgroups.append(thiscg)
				else:
					thiscg=[cg for cg in colgroups if cg['headerName']==k][0]
				thiscg_idx=colgroups.index(thiscg)
				colgroups[thiscg_idx]['children']=makecolgroups(thiscg['children'],mlct,fullpath)
			elif k=='All':
				##N.B. "All" is a reserved column name here, for the margins/totals
				thiscg=makechild('',isfield=False)
				thisfield=makechild(k,isfield=True,key=fullpath)
				thiscg['children'].append(thisfield)
				colgroups.append(thiscg)
			else:
				thisfield=makechild(k,isfield=True,key=fullpath)
				colgroups.append(thisfield)
		return colgroups
	
	colgroups=[]
	indexcol_varname=rows[0]
	if 'rows_label' in rdata:
		indexcol_name=rdata['rows_label'][0]
	else:
		indexcol_name=''
	indexcolcg=makechild('',isfield=False)
	indexcolfield=makechild(indexcol_name,isfield=True,key=indexcol_name)
	indexcolfield['pinned']='left'
	indexcolcg['children'].append(indexcolfield)
	colgroups.append(indexcolcg)
	
	for mlct in mlctuples:
		l=list(mlct)
		l.reverse()
		colgroups=makecolgroups(colgroups,l,mlct)
	
	records=[]
	##N.B. "All" is a reserved column name here, for the margins/totals
	### IN OTHER WORDS, NO VALUE FOR A COLUMN IN THE DF CAN BE "ALL"
	allcolumns=["__".join(c) if c[0]!='All' else 'All' for c in mlctuples]
	allcolumns.insert(0,indexcol_name)
	print(len(ct.to_records()[0]),len(allcolumns))
	ct=ct.fillna(0)
	for r in ct.to_records():
		thisrecord={allcolumns[i]:r[i] for i in range(len(r))}
		records.append(thisrecord)
	
	output={'tablestructure':colgroups,'data':records}
	return json.dumps(output)

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