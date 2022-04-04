import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.serializers import VoyageSerializer,PlaceSerializer
from voyage.models import Voyage,Place
from past.serializers import EnslavedSerializer
from past.models import Enslaved
from assessment.serializers import EstimateSerializer
from assessment.models import Estimate


class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		flatfile_params=[
			{
				'output_filename':'voyage/voyage_options',
				'serializer':VoyageSerializer,
				'objectclass':Voyage
			},
			{
				'output_filename':'voyage/geo_options',
				'serializer':PlaceSerializer,
				'objectclass':Place
			},
			{
				'output_filename':'past/past_options',
				'serializer':EnslavedSerializer,
				'objectclass':Enslaved
			},
			{
				'output_filename':'assessment/assessment_options',
				'serializer':EstimateSerializer,
				'objectclass':Estimate
			},
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
		
		def options_walker(schema,base_address,serializer,baseflatlabel=None):
			
			
			#print("!!!",str(base_address))
			
			try:
				fields=serializer._declared_fields
			except:
				try:
					fields=serializer.fields
				except:
					fields=serializer.child.fields
			
			if len(fields)<=1:
			#if base_address=="voyage_itinerary__first_landing_place":
				#print(base_address,list(fields),str(serializer))
				try:
					#print(serializer.fields)
					fields=serializer.fields
				except:
					pass
			
			
			
			if base_address=='':
				extrafields=serializer.Meta.fields
				print(base_address)
				#print(extrafields,fields)
				for f in extrafields:
					if f not in fields:
						print(f)
						#print(eval("serializer.Meta.model."+f+".__dict__"))
						#print(serializer.Meta.model.__dict__[f].__dict__['field'].__dict__)
						fields[f]=serializer.Meta.model.__dict__[f].__dict__['field']
				#if f not in fields:
						
						
						#field=serializer.Meta.model.__dict__[f]
						#fields[f]=field
			
			'''if base_address=="voyage_itinerary__first_landing_place":
				print(base_address,len(fields),fields,serializer)'''
			
			#print("++++++",len(fields),fields)
			
			
			for field in fields:
				datatypestr=str(type(fields[field]))
				if base_address!='':
					address='__'.join([base_address,field])
				else:
					address=field
				
				'''if address=="voyage_itinerary__port_of_departure" or field=="port_of_departure":
					print(address,field,datatypestr)'''
				#print(address)
				#print('?',address,datatypestr)
				if 'serializer' in datatypestr:
					
					try:
						label=serializer.Meta.model.__dict__[field].__dict__['field'].__dict__['verbose_name']
					except:
						label=serializer.child.fields[field].Meta.model._meta.verbose_name
					#print(label)
					flatlabel=valuesconcatenate([baseflatlabel,label]," : ")
					
					schema[address]={'type':'table','label':label,'flatlabel':flatlabel}
					
					#schema[address]={}
					schema=options_walker(schema,address,fields[field],flatlabel)
				else:
					#print("--->",address,datatypestr)
					#print(fields[field])
					#print(fields[field])
					try:
						label=fields[field].__dict__['label']
					except:
						label=fields[field].__dict__['verbose_name']
					flatlabel=valuesconcatenate([baseflatlabel,label]," : ")
					#queryset=fields[field].queryset
					schema[address]={'type':datatypestr,'label':label,'flatlabel':flatlabel}
			
			return schema
	
	
	
	
	
	
	

		def options_walker2(schema,base_address,serializer,baseflatlabel=None):
			
			fields=serializer.fields
			
			if len(fields)<=1:
			#if base_address=="voyage_itinerary__first_landing_place":
				#print(base_address,list(fields),str(serializer))
				try:
					#print(serializer.fields)
					fields=serializer.fields
				except:
					pass
			for field in fields:
				datatypestr=str(type(fields[field]))
				if base_address!='':
					address='__'.join([base_address,field])
				else:
					address=field
				
				if 'serializer' in datatypestr:
					
					try:
						label=serializer.Meta.model.__dict__[field].__dict__['field'].__dict__['verbose_name']
					except:
						label=serializer.child.fields[field].Meta.model._meta.verbose_name
					flatlabel=valuesconcatenate([baseflatlabel,label]," : ")
					schema[address]={'type':'table','label':label,'flatlabel':flatlabel}
					schema=options_walker(schema,address,fields[field],flatlabel)
				else:
					try:
						label=fields[field].__dict__['label']
					except:
						label=fields[field].__dict__['verbose_name']
					flatlabel=valuesconcatenate([baseflatlabel,label]," : ")
					#queryset=fields[field].queryset
					schema[address]={'type':datatypestr,'label':label,'flatlabel':flatlabel}
			
			return schema
		
		for fp in flatfile_params:
			
			
			output_filename=fp['output_filename']
			serializer=fp['serializer']
			objectclass=fp['objectclass']
			
			testobject=objectclass.objects.all()
			testobject=serializer(testobject,many=False)
			flat=options_walker2({},'',testobject)
			d=open(output_filename+'_flat.json','w')
			d.write(json.dumps(flat))
			d.close
			hierarchical={}
			for i in flat:
				payload=flat[i]
				keychain=i.split('__')
				key=keychain[0]
				hierarchical=addlevel(hierarchical,keychain,payload)
			d=open(output_filename+'_hierarchical.json','w')
			d.write(json.dumps(hierarchical))
			d.close