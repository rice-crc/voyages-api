from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
import pprint
import gc

# class SparseDateSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=SparseDate
# 		fields='__all__'

class autocompleterequestserializer(serializers.Serializer):
	varname=serializers.CharField(max_length=500)
	querystr=serializers.CharField(max_length=255)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=serializers.JSONField()

class autocompletekvserializer(serializers.Serializer):
	value=serializers.CharField(max_length=255)

class autocompleteresponseserializer(serializers.Serializer):
	varname=serializers.CharField(max_length=500)
	querystr=serializers.CharField(max_length=255)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=serializers.JSONField()
	suggested_values=autocompletekvserializer(many=True)


