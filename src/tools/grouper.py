import pandas as pd
import numpy as np
import json
import math

def load_long_df(filepath):
	d=open(filepath,'r')
	t=d.read()
	d.close()
	j=json.loads(t)
	headers=j['ordered_keys']
	d2={h:[] for h in headers}
	for h in headers:
		for item in j['items']:
			d2[h].append(j['items'][item][headers.index(h)])
	df=pd.DataFrame.from_dict(d2)
	return(df)

voyage_export=load_long_df('./static/customcache/voyage_export.json')





#receives
##the name of a dataframe ("registered" above)
##an array of integer pk's
##row variable names (with a "number_of_bins" option if the datatype is numeric)
##column variable names
##cell variable names
#returns
##well what do you expect?

def pivottable(dfname,ids,rows,columns,cells):
	df=eval(dfname)
	
	






#GROUPBY (SUMS ONLY for now)
##e.g., how many people embarked for all port_embarkation/port_disembarkation pairs in a given year range?
## So the below payload works on this function, as written
#data={
#	'voyage_itinerary__imp_principal_region_slave_dis__region':[
#	'Barbados',
#	'Jamaica'
#	],
#	'groupby_value_fields':['voyage_itinerary__principal_port_of_slave_dis__place','voyage_itinerary__imp_principal_place_of_slave_purchase__place'],
#	'groupby_sum_fields':['voyage_slaves_numbers__imp_total_num_slaves_disembarked']
#}
#receives
##the name of a dataframe ("registered above")
##an array of integer pk's
##value fields (an array of double-underscore-delimited, fully-qualified django (categorical) variable names to group by)
##function tuples (another array of tuples, of the names of numeric variables and the summary functions to be performed on them)

def groupby(dfname,ids,groupby_value_fields,groupby_function_tuples):

	groupby_value_fields=params.get('groupby_value_fields')
	groupby_sum_fields=params.get('groupby_sum_fields')
	
	'''if groupby_value_fields is not None and groupby_sum_fields is not None:
	queryset=eval('queryset.values(%s)' %('\''+'\',\''.join(groupby_value_fields)+'\'')).annotate(sumfield=Sum(groupby_sum_fields[0])).order_by()'''
	
	
	
	
