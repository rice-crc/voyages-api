from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin,NestedUpdateMixin

class SourceVoyageConnectionSerializerCRUD(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class SourceEnslavedConnectionSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'

class SourceEnslavementRelationConnectionSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=SourceEnslavementRelationConnection
		fields='__all__'
		
class SourceEnslaverConnectionSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=SourceEnslaverConnection
		fields='__all__'

class TranscriptionSerializerCRUD(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Transcription
		fields='__all__'
	def create(self, validated_data):
		try:
			return TranscriptionSerializerCRUD.objects.get(id=validated_data['id'])
		except:
			return super(TranscriptionSerializerCRUD, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return Transcription.objects.get(id=validated_data['id'])
		except:
			return super(TranscriptionSerializerCRUD, self).create(validated_data)

class PageSerializerCRUD(UniqueFieldsMixin, serializers.ModelSerializer):
	transcriptions=TranscriptionSerializerCRUD(many=True,allow_null=True)
	class Meta:
		model=Page
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		if 'id' in validated_data:
			return Page.objects.get(id=validated_data['id'])
		else:
			return super(PageSerializerCRUD, self).create(validated_data)

class SourcePageConnectionSerializerCRUD(WritableNestedModelSerializer):
	page=PageSerializerCRUD(many=False)
	class Meta:
		model=SourcePageConnection
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		if 'id' in validated_data:
			return SourcePageConnection.objects.get(id=validated_data['id'])
		else:
			return super(SourcePageConnectionSerializerCRUD, self).create(validated_data)

class ShortRefSerializerCRUD(UniqueFieldsMixin, WritableNestedModelSerializer):
	class Meta:
		model=ShortRef
		fields='__all__'

class SourceTypeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=SourceType
		fields='__all__'

class DocSparseDateSerializerCRUD(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=DocSparseDate
		fields='__all__'
	def create(self, validated_data):
		try:
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except:
			return super(SourceVoyageConnectionSerializerCRUD, self).create(validated_data)
	def update(self, instance, validated_data):
		try:
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except:
			return super(SourceVoyageConnectionSerializerCRUD, self).create(validated_data)

class SourceSerializerCRUD(WritableNestedModelSerializer):
	source_type=SourceTypeSerializerCRUD(many=False)
	page_connections=SourcePageConnectionSerializerCRUD(many=True,allow_null=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializerCRUD(many=True,allow_null=True)
	source_voyage_connections=SourceVoyageConnectionSerializerCRUD(many=True,allow_null=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializerCRUD(many=True,allow_null=True)
	source_enslavement_relation_connections=SourceEnslavementRelationConnectionSerializerCRUD(many=True,allow_null=True)
	item_url=serializers.URLField(allow_null=True)
	zotero_group_id=serializers.IntegerField(allow_null=True)
	zotero_item_id=serializers.CharField(allow_null=True)
	title=serializers.CharField(allow_null=True)
	date=DocSparseDateSerializerCRUD(many=False,allow_null=True)
	last_updated=serializers.DateTimeField(allow_null=True)
	human_reviewed=serializers.BooleanField(allow_null=True)
	notes=serializers.CharField(allow_null=True)
	class Meta:
		model=Source
		fields='__all__'