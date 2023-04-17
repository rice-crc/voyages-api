from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
import pprint
import gc
from tools.nest import nest_selected_fields

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
	def __init__(self, *args, **kwargs):
		selected_fields = kwargs.pop('selected_fields', None)
		super().__init__(*args, **kwargs)
		pp = pprint.PrettyPrinter(indent=4)
		if selected_fields is not None:
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
			
			selected_fields_dict=nestthis(selected_fields)
			print("--selected fields--")
			pp.pprint(selected_fields_dict)
			self=nest_selected_fields(self,selected_fields_dict)

class DocTagSerializer(serializers.ModelSerializer):
	class Meta:
		model=DocTag
		fields='__all__'

class DocSerializer(DynamicFieldsModelSerializer):
	tag=DocTagSerializer(many=True,read_only=True)
	class Meta:
		model=Doc
		fields='__all__'
		
		
