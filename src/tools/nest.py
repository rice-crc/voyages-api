import collections
from rest_framework import serializers
import re

#provided an ordered dict and a hierarchically-ordered list of keys
##like: ['voyage_itinerary','imp_port_voyage_begin','longitude']
##and: OrderedDict([('imp_principal_region_slave_dis', None), ('imp_port_voyage_begin', OrderedDict([('place', 'Baltimore'), ('longitude', '-76.6125000')]))])
#this will drill down to the value (assuming that this path is in the ordered dict)
def bottomout(input,keychain):
	if len(keychain)>0 and input is not None:
		k=keychain.pop(0)
		if type(input)==list:
			r=[]
			keychain3=list([k]+list(keychain))
			for i in input:
				keychain4=list(keychain3)
				r.append(bottomout(i,keychain4))
		else:
			if type(input[k])==collections.OrderedDict:
				r=bottomout(input[k],list(keychain))
			##this allows it to return split fields (which occur with many to many relations, like voyage_ship_owner__name)
			elif type(input[k])==list and len(keychain)>0:
				k2=keychain.pop(0)
				#you can use this to test for bad entries in the options file
				r=[]
				for i in input[k]:
					keychain2=list(keychain)
					if len(keychain)==0:
						r.append(i[k2])					
					else:
						r.append(bottomout(i[k2],keychain2))
				if len(r)==0:
					r=None
				return(r)
			else:
				r=input[k]
	else:
		r=None

	return(r)

##RECURSIVE NEST-BUILDERS

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

def nest_django_dict(flat_dict):
	hierarchical={}
	for i in flat_dict:
		payload=flat_dict[i]
		keychain=i.split('__')
		key=keychain[0]
		hierarchical=addlevel(hierarchical,keychain,payload)
	return hierarchical

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
