from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
import pprint
from .models import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
	def __init__(self, *args, **kwargs):
		dynamicfieldsserializermode=kwargs.pop('dynamicfieldsserializermode',None)
		selected_fields = kwargs.pop('selected_fields', None)
	
		super().__init__(*args, **kwargs)
		pp = pprint.PrettyPrinter(indent=4)
		if selected_fields is not None and dynamicfieldsserializermode:
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
			
class LocationTypeSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=LocationType
		fields='__all__'

class PolygonSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=Polygon
		fields='__all__'

class LocationParentSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

class LocationChildSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

class LocationSerializerDeep(DynamicFieldsModelSerializer):
	child_of=LocationParentSerializer(many=False)
	parent_of=LocationChildSerializer(many=True)
	spatial_extent=PolygonSerializer(many=False)
	location_type=LocationTypeSerializer(many=False)
	class Meta:
		model=Location
		fields='__all__'

##REMOVING CHILD_OF AND PARENT_OF RECORDS FROM THE MAIN LOCATION SERIALIZER
##IT HUGELY REDUCES THE OVERHEAD HERE
class LocationSerializer(DynamicFieldsModelSerializer):
	spatial_extent=PolygonSerializer(many=False)
	location_type=LocationTypeSerializer(many=False)
	class Meta:
		model=Location
		fields='__all__'

class AdjacencySerializer(DynamicFieldsModelSerializer):
	source=LocationSerializer(many=False)
	target=LocationSerializer(many=False)
	class Meta:
		model=Adjacency
		fields='__all__'