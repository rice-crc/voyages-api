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
	estimate_pivot_tables,
	timelapse
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
		rcname=rc['name']
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
			thisdf=load_long_df(endpoint,variables,options)
			
			#timelapse needs is na entries filled ahead of time
			if rcname=='timelapse':
				for varName in variables:
					optionsvar=options[varName]
					vartype=optionsvar['type']	
					if vartype in [
						"integer",
						"number"
					]:
						thisdf[varName]=thisdf[varName].fillna(0)
						thisdf[varName]=thisdf[varName].astype('int')
					else:
						thisdf[varName]=thisdf[varName].fillna('')
			rc['df']=thisdf
			print(rc['df'])
		except:
			failures_count+=1
			print("failed on cache:",rcname)
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


@app.route('/timelapse/',methods=['POST'])
def timelapse_animation():

	'''
	https://www.slavevoyages.org/voyage/database#timelapse
	'''
	st=time.time()
	rdata=request.json
	ids=rdata['ids']
	df=eval('timelapse')['df']
	df=df[df['id'].isin(ids)]
	
	colname_map={'id': 'voyage_id', 'voyage_ship__imputed_nationality__id':'nat_id','voyage_itinerary__imp_principal_place_of_slave_purchase__id': 'src', 'voyage_itinerary__imp_principal_port_slave_dis__id': 'dst', 'voyage_itinerary__imp_principal_region_of_slave_purchase__id': 'regsrc', 'voyage_itinerary__imp_broad_region_of_slave_purchase__id': 'bregsrc', 'voyage_itinerary__imp_principal_region_slave_dis__id': 'regdst', 'voyage_itinerary__imp_broad_region_slave_dis__id': 'bregdst', 'voyage_slaves_numbers__imp_total_num_slaves_embarked': 'embarked', 'voyage_slaves_numbers__imp_total_num_slaves_disembarked': 'disembarked', 'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year': 'year', 'voyage_dates__imp_arrival_at_port_of_dis_sparsedate__month': 'month', 'voyage_ship__tonnage_mod': 'ship_ton', 'voyage_ship__imputed_nationality__name': 'nat_id', 'voyage_ship__ship_name': 'ship_name'}
	
	df=df.rename(columns=colname_map)
	print(df)
	return df.to_json(orient="records")

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
		return {
			k: v for k, v in a if not self.is_nan(v) and v!={}
		}


def interval_to_str(s):
	s=str(s)
	return re.sub('[\s,]+','-',re.sub('[\[\]]','',s))

def makestr(s):
	if s is None:
		return "Unknown"
	else:
		return str(s)

@app.route('/voyage_summary_stats/',methods=['POST'])
def voyage_summary_stats():

	'''
	https://www.slavevoyages.org/voyage/database#statistics
	'''
	st=time.time()
	rdata=request.json
	ids=rdata['ids']
	df=eval('voyage_summary_statistics')['df']
	
	imputed_rows={
		'voyage_slaves_numbers__imp_total_num_slaves_embarked':'Captives embarked (Imputed)',
		'voyage_slaves_numbers__imp_total_num_slaves_disembarked':'Captives disembarked (Imputed)',
	}
	non_imputed_rows={
		'voyage_slaves_numbers__imp_mortality_ratio':'Percentage of captives embarked who died during crossing',
		'voyage_dates__length_middle_passage_days':"Duration of captives' crossing (in days)",
		'voyage_slaves_numbers__percentage_male':'Percentage male',
		'voyage_slaves_numbers__percentage_female':'Percentage female',
		'voyage_slaves_numbers__percentage_child':'Percentage children',
		'voyage_ship__tonnage_mod':'Tonnage of vessel'
	}
	
	#filter down on the pk's
	df=df[df['id'].isin(ids)]
	outputrecords=[]
	
	theaders=[
		''
		'Total captives',
		'Total voyages with this datapoint'
		'Average',
		'Median',
		'Standard deviation'
	]
	
	percentagerowkeys=[
		'voyage_slaves_numbers__imp_mortality_ratio',
		'voyage_slaves_numbers__percentage_male',
		'voyage_slaves_numbers__percentage_child',
		'voyage_slaves_numbers__percentage_female'
	]
	
	for k in imputed_rows:
		v=imputed_rows[k]
		record={'index':v}
		record['Total captives']=f'{int(df[k].sum()):,}'
		record['Total voyages with this datapoint']=f'{int(df[k].dropna().shape[0]):,}'
		record['Average']=str(round(df[k].mean(),1))
		record['Median']=str(round(df[k].median(),1))
		record['Standard deviation']=str(round(df[k].std(),1))
		outputrecords.append(record)
	
	for k in non_imputed_rows:
		v=non_imputed_rows[k]
		record={'index':v}
		record['Total captives']=''
		record['Total voyages with this datapoint']=f'{int(df[k].dropna().shape[0]):,}'
		
		average=df[k].mean()
		median=df[k].median()
		std=df[k].std()
		if k in percentagerowkeys:
			average=str(round(average*100,1))
			median=str(round(median*100,1))
			std=str(round(std*100,1))
			
			average=f'{average}%'
			median=f'{median}%'
			std=f'{std}%'
		else:
			average=str(round(average,1))
			median=str(round(median,1))
			std=str(round(std))
			
		record['Average']=average
		record['Median']=median
		record['Standard deviation']=std
		outputrecords.append(record)
	
	headers=[
		'Total captives',
		'Total voyages with this datapoint',
		'Average',
		'Median',
		'Standard deviation'
	]
	
	headertablerow="".join([f'<th>{h}</th>' for h in headers])
	
	headertablerowhtml=f'<thead><tr style="text-align: right;"><th></th>{headertablerow}</tr></thead>'
	
	rowshtml=''
	
	for r in outputrecords:
		indexname=r['index']
		row="".join([f'<td>{r[h]}</td>' for h in headers])
		rowhtml=f"<tr><td>{indexname}</td>{row}</tr>"
		rowshtml+=rowhtml
	
	table=f'<table border="1" class="dataframe">{headertablerowhtml}{rowshtml}</table>'
	
	outputrecords.append(record)
	
	return json.dumps(
		{
			"data":table
		}
	)

@app.route('/estimates_pivot/',methods=['POST'])
def estimates_pivot():

	'''
	We cannot implement multi-level rows in AG Grid
		1. because it's in the enterprise version
		2. because it's ugly
	It is possible that this is the implementation I was looking for all along.
	'''
	st=time.time()
	rdata=request.json
	ids=rdata['ids']
	rows=rdata['rows']
	cols=rdata['cols']
	vals=rdata['vals']
	binsize=rdata.get('binsize')
	mode=rdata['mode']
	
	df=eval('estimate_pivot_tables')['df']
	
	#filter down on the pk's
	pv=df[df['id'].isin(ids)]
	
	if len(pv)==0:
		
		html="<table border=\"1\"><tr><td>No results.</td></tr></table>"
		
	else:
	
		pv=pv.fillna(0)
		
		#force ints
		for val in vals:
			pv[val]=pv[val].astype('int')
		
		#handle a duplicate varname request like
		#rows=['nation__name'],cols=['nation__name']
		#which is dumb, because who wants a diagonal matrix???
		duplicate_indices=[i for i in cols if i in rows]
		c=1
		for duplicate_index in duplicate_indices:
			duplicate_position=cols.index(duplicate_index)
			pv=eval(f'pv.assign(duplicate_col_{c}=pv[duplicate_index])')
			cols[duplicate_position]=f'duplicate_col_{c}'
			c+=1
		
		#if we are binning, then rows should only have one varname
		#and that var should be numeric
		if binsize is not None:
			rows=rows[0]
			binsize=int(binsize)
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
			aggfunc="sum",
			margins=True
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
			colnames_list=pv.columns.tolist()
			all_column_embark_position=colnames_list.index(('All', 'embarked_slaves'))
			del(colnames_list[all_column_embark_position])
			colnames_list.append(('All', 'embarked_slaves'))
			all_column_disembark_position=colnames_list.index(('All', 'disembarked_slaves'))
			del(colnames_list[all_column_disembark_position])
			colnames_list.append(('All', 'disembarked_slaves'))
			pv=pv[colnames_list]
			
		
		pv=pv.fillna(0)
		html=pv.to_html(index_names=False)
		html=re.sub('\\n\s+','',html)
		html=re.sub("disembarked_slaves","Disembarked",html)
		html=re.sub("embarked_slaves","Embarked",html)
		html=re.sub("\.0","",html)
	return json.dumps(
		{
			"data":html
		}
	)


@app.route('/estimates_timeline/',methods=['POST'])
def estimates_timeline():

	'''
	Implements the pandas groupby function and returns the sparse summary.
	Excellent for bar & pie charts.
	'''
	st=time.time()
	rdata=request.json
	ids=rdata['ids']
	df=eval('estimate_pivot_tables')['df']
	cols=['disembarked_slaves','embarked_slaves']
	df2=df[df['id'].isin(ids)]
	ct=df2.groupby('year',group_keys=True)[cols].agg('sum')
	ct=ct.fillna(0)
	resp={'year':list(ct.index)}
	for col in cols:
		resp[col]=list(ct[col])
	return json.dumps(resp)


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