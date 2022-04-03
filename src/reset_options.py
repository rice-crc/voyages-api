import requests
import json
from tools.nest import *
from voyage.serializers import VoyageSerializer,PlaceSerializer

flatfile_params=[

{
'address':'/voyage/',
'output_filename':'../voyage/voyage_options',
'serializer':VoyageSerializer
}

]

def options_handler(self,request,flatfile=None,auto=False):
	
	schema=options_walker({},'',VoyageSerializer)
	schema=flatfile
	
	hierarchical=True
	if 'hierarchical' in request.query_params:
		if request.query_params['hierarchical'].lower() in ['false','0','n']:
			hierarchical=False
	
	unwound={}
	if hierarchical==True:
		print("tree")
		for i in schema:
			payload=schema[i]
			keychain=i.split('__')
			key=keychain[0]
			unwound=addlevel(unwound,keychain,payload)
		schema=unwound
	
	return schema

for fp in flatfile_params:
	address=fp['address']
	output_filename=fp['output_filename']
	serializer=fp['serializer']
	flat=options_walker({},'',serializer)
	hierarchical={}
	for i in flat:
		payload=flat[i]
		keychain=i.split('__')
		key=keychain[0]
		hierarchical=addlevel(hierarchical,keychain,payload)
	for outputtype in [['hierarchical',hierarchical],['flat',flat]]:
		structure,payload=outputtype
		d=open(output_filename+'_'+structure+'.json','w')
		d.write(json.dumps(payload))
		d.close()