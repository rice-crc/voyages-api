import requests
import json

base_url="http://127.0.0.1:8000"

flatfile_params=[

{
'address':'/voyage/',
'output_filename':'../voyage/voyage_options.json'
},
{
'address':'/voyage/geo',
'output_filename':'../voyage/geo_options.json'
},
{
'address':'/assessment/',
'output_filename':'../assessment/assessment_options.json'
},
{
'address':'/past/',
'output_filename':'../past/past_options.json'
}

]


r=requests.post(base_url+'/voyages2022_auth_endpoint/',{'username':'voyages','password':'voyages'})
token=json.loads(r.text)['token']
headers={'Authorization':'Token %s' %token}


for fp in flatfile_params:
	address=fp['address']
	output_filename=fp['output_filename']
	r=requests.options(base_url+address+'?hierarchical=False&auto=True',headers=headers)
	try:
		j=json.loads(r.text)
		d=open(output_filename,'w')
		d.write(r.text)
		d.close()
	except:
		print("bad response:",r)