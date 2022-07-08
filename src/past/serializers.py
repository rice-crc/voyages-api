from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from voyage.serializers import *

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

class EnslaverIdentitySourceConnectionSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=EnslaverIdentitySourceConnection
		fields='__all__'

class EnslaverIdentitySerializer(DynamicFieldsModelSerializer):
	enslaver_sources=EnslaverIdentitySourceConnectionSerializer(many=True,read_only=False)
	principal_location=PlaceSerializer(many=False)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslaverAliasSerializer(DynamicFieldsModelSerializer):
	identity=EnslaverIdentitySerializer(many=False)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslaverRoleSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class EnslaverInRelationSerializer(DynamicFieldsModelSerializer):
	enslaver_alias=EnslaverAliasSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslavementRelationTypeSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class EnslavementRelationSerializer(DynamicFieldsModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	enslavers=EnslaverInRelationSerializer(many=True,read_only=False)
	source=VoyageSourcesSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	place=PlaceSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslavedInRelationSerializer(DynamicFieldsModelSerializer):
	transaction=EnslavementRelationSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslavedSourceConnectionSerializer(DynamicFieldsModelSerializer):
	source=VoyageSourcesSerializer(many=False)
	class Meta:
		model=EnslavedSourceConnection
		fields='__all__'

class CaptiveFateSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=CaptiveFate
		fields='__all__'

class CaptiveStatusSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=CaptiveStatus
		fields='__all__'

class EnslavedSerializer(DynamicFieldsModelSerializer):
	post_disembark_location=PlaceSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	sources_conn=EnslavedSourceConnectionSerializer(many=True,read_only=True)
	transactions=EnslavedInRelationSerializer(many=True,read_only=True)
	captive_status=CaptiveStatusSerializer(many=False)
	class Meta:
		model=Enslaved
		fields='__all__'


# fields=[
# 'post_disembark_location',
# 'voyage',
# 'captive_fate',
# 'sources_conn',
# 'transactions',
# 'captive_status',
# 'id',
# 'documented_name',
# 'name_first',
# 'name_second',
# 'name_third',
# 'modern_name',
# 'editor_modern_names_certainty',
# 'age',
# 'gender',
# 'height',
# 'skin_color',
# 'last_known_date',
# 'last_known_date_dd',
# 'last_known_date_mm',
# 'last_known_year_yyyy',
# 'dataset',
# 'notes',
# 'sources',
# ]



class EnslaverSerializer(DynamicFieldsModelSerializer):
	principal_location=PlaceSerializer(many=False)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'
		
'''fields=[
	'principal_alias',
	'birth_year ',
	'birth_month ',
	'birth_day ',
	'birth_place',
	'death_year ',
	'death_month ',
	'death_day ',
	'death_place',
	'father_name ',
	'father_occupation ',
	'mother_name',
	'first_spouse_name ',
	'first_marriage_date ',
	'second_spouse_name ',
	'second_marriage_date',
	'probate_date ',
	'will_value_pounds ',
	'will_value_dollars ',
	'will_court ',
	'text_id',
	'first_active_year',
	'last_active_year',
	'number_enslaved',
	'principal_location'
	]'''
		




