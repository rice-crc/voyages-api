import requests
import time
import json
from urllib.parse import urlencode
import os
import csv

step=500

results_per_page=step

selected_fields=[
	'voyage_itinerary__imp_principal_port_slave_dis__place',
	'voyage_itinerary__imp_principal_place_of_slave_purchase__place',
	'voyage_slaves_numbers__imp_total_num_slaves_embarked'
]

otherargs= {
	'results_per_page':results_per_page
}

'''otherargs= {
	'voyage_dates__imp_arrival_at_port_of_dis_yyyy':'1800,1810',
	'results_per_page':results_per_page
}'''

args={k:otherargs[k] for k in otherargs}
args['selected_fields']=','.join([i for i in selected_fields])

params=urlencode(args)

if os.path.exists('timings.csv'):
	os.remove('timings.csv')

xy=[]

with open('timings.csv', 'w', newline='') as csvfile:
	csvwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)

	total_results_count=step+1
	
	csvwriter.writerow(['batch size', 'number selected fields', 'total fetch time','total results count'])

	while results_per_page < total_results_count:
	
		next_uri="http://152.70.193.224:8000/voyage/dataframes?%s" % params
		#next_uri="http://127.0.0.1:8000/voyage/dataframes?%s" % params
		total_results_count=None
		st=time.time()
		while next_uri != 'None':
			r=requests.get(next_uri)
			if r.status_code==200:
				if total_results_count is None and 'total_results_count' in r.headers:
					total_results_count=int(r.headers['total_results_count'])
					print('total results:',total_results_count)
				next_uri=r.headers['next_uri']
			else:
				print("trying again, failed on:",next_uri)
		runningtime=time.time()-st
		csvwriter.writerow([results_per_page, len(selected_fields), runningtime,total_results_count])
		
		xy.append([results_per_page,runningtime])
		print('batch size:',results_per_page)
		print('num of cols:',len(selected_fields))
		print('running time:',time.time()-st)
		
		results_per_page+=step
		
		print("sleeping")
		time.sleep(5)

import plotly.graph_objs as go
import plotly
fig = go.Figure()
this_series_x=[i[0] for i in xy]
this_series_y=[i[1] for i in xy]

fig.add_trace(go.Scatter(x=this_series_x,y=this_series_y))
	

plotly.offline.plot(fig,
	filename="benchmark.html"
)



