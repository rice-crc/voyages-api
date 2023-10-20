from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

class SourceVoyageSerializer(serializers.ModelSerializer):
	class Meta:
		model=Voyage
		fields='__all__'

class SourceVoyageConnectionSerializer(serializers.ModelSerializer):
	voyage=SourceVoyageSerializer(many=False,read_only=True)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class SourceEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields='__all__'

class SourceEnslavedConnectionSerializer(serializers.ModelSerializer):
	enslaved=SourceEnslavedSerializer(many=False,read_only=True)
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'

class SourceEnslaverIdentitySerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class SourceEnslaverConnectionSerializer(serializers.ModelSerializer):
	enslaver=SourceEnslaverIdentitySerializer(many=False,read_only=True)
	class Meta:
		model=SourceEnslaverConnection
		fields='__all__'

class SourcePageSerializer(serializers.ModelSerializer):
	class Meta:
		model=SourcePage
		fields='__all__'

class SourcePageConnectionSerializer(serializers.ModelSerializer):
	source_page=SourcePageSerializer(many=False,read_only=True)
	class Meta:
		model=SourcePageConnection
		fields='__all__'


@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Ex. 1: array of str vals',
            summary='OR Filter on exact matches of known str values',
            description='Here, we search on str value fields for known exact matches to ANY of those values. Specifically, we are searching for sources in the Outward Manifests for New Orleans collection',
            value={
				"short_ref":["OMNO"]
			},
			request_only=True,
			response_only=False,
        )
    ]
)
class SourceSerializer(serializers.ModelSerializer):
	page_connection=SourcePageConnectionSerializer(many=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializer(many=True)
	source_voyage_connections=SourceVoyageConnectionSerializer(many=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializer(many=True)
	class Meta:
		model=Source
		fields='__all__'

