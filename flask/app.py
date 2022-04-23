import time
from flask import Flask,jsonify,request
import pandas as pd
import numpy as np
import json
import math
import requests
from localsettings import *

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


#voyage_export=load_long_df(DJANGO_STATIC_URL+'customcache/voyage_export.json')

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

@app.route('/groupby/',methods=['POST'])
def groupby():
	st=time.time()
	rdata=request.json
	
	#print("------->",rdata)
	dfname=rdata['cachename'][0]
	
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
	
	#print("+++++++++++++++++++")
	#print(columns)
	#print(df2.columns)
	#print("+++++++++++++++++++")

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

@app.route('/dataframes/',methods=['POST'])
def dataframes():
	st=time.time()
	
	rdata=request.json
	
	dfname=rdata['cachename'][0]
	df=eval(dfname)
	
	#it must have a list of ids (even if it's all of the ids)
	#ids=rdata['ids']
	#ids=[1860, 2555, 2559, 2573, 2581, 2582, 2695, 2697, 4229, 4772, 5095, 7501, 9551, 9552, 9553, 9554, 9555, 9556, 9557, 9558, 9559, 9560, 9561, 9563, 9566, 9567, 9568, 9570, 9572, 9575, 9576, 9580, 9581, 9584, 9585, 9590, 9591, 9594, 9595, 9596, 9598, 9602, 9605, 9606, 9607, 9608, 9611, 9616, 9619, 9620, 9621, 9623, 9624, 9625, 9626, 9627, 9630, 9631, 9632, 9633, 9634, 9635, 9636, 9637, 9639, 9640, 9641, 9642, 9644, 9645, 9646, 9652, 9653, 9654, 9655, 9656, 9657, 9659, 9662, 9664, 9665, 9666, 9668, 9669, 9670, 9672, 9673, 9674, 9675, 9676, 9677, 9678, 9679, 9680, 9681, 9682, 9683, 9684, 9687, 9688, 9689, 9690, 9691, 9692, 9693, 9694, 9697, 9698, 9700, 9701, 9702, 9703, 9704, 9706, 9707, 9708, 9709, 9710, 9711, 9712, 9713, 9714, 9716, 9718, 9719, 9720, 9722, 9724, 9725, 9726, 9729, 9730, 9731, 9735, 9736, 9737, 9738, 9739, 9746, 9747, 9749, 9750, 9751, 9752, 9754, 9755, 9756, 9757, 9758, 9759, 9761, 9762, 9764, 9784, 9801, 9808, 9809, 9810, 9811, 9812, 9818, 9819, 9820, 9821, 9823, 9824, 9827, 9828, 9829, 9830, 9831, 9832, 9834, 9836, 9837, 9839, 9840, 9842, 9843, 9844, 9845, 9846, 9847, 9848, 9849, 9850, 9852, 9853, 9854, 9856, 9857, 9858, 9859, 9860, 9861, 9862, 9867, 9868, 9869, 9870, 9871, 9872, 9873, 9874, 9875, 9876, 9877, 9878, 9879, 9880, 9881, 9882, 9883, 9885, 9886, 9887, 9888, 9889, 9893, 9894, 9895, 9897, 9898, 9900, 9901, 9902, 9903, 9904, 9905, 9906, 9909, 9910, 9911, 9912, 9913, 9915, 9916, 9917, 9918]
	
	#we will lock regular accounts out of the full dataframes calls
	#and provide indexed dataframe access like so
	columns=rdata['selected_fields']
	
	df2=df[[c for c in columns]]
	
	return jsonify(df2.to_dict())