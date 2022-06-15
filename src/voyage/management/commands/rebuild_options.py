import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.serializers import VoyageSerializer,PlaceSerializer
from voyage.models import Voyage,Place
from past.serializers import EnslavedSerializer
from past.models import Enslaved
from assessment.serializers import EstimateSerializer
from assessment.models import Estimate
from geo.serializers import LocationSerializer,RouteSerializer
from geo.models import Location,Route

class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		#Here we define the output filenames
		# & the base serializer & object class we're feeding into it.
		 
		flatfile_params=[
			{
				'output_filename':'voyage/voyage_options.json',
				'serializer':VoyageSerializer,
				'objectclass':Voyage
			},
			{
				'output_filename':'voyage/geo_options.json',
				'serializer':PlaceSerializer,
				'objectclass':Place
			},
			{
				'output_filename':'past/past_options.json',
				'serializer':EnslavedSerializer,
				'objectclass':Enslaved
			},
			{
				'output_filename':'assessment/assessment_options.json',
				'serializer':EstimateSerializer,
				'objectclass':Estimate
			},
			{
				'output_filename':'geo/location_options.json',
				'serializer':LocationSerializer,
				'objectclass':Location
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

		def valuesconcatenate(valuelist,joiner):
			joinedlabel=joiner.join([i for i in valuelist if i not in [None,'']])
			return(joinedlabel)

		def options_walker2(schema,base_address,serializer,baseflatlabel=None):
			try:
				fields=serializer.fields
			except:
				fields=serializer.child.fields
			for field in fields:
				datatypestr=str(type(fields[field]))
				if base_address!='':
					address='__'.join([base_address,field])
				else:
					address=field
				if 'serializer' in datatypestr:
					#print(address,datatypestr)
					if 'ListSerializer' in datatypestr:
						#this gets the table label from m2m connections on reverse/related field lookups
						#so, for instance, the reverse lookup from voyagesourceconnections to voyage
						##gets returns the label "voyage source connection"
						label=serializer.fields[field].child.Meta.model._meta.verbose_name
					else:						
						try:
							label=serializer.child.fields[field].Meta.model._meta.verbose_name
						except:
							try:
								label=serializer.Meta.model.__dict__[field].__dict__['field'].__dict__['related_query_name']
							except:
								label=serializer.Meta.model.__dict__[field].__dict__['field'].__dict__['verbose_name']
							
					flatlabel=valuesconcatenate([baseflatlabel,label]," : ")
					schema[address]={'type':'table','label':label,'flatlabel':flatlabel}
					#schema[address]={'type':'table','label':label}
					schema=options_walker2(schema,address,fields[field],flatlabel)
				else:
					try:
						label=fields[field].__dict__['label']
					except:
						label=fields[field].__dict__['verbose_name']
					flatlabel=valuesconcatenate([baseflatlabel,label]," : ")
					schema[address]={'type':datatypestr,'label':label,'flatlabel':flatlabel}
					#schema[address]={'type':datatypestr,'label':label}
			return schema
		
		for fp in flatfile_params:
			output_filename=fp['output_filename']
			serializer=fp['serializer']
			objectclass=fp['objectclass']
			print("options for %s" %str(serializer))
			testobject=objectclass.objects.all()
			testobject=serializer(testobject,many=False)
			flat=options_walker2({},'',testobject)
			d=open(output_filename,'w')
			d.write(json.dumps(flat,indent=2))
			d.close
			print("--> wrote %d var descriptions"%len(flat))