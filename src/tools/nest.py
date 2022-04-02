import collections
from rest_framework import serializers
import re

def nestthis(keychain,thisdict={}):
	while keychain:
		k=keychain.pop(0)
		kvs=k.split('__')
		if len(kvs)==2:
			i,v=kvs
			if i in thisdict:
				thisdict[i][v]={}
			else:
				thisdict[i]={v:{}}
					
		elif len(kvs)==1:
			thisdict[kvs[0]]={}
		else:
			i=kvs[0]
			j=['__'.join(kvs[1:])]
			if i in thisdict:
				thisdict[i]=nestthis(j,thisdict[i])
			else:
				thisdict[i]=nestthis(j,{})
	return thisdict

#provided an ordered dict and a hierarchically-ordered list of keys
##like: ['voyage_itinerary','imp_port_voyage_begin','longitude']
##and: OrderedDict([('imp_principal_region_slave_dis', None), ('imp_port_voyage_begin', OrderedDict([('place', 'Baltimore'), ('longitude', '-76.6125000')]))])
#this will drill down to the value (assuming that this path is in the ordered dict)
def bottomout(input,keychain):
	if len(keychain)>0:
		k=keychain.pop(0)
		if type(input[k])==collections.OrderedDict:
			r=bottomout(input[k],list(keychain))
		##this allows it to return split fields (which occur with many to many relations, like voyage_ship_owner__name)
		elif type(input[k])==list and len(keychain)>0:
			k2=keychain.pop(0)
			#you can use this to test for bad entries in the options file
			#print(k,k2,[i for i in input[k]])
			r=[i[k2] for i in input[k]]
			return(r)
		else:
			r=input[k]
	else:
		r=[]
	return(r)

##RECURSIVE NEST-BUILDER
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

##RECURSIVE DRILL-DOWN INTO A SCHEMA, GETS ALL ITS FIELDS, THEIR LABELS, AND DATATYPES
##PUSHING MODEL VERBOSE NAMES INTO THE ID FIELDS' LABELS SO THAT WE HAVE TABLE-LEVEL LABELS
##ASSUMES ID AS PK ON EVERY TABLE -- WILL NEED LOTS OF MIGRATIONS TO MAKE THIS HAPPEN

def labelconcatenate(valuelist):
	joinedlabel=' : '.join([i for i in valuelist if i not in [None,'s']])
	return(joinedlabel)
	

def options_walker(schema,base_address,serializer,baseflatlabel=None):
	try:
		fields=serializer.fields.__dict__['fields']
	except:
		#this (unintelligently) handles through fields
		fields=serializer.__dict__['child'].fields
	for field in fields:
		datatypestr=str(type(fields[field]))
		if base_address!='':
			address='__'.join([base_address,field])
		else:
			address=field
		if 'SerializerMethodField' in datatypestr:
			#this handles serializermethodfields
			#(which I am storing in the "default" key)
			#print("++++++++++++",address,label)
			label=fields[field].label
			datatypestr=str(fields[field].__dict__['default'])
			schema[address]={'type':datatypestr,'label':label,'flatlabel': labelconcatenate([baseflatlabel,label])}	
		elif 'PrimaryKeyRelatedField' in datatypestr:
			label=fields[field].label
			#print("++++++++++++",address,label)
		elif 'serializer' in datatypestr:
			label=fields[field].label
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
			
			schema=options_walker(schema,address,fields[field],labelconcatenate([baseflatlabel,label]))
		else:			
			if address.endswith("__id"):
				label="ID"
				schema[address]={'type':datatypestr,'label':label,'flatlabel': labelconcatenate([baseflatlabel,label])}
			else:
				label=fields[field].label
				schema[address]={'type':datatypestr,'label':label,'flatlabel': labelconcatenate([baseflatlabel,label])}
	return schema

def nest_selected_fields(self,selected_fields_dict):
	fields=list(self.fields)
	for field in fields:
		if field not in selected_fields_dict:
			del(self.fields[field])
		else:
			
			if type(self.fields[field])==serializers.ListSerializer:
				'''handles list serializers (many-to-many connections)'''
				try:
					s=list(self.fields[field].child.fields)
				except:
					s=None
				if s is not None:
					self.fields[field].child.fields=nest_selected_fields(self.fields[field].child,selected_fields_dict[field])
			else:
				'''handles one-to-one relations'''
				try:
					s=list(self.fields[field].fields)
				except:
					s=None
				if s is not None:
					self.fields[field].fields=nest_selected_fields(self.fields[field],selected_fields_dict[field])
	return(self.fields)
