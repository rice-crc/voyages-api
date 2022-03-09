import collections
from rest_framework import serializers


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
		thisdict[thiskey]=payload
	return thisdict

##RECURSIVE DRILL-DOWN INTO A SCHEMA, GETS ALL ITS FIELDS, THEIR LABELS, AND DATATYPES
##PUSHING MODEL VERBOSE NAMES INTO THE ID FIELDS' LABELS SO THAT WE HAVE TABLE-LEVEL LABELS
##ASSUMES ID AS PK ON EVERY TABLE -- WILL NEED LOTS OF MIGRATIONS TO MAKE THIS HAPPEN
def options_walker(schema,base_address,serializer):
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
			label=fields[field].label
			datatypestr=str(fields[field].__dict__['default'])
			schema[address]={'type':datatypestr,'label':label}	
		elif 'serializer' in datatypestr:
			schema=options_walker(schema,address,fields[field])
		else:
			#CREATING PARENT FIELD W ID (RISKY)
			if address.endswith("__id"):
				try:
					label=serializer.Meta.model._meta.verbose_name
				except:
					label=serializer.__dict__['child'].Meta.model._meta.verbose_name
				schema[address]={'type':datatypestr,'label':label+" ID"}
				schema[address[:-4]]={'type':"table",'label':label}
			else:
				label=fields[field].label
				schema[address]={'type':datatypestr,'label':label}
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
