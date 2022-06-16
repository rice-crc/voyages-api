from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from voyage.serializers import *


class EnslaverIdentitySourceConnectionSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentitySourceConnection
		fields='__all__'

class EnslaverIdentitySerializer(serializers.ModelSerializer):
	enslaver_sources=EnslaverIdentitySourceConnectionSerializer(many=True,read_only=False)
	principal_location=PlaceSerializer(many=False)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslaverAliasSerializer(serializers.ModelSerializer):
	identity=EnslaverIdentitySerializer(many=False)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslaverRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class EnslaverInRelationSerializer(serializers.ModelSerializer):
	enslaver_alias=EnslaverAliasSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslavementRelationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class EnslavementRelationSerializer(serializers.ModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	enslavers=EnslaverInRelationSerializer(many=True,read_only=False)
	source=VoyageSourcesSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	place=PlaceSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslavedInRelationSerializer(serializers.ModelSerializer):
	transaction=EnslavementRelationSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslavedSourceConnectionSerializer(serializers.ModelSerializer):
	source=VoyageSourcesSerializer(many=False)
	class Meta:
		model=EnslavedSourceConnection
		fields='__all__'

class CaptiveFateSerializer(serializers.ModelSerializer):
	class Meta:
		model=CaptiveFate
		fields='__all__'

class CaptiveStatusSerializer(serializers.ModelSerializer):
	class Meta:
		model=CaptiveStatus
		fields='__all__'

class EnslavedSerializer(serializers.ModelSerializer):
	post_disembark_location=PlaceSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	sources_conn=EnslavedSourceConnectionSerializer(many=True,read_only=True)
	transactions=EnslavedInRelationSerializer(many=True,read_only=True)
	captive_status=CaptiveStatusSerializer(many=False)
	class Meta:
		model=Enslaved
		fields=[
			'post_disembark_location',
			'voyage',
			'captive_fate',
			'sources_conn',
			'transactions',
			'captive_status',
			'id',
			'documented_name',
			'name_first',
			'name_second',
			'name_third',
			'modern_name',
			'editor_modern_names_certainty',
			'age',
			'gender',
			'height',
			'skin_color',
			'last_known_date',
			'last_known_date_dd',
			'last_known_date_mm',
			'last_known_year_yyyy',
			'dataset',
			'notes',
			'sources',
			]



class EnslaverSerializer(serializers.ModelSerializer):
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
		




