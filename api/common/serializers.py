from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
import pprint
import gc



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