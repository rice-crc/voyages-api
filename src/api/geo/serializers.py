from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin

class CRUDLocationTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=LocationType
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return LocationType.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(LocationTypeSerializer, self).create(validated_data)


class CRUDPolygonSerializer(serializers.ModelSerializer):
	class Meta:
		model=Polygon
		fields='__all__'

class CRUDLocationSerializer(WritableNestedModelSerializer):
	spatial_extent=CRUDPolygonSerializer(many=False,allow_null=True)
	location_type=CRUDLocationTypeSerializer(many=False)
	latitude=serializers.FloatField(allow_null=True)
	longitude=serializers.FloatField(allow_null=True)
	class Meta:
		model=Location
		fields='__all__'