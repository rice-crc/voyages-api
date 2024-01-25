from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
import pprint
import gc
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

class autocompleterequestserializer(serializers.Serializer):
	varName=serializers.CharField(max_length=500)
	querystr=serializers.CharField(max_length=255)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()

class autocompletekvserializer(serializers.Serializer):
	value=serializers.CharField(max_length=255)

class autocompleteresponseserializer(serializers.Serializer):
	varName=serializers.CharField(max_length=500)
	querystr=serializers.CharField(max_length=255)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	suggested_values=autocompletekvserializer(many=True)

class crosstabrequestserializer(serializers.Serializer):
	columns=serializers.ListField(child=serializers.CharField())
	rows=serializers.CharField(max_length=500)
	binsize=serializers.IntegerField()
	rows_label=serializers.CharField(max_length=500,allow_null=True)
	agg_fn=serializers.CharField(max_length=500)
	value_field=serializers.CharField(max_length=500)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	
class offsetpaginationserializer(serializers.Serializer):
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	total_results_count=serializers.IntegerField()
	
class crosstabresponseserializer(serializers.Serializer):
	tablestructure=serializers.JSONField()
	data=serializers.JSONField()
	medatadata=offsetpaginationserializer(many=False)


############ GLOBAL SEARCH SERIALIZERS
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Global search acrossed indexed entities',
			summary='Global search acrossed indexed entities',
			description='Here, we are searching across the indexed text fields of our core entities for a substring like "ami".',
			value={
				"search_string": "ami"
			},
			request_only=True
		)
    ]
)
class GlobalSearchRequestSerializer(serializers.Serializer):
	search_string=serializers.CharField(max_length=500)
	
class GlobalSearchResponseItemSerializer(serializers.Serializer):
	type=serializers.CharField(max_length=50)
	results_count=serializers.IntegerField()
	ids=serializers.ListField(child=serializers.IntegerField())