import requests
import time
import json
from urllib.parse import urlencode
import os
import csv
from multiprocessing import Pool, TimeoutError




def f(uri):

	r=requests.get(uri)
	print(r)

if __name__ == '__main__':
	results_per_page=3000
		
	selected_fields=[
		'voyage_itinerary__imp_principal_port_slave_dis__place',
		'voyage_itinerary__imp_principal_place_of_slave_purchase__place',
		'voyage_slaves_numbers__imp_total_num_slaves_embarked'
	]

	otherargs= {
		'results_per_page':results_per_page
	}
	
	args={}
	
	args['selected_fields']=','.join([i for i in selected_fields])
	
	test_uri="http://152.70.193.224:8000/voyage/dataframes?%s&results_per_page=1" % urlencode(args)
	r=requests.get(test_uri)
	total_results_count=int(r.headers['total_results_count'])
	print(total_results_count)
	
	num_pages=int(total_results_count/results_per_page)
	if total_results_count%results_per_page != 0:
		num_pages+=1
	
	args={k:otherargs[k] for k in otherargs}
	
	args['selected_fields']=','.join([i for i in selected_fields])

	params=urlencode(args)
	
	base_uri="http://152.70.193.224:8000/voyage/dataframes?%s" % params
	work=[]
	
	for page in range(1,num_pages+1):
		uri=base_uri+"&results_page=%d" %page
		work.append(uri)
	
	st=time.time()
	
	with Pool(processes=num_pages+1) as pool:
		pool.map(f,work)
	
	print(time.time()-st)