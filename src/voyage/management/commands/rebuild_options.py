import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.serializers import VoyageSerializer,PlaceSerializer


class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		flatfile_params=[
		{
		'output_filename':'voyage/voyage_options',
		'serializer':VoyageSerializer
		},
		{
		'address':'/voyage/geo',
		'output_filename':'voyage/geo_options',
		'serializer':PlaceSerializer
		}
		]

		def addlevel(thisdict,keychain,payload):
			thiskey=keychain.pop(0)
			if len(keychain)>0:
				if thiskey not in thisdict:
					thisdict[thiskey]={}
				thisdict[thiskey]=addlevel(thisdict[thiskey],keychain,payload)
			else:
				if thiskey not in thisdict:
					thisdict[thiskey]=payload
				else:
					if type(payload)==dict:
						for p in payload:
							thisdict[thiskey][p]=payload[p]
			return thisdict

		def labelconcatenate(valuelist):
			joinedlabel=' : '.join([i for i in valuelist if i not in [None,'s']])
			return(joinedlabel)

		def options_walker(schema,base_address,serializer,baseflatlabel=None):
			
			fieldsdict={}
			
			try:
				fields=serializer._declared_fields
				#print(help(serializer))
			except:
				fields=serializer.child.fields
				#print(serializer.child.Meta.model._meta.verbose_name)
				#fields=serializer.child.fields
			
			for field in fields:
				
				datatypestr=str(type(fields[field]))
				
				#print("???????????",field,datatypestr)
				if base_address!='':
					address='__'.join([base_address,field])
				else:
					address=field
					
				if 'serializer' in datatypestr:
					try:
						label=serializer.Meta.model._meta.verbose_name
					except:
						print("!!!!!!!!!",field)
						label=serializer
					#print(label,address)
					#print(fields[field])
					try:
						s=str(serializer.Meta.model)
						try:
							model=re.search("(?<=<class \').*(?=\')",s).group(0)
						except:
							model="Unkown model name -- retrieval failed"
					except:
						s=str(serializer.__dict__['child'].Meta.model)
						try:
							model=re.search("(?<=<class \').*(?=\')",s).group(0)
						except:
							model="Unkown model name -- retrieval failed"
					schema[address]={'type':'table','label':label,'flatlabel': labelconcatenate([baseflatlabel,label]),'model':model}
					print(schema[address],s)
					schema=options_walker(schema,address,fields[field],labelconcatenate([baseflatlabel,label]))
				else:
					print("----->",field)
					if address.endswith("__id"):
						label="ID"
						schema[address]={'type':datatypestr,'label':label,'flatlabel': labelconcatenate([baseflatlabel,label])}
					else:
						label=fields[field].label
						schema[address]={'type':datatypestr,'label':label,'flatlabel': labelconcatenate([baseflatlabel,label])}
			return schema

		for fp in flatfile_params:
			output_filename=fp['output_filename']
			serializer=fp['serializer']
			flat=options_walker({},'',serializer)
			print(flat)
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