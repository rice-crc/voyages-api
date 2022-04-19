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

#HARD-CODED URL
voyage_export=load_long_df('http://voyagesapi-django:8000/static/customcache/voyage_export.json')

@app.route('/',methods=['POST'])
def hello():
	st=time.time()
	rdata=request.json
	dfname='voyage_export'
	ids=rdata['ids']
	groupby_fields=rdata['groupby_fields']
	value_field_tuple=rdata['value_field_tuple']
	df=eval(dfname)
	val,fn=value_field_tuple
	df2=df[df['id'].isin(ids)]
	ct=pd.crosstab(
		df2[groupby_fields[0]],
		df2[groupby_fields[1]],
		values=df2[val],
		aggfunc=eval("np."+fn)
	)
	#https://stackoverflow.com/questions/26033301/make-pandas-dataframe-to-a-dict-and-dropna
	ctd2={col: ct[col].dropna().to_dict() for col in ct.columns}
	return jsonify(ctd2)



