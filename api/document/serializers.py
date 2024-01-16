from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin,NestedUpdateMixin

class CRUDSourceTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SourceType
		fields='__all__'
	def create(self, validated_data):
		try:
			return SourceType.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceTypeSerializer, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return SourceType.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceTypeSerializer, self).create(validated_data)

class CRUDTranscriptionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Transcription
		fields='__all__'
	def create(self, validated_data):
		try:
			return CRUDTranscriptionSerializer.objects.get(id=validated_data['id'])
		except:
			return super(CRUDTranscriptionSerializer, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return Transcription.objects.get(id=validated_data['id'])
		except:
			return super(CRUDTranscriptionSerializer, self).create(validated_data)

class CRUDDocSparseDateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=DocSparseDate
		fields='__all__'
	def create(self, validated_data):
		try:
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceVoyageConnectionSerializer, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceVoyageConnectionSerializer, self).create(validated_data)

class CRUDSourceVoyageConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'
	def create(self, validated_data):
		try:
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceVoyageConnectionSerializer, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceVoyageConnectionSerializer, self).create(validated_data)

class CRUDSourceEnslavedConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'
	def create(self, validated_data):
		try:
			return CRUDSourceEnslavedConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceEnslavedConnectionSerializer, self).create(validated_data)
	def update(self, instance,validated_data):
		try:
			return CRUDSourceEnslavedConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceEnslavedConnectionSerializer, self).create(validated_data)

class CRUDSourceEnslavementRelationConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SourceEnslavementRelationConnection
		fields='__all__'
	def create(self, validated_data):
		try:
			return SourceEnslavementRelationConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceEnslavementRelationConnectionSerializer, self).create(validated_data)
	def update(self, instance,validated_data):
		try:
			return SourceEnslavementRelationConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceEnslavementRelationConnectionSerializer, self).create(validated_data)

class CRUDSourceEnslaverConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SourceEnslaverConnection
		fields='__all__'
	def create(self, validated_data):
		try:
			return SourceEnslaverConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceEnslaverConnectionSerializer, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return SourceEnslaverConnection.objects.get(id=validated_data['id'])
		except:
			return super(CRUDSourceEnslaverConnectionSerializer, self).create(validated_data)		

class CRUDPageSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	transcriptions=CRUDSourceTypeSerializer(many=True)
	class Meta:
		model=Page
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		if 'id' in validated_data:
			return Page.objects.get(id=validated_data['id'])
		else:
			return super(CRUDPageSerializer, self).create(validated_data)
			

class CRUDSourcePageConnectionSerializer(WritableNestedModelSerializer):
	page=CRUDPageSerializer(many=False,read_only=False)
	class Meta:
		model=SourcePageConnection
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		if 'id' in validated_data:
			return SourcePageConnection.objects.get(id=validated_data['id'])
		else:
			return super(CRUDSourcePageConnectionSerializer, self).create(validated_data)

class CRUDShortRefSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
	class Meta:
		model=ShortRef
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return ShortRef.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(CRUDShortRefSerializer, self).create(validated_data)

@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Ex. 1: Create a source with the bare minimum information, based on its unique short_ref (a legacy field)',
            summary='Nulls for all fields except short_ref',
            description='This is a good example of how you might create a placeholder source, before later filling it in with PATCH or PUT operation',
            value={
			  "page_connections": None,
			  "source_enslaver_connections": None,
			  "source_voyage_connections": None,
			  "source_enslaved_connections": None,
			  "source_enslavement_relation_connections":None,
			  "item_url": None,
			  "zotero_group_id": None,
			  "zotero_item_id": None,
			  "short_ref": {"name":"1713Poll"},
			  "title": None,
			  "date": None,
			  "last_updated": None,
			  "human_reviewed": None,
			  "notes": None
			},
			request_only=True,
			response_only=False
        )
    ]
)
class SourceCRUDSerializer(WritableNestedModelSerializer):
	page_connections=CRUDSourcePageConnectionSerializer(many=True,allow_null=True)
	source_enslaver_connections=CRUDSourceEnslaverConnectionSerializer(many=True,allow_null=True)
	source_voyage_connections=CRUDSourceVoyageConnectionSerializer(many=True,allow_null=True)
	source_enslaved_connections=CRUDSourceEnslavedConnectionSerializer(many=True,allow_null=True)
	source_enslavement_relation_connections=CRUDSourceEnslavementRelationConnectionSerializer(many=True,allow_null=True)
	item_url=serializers.URLField(allow_null=True)
	zotero_group_id=serializers.IntegerField(allow_null=True)
	zotero_item_id=serializers.CharField(allow_null=True)
	short_ref=CRUDShortRefSerializer(many=False,allow_null=False)
	title=serializers.CharField(allow_null=True)
	date=CRUDDocSparseDateSerializer(many=False,allow_null=True)
	last_updated=serializers.DateTimeField(allow_null=True)
	human_reviewed=serializers.BooleanField(allow_null=True)
	notes=serializers.CharField(allow_null=True)
	class Meta:
		model=Source
		fields='__all__'