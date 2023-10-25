from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin

class SourceVoyageSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Voyage
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return Voyage.objects.get(id=validated_data['id'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(SourceVoyageSerializer, self).create(validated_data)


class SourceVoyageConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	voyage=SourceVoyageSerializer(many=True,read_only=True)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return SourceVoyageConnection.objects.get(id=validated_data['id'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(SourceVoyageConnectionSerializer, self).create(validated_data)

class SourceEnslavedSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return Enslaved.objects.get(id=validated_data['id'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(SourceEnslavedSerializer, self).create(validated_data)

class SourceEnslavedConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	enslaved=SourceEnslavedSerializer(many=True,read_only=True)
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return SourceEnslavedConnection.objects.get(id=validated_data['id'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(SourceEnslavedConnectionSerializer, self).create(validated_data)

class SourceEnslaverIdentitySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return EnslaverIdentity.objects.get(id=validated_data['id'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(SourceEnslaverIdentitySerializer, self).create(validated_data)

class SourceEnslaverConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	enslaver=SourceEnslaverIdentitySerializer(many=True,read_only=True)
	class Meta:
		model=SourceEnslaverConnection
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		try:
			# if there is already an instance in the database with the
			# given value (e.g. tag='apple'), we simply return this instance
			return SourceEnslaverConnection.objects.get(id=validated_data['id'])
		except ObjectDoesNotExist:
			# else, we create a new tag with the given value
			return super(SourceEnslaverConnectionSerializer, self).create(validated_data)

class PageSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Page
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		if 'id' in validated_data:
			return Page.objects.get(id=validated_data['id'])
		else:
			return super(PageSerializer, self).create(validated_data)
			

class SourcePageConnectionSerializer(WritableNestedModelSerializer):
	page=PageSerializer(many=False,read_only=False)
	class Meta:
		model=SourcePageConnection
		fields='__all__'
	def create(self, validated_data):
		#really smart get_or_create-like hack here
		#https://stackoverflow.com/questions/26247192/reuse-existing-object-in-django-rest-framework-nested-serializer
		if 'id' in validated_data:
			return SourcePageConnection.objects.get(id=validated_data['id'])
		else:
			return super(SourcePageConnectionSerializer, self).create(validated_data)


class ShortRefSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
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
			return super(ShortRefSerializer, self).create(validated_data)

@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Ex. 1: array of str vals',
            summary='OR Filter on exact matches of known str values',
            description='Here, we search on str value fields for known exact matches to ANY of those values. Specifically, we are searching for sources in the Outward Manifests for New Orleans collection',
            value={
				"short_ref":["OMNO"]
			}
        )
    ]
)
class SourceSerializer(WritableNestedModelSerializer):
	page_connections=SourcePageConnectionSerializer(many=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializer(many=True)
	source_voyage_connections=SourceVoyageConnectionSerializer(many=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializer(many=True)
	short_ref=ShortRefSerializer(many=False,allow_null=False)
	class Meta:
		model=Source
		fields='__all__'

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
			  "item_url": None,
			  "zotero_group_id": None,
			  "zotero_item_id": None,
			  "short_ref": {"name":"OMNO"},
			  "title": None,
			  "date": None,
			  "last_updated": None,
			  "human_reviewed": None,
			  "notes": None
			}
        )
    ]
)

class SourceCRUDSerializer(WritableNestedModelSerializer):
	page_connections=SourcePageConnectionSerializer(many=True,allow_null=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializer(many=True,allow_null=True)
	source_voyage_connections=SourceVoyageConnectionSerializer(many=True,allow_null=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializer(many=True,allow_null=True)
	item_url=serializers.URLField(allow_null=True)
	zotero_group_id=serializers.IntegerField(allow_null=True)
	zotero_item_id=serializers.CharField(allow_null=True)
	short_ref=ShortRefSerializer(many=False,allow_null=False)
	title=serializers.CharField(allow_null=True)
	date=serializers.CharField(allow_null=True)
	last_updated=serializers.DateTimeField(allow_null=True)
	human_reviewed=serializers.BooleanField(allow_null=True)
	notes=serializers.CharField(allow_null=True)
	class Meta:
		model=Source
		fields='__all__'

