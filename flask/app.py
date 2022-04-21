import time
from flask import Flask,jsonify,request
import pandas as pd
import numpy as np
import json
import math
import requests

app = Flask(__name__)

def load_long_df(idx_url):
	r=requests.get(idx_url)
	j=json.loads(r.text)
	headers=j['ordered_keys']
	d2={h:[] for h in headers}
	for h in headers:
		for item in j['items']:
			d2[h].append(j['items'][item][headers.index(h)])
	df=pd.DataFrame.from_dict(d2)
	return(df)

#on initialization, load every index as a dataframe, via a call to the django api's static assets

##HARD-CODED URL
voyage_export=load_long_df('http://voyages-django:8000/static/customcache/voyage_export.json')

#Implementing this as a limited pivot table with some weird twists at the end to replicate legacy functionality
##first series is the rows of course
##only one column, however (at least for now)
##### with the exception of binning -- we'll allow a column for that on numeric variables
##then a tuple giving you one value and a function to apply on top of it
###n.b. this would remove the embarked/disembarked split view on the pivot table (but it's fast enough to allow that to just be a toggle)
##this allows us to use it as well as:
###a groupby function
#####non-tabular if you use rmna="All"
###a normalized (percentages) table
##& to apply binning -- which I'm going to require is expressed as a simple integer of the number of bins. making that friendly is a ui question.

@app.route('/',methods=['POST'])
def pivot_groupby():
	st=time.time()
	rdata=request.json
	
	#print(rdata)
	
	dfname='voyage_export'
	
	#it must have a list of ids (even if it's all of the ids)
	ids=rdata['ids']
	
	#and a 2ple for groupby_fields to give us rows & columns (maybe expand this later)
	columns,rows=rdata['groupby_fields']
	val,fn=rdata['value_field_tuple']
	
	removeallNA=False
	rmna=rdata.get('rmna')
	
	if rmna is not None:
		rmna=rmna[0]
	
	if rmna in ["True",True]:
		rmna=True
	elif rmna in ["all","All"]:
		rmna=False
		removeallNA=True
	
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
	
	#https://pandas.pydata.org/docs/user_guide/reshaping.html#reshaping-crosstabulations
	ct=pd.crosstab(
		df2[columns],
		df2[rows],
		values=df2[val],
		aggfunc=eval("np."+fn),
		normalize=normalize,
		dropna=rmna
	)
	
	if removeallNA:
		#https://stackoverflow.com/questions/26033301/make-pandas-dataframe-to-a-dict-and-dropna
		ctd={col: ct[col].dropna().to_dict() for col in ct.columns}
	else:
		ctd=ct.to_dict()
	
	return jsonify(ctd)