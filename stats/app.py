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

def load_long_df(endpoint,variables,options):
	headers={'Authorization':DJANGO_AUTH_KEY,'Content-Type': 'application/json'}
	r=requests.post(
		url=DJANGO_BASE_URL+endpoint,
		headers=headers,
		data=json.dumps({'selected_fields':variables,'filter':[]})
	)
	j=json.loads(r.text)
	df=pd.DataFrame.from_dict(j)
	#coerce datatypes based on options call
	for varName in variables:
		optionsvar=options[varName]
		vartype=optionsvar['type']	
		if vartype in [
			"integer",
			"number"
		]:
			df[varName]=pd.to_numeric(df[varName])
	return(df)

registered_caches=[
	voyage_bar_and_donut_charts,
	voyage_summary_statistics,
	voyage_pivot_tables,
	voyage_xyscatter,
	estimate_pivot_tables
]

#on initialization, load every index as a dataframe, via a call to the django api
st=time.time()

standoff_base=4
standoff_count=0
while True:
	failures_count=0
	for rc in registered_caches:
		time.sleep(1)
		#pull the index keys from the index_vars.py file
		#and load each cache based on the parameters it sets out
		endpoint=rc['endpoint']
		variables=rc['variables']
		schema_name=rc['schema_name']
		headers={'Authorization':DJANGO_AUTH_KEY,'Content-Type': 'application/json'}
		#before we make the dataframes call, we need to get the schema data
		#via an options call to the django server
		#because this will allow us to coerce the propert data types (numeric or categorical)
		#in order to make the math work out properly later!
		try:
			r=requests.get(url=DJANGO_BASE_URL+'common/schemas/?schema_name=%s&hierarchical=False' %schema_name,headers=headers)
			options=json.loads(r.text)
			rc['options']=options
			rc['df']=load_long_df(endpoint,variables,options)
			print(rc['df'])
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
	dfname=rdata['cachename']
	ids=rdata['ids']
	groupby_by=rdata['groupby_by']
	groupby_cols=rdata['groupby_cols']
	agg_fn=rdata['agg_fn']
	df=eval(dfname)['df']
	df2=df[df['id'].isin(ids)]
	ct=df2.groupby(groupby_by,group_keys=True)[groupby_cols].agg(agg_fn)
	ct=ct.fillna(0)
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


def interval_to_str(s):
	s=str(s)
	return re.sub('[\s,]+','-',re.sub('[\[\]]','',s))

def makestr(s):
	if s is None:
		return "Unknown"
	else:
		return str(s)


@app.route('/pivot/',methods=['POST'])
def pivot():

	'''
	We cannot implement multi-level rows in AG Grid
		1. because it's in the enterprise version
		2. because it's ugly
	It is possible that this is the implementation I was looking for all along.
	'''
	st=time.time()
	rdata=request.json
	dfname=rdata['cachename']
	ids=rdata['ids']
	rows=rdata['rows']
	cols=rdata['cols']
	vals=rdata['vals']
	binsize=rdata.get('binsize')
	mode=rdata['mode']
	
	df=eval(dfname)['df']
	
	#filter down on the pk's
	pv=df[df['id'].isin(ids)]
	
	pv=pv.fillna(0)
	
	#force ints
	for val in vals:
		pv[val]=pv[val].astype('int')
	
	#if we are binning, then rows should only have one varname
	#and that var should be numeric
	if binsize is not None:
		rows=rows[0]
		binsize=int(binsize)
		pv[rows]=pv[rows]
		pv[rows]=pv[rows].astype('int')
		binvar_min=pv[rows].min()
		binvar_max=pv[rows].max()
		binvar_ints=list(range(int(binvar_min),int(binvar_max)+1))
		if binvar_max-binvar_min <=binsize:
			nbins=1
		else:
			nbins=int((binvar_max-binvar_min)/binsize)
		bin_arrays=np.array_split(binvar_ints,nbins)
		bins=pd.IntervalIndex.from_tuples([(i[0],i[-1]) for i in bin_arrays],closed='both')
		pv=pv.assign(row_bins=pd.cut(df[rows],bins,include_lowest=True))
		pv=pv[cols+vals+['row_bins']]
		pv.rename(columns={"row_bins": rows})
		pv['row_bins']=pv['row_bins'].astype('str')
		pv['row_bins']=pv['row_bins'].apply(interval_to_str)
		rows='row_bins'
	#pivot
	
	
	if len(vals)==1:
		vals=vals[0]
		split_cells=False
	else:
		split_cells=True
	
	pv=pv.pivot_table(
		columns=cols,
		index=rows,
		values=vals,
		aggfunc="sum"
	)
	
	#if we're doing split cells
	#pandas puts the values on top -- flip it to get split cells
	if split_cells:
		cl=len(cols)
		if cl==1:
			pv=pv.swaplevel(0,len(cols),axis=1).sort_index(axis=1)
		elif cl==2:
			#there's got. to be. a better. way.
			pv=pv.swaplevel(0,1,axis=1).sort_index(axis=1)
			pv=pv.swaplevel(1,2,axis=1).sort_index(axis=1)
	
	pv=pv.fillna(0)
	html=pv.to_html(index_names=False)
	html=re.sub('\\n\s+','',html)
	return json.dumps(
		{
			"data":html
		}
	)


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
	dfname=rdata.get('cachename')
# 	dfname='voyage_pivot_tables'
	#it must have a list of ids (even if it's all of the ids)
	ids=rdata['ids']

	#and a 2ple for groupby_fields to give us rows & columns (maybe expand this later)
	columns=rdata.get('columns')
	rows=rdata.get('rows')
	val=rdata.get('value_field')
	fn=rdata.get('agg_fn')
	limit=rdata.get('limit') or 10
	offset=rdata.get('offset') or 0
	binsize=rdata.get('binsize')
	order_by=rdata.get('order_by')
	if order_by is not None:
		ascending=True
		order_by=order_by[0]
		if order_by.startswith("-"):
			ascending=False
			order_by=order_by[1:]
		order_by_list=order_by.split('__')
		order_by_list=tuple(order_by_list)
		
	normalize=rdata.get('normalize')
	if normalize is not None:
		normalize=normalize[0]
	if normalize not in ["columns","index"]:
		normalize=False
	
	df=eval(dfname)['df']
	options=eval(dfname)['options']
	df=df[df['id'].isin(ids)]
	
	yeargroupmode=False
	
	def interval_to_str(s):
		s=str(s)
		return re.sub('[\s,]+','-',re.sub('[\[\]]','',s))

	def makestr(s):
		if s is None:
			return "Unknown"
		else:
			return str(s)

	valuetype=options[val]['type']
	
	##TBD --> NEED TO VALIDATE THAT THE ROWS VARIABLE IS
	####1) NUMERIC TO WORK IN THE FIRST PLACE
	####2) A YEAR VAR IN ORDER TO MAKE SENSE TO A HUMAN END-USER
	if binsize is not None:
		binsize=int(binsize)
		yeargroupmode=True
		df=df.dropna(subset=[rows,val])
		df[rows]=df[rows].astype('int')
		year_min=df[rows].min()
		year_max=df[rows].max()
		year_ints=list(range(int(year_min),int(year_max+1)))
		if year_max-year_min <= binsize:
			nbins=1
		else:
			nbins=int((year_max-year_min)/binsize)
		bin_arrays=np.array_split(year_ints,nbins)
		bins=pd.IntervalIndex.from_tuples([(i[0],i[-1]) for i in bin_arrays],closed='both')
		df=df.assign(row_bins=pd.cut(df[rows],bins,include_lowest=True))
		df=df[columns+[val]+['row_bins']]
		df.rename(columns={"row_bins": rows})
		df['row_bins']=df['row_bins'].astype('str')
		df[val]=df[val].astype('int')
		df['row_bins']=df['row_bins'].apply(interval_to_str)
		ct=pd.crosstab(
			[df['row_bins']],
			[df[col] for col in columns],
			values=df[val],
			aggfunc=fn,
			margins=True
		)
		ct.fillna(0)
	else:
		ct=pd.crosstab(
			[df[rows]],
			[df[col] for col in columns],
			values=df[val],
			aggfunc=fn,
			normalize=normalize,
			margins=True
		)
		ct.fillna(0)
	
	if order_by is not None:
		ct=ct.sort_values(by=order_by_list,ascending=ascending)
	
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
# 					key=re.sub('\.','','__'.join(key))
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
	indexcol_name=rdata.get('rows_label') or ''
	indexcolcg=makechild('',isfield=False)
	indexcolfield=makechild(indexcol_name,isfield=True,key=indexcol_name)
	indexcolfield['pinned']='left'
	indexcolcg['children'].append(indexcolfield)
	colgroups.append(indexcolcg)
	
	for mlct in mlctuples:
		l=list(mlct)
		l.reverse()
		colgroups=makecolgroups(colgroups,l,mlct)
	
	output_records=[]
	##N.B. "All" is a reserved column name here, for the margins/totals
	### IN OTHER WORDS, NO VALUE FOR A COLUMN IN THE DF CAN BE "ALL"
# 	allcolumns=[re.sub('\.','',"__".join(c)) if c[0]!='All' else 'All' for c in mlctuples]
	allcolumns=["__".join(c) if c[0]!='All' else 'All' for c in mlctuples]
	allcolumns.insert(0,indexcol_name)
	ct=ct.fillna(0)
	
# 	print(ct)
	
	def convertcell(cellval,valuetype):
		if valuetype == "number":
			return float(cellval)
		elif valuetype=="integer":
			return int(cellval)
	
	ctshape=ct.shape
# 	print(ctshape)
	rowcount=ctshape[0]	
	start=offset
	end=min((offset+limit),rowcount-1)
	
	ct=ct.iloc[start:end,]
	ct_records=ct.to_records()
	
	for r in ct_records:	
		for i in range(len(r)):
			if i==0:
				thisrecord={
					allcolumns[i]:(
						convertcell(r[i],valuetype) if i!=0 else r[i]
					)
					for i in range(len(r))
				}
		output_records.append(thisrecord)
	
	
	
	output={
		'tablestructure': colgroups,
		'data': output_records,
		'metadata':{
			'total_results_count': rowcount,
			'offset':offset,
			'limit':limit
		}
	}
	
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