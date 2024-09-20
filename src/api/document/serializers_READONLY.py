from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField,Field
import re
from .models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from voyages3.localsettings import STATIC_URL,OPEN_API_BASE_API
from common.static.Source_options import Source_options
from voyage.models import VoyageShip
from common.autocomplete_indices import get_all_model_autocomplete_fields


class SourceTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=SourceType
		fields='__all__'

# class TranscriptionSerializer(Serializers.ModelSerializer):
# 	class Meta:
# 		model=Transcription
# 		fields='__all__'

class DocSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=DocSparseDate
		fields='__all__'

class SourceVoyageShipSerializer(serializers.ModelSerializer):
	ship_name=serializers.CharField()
	class Meta:
		model=VoyageShip
		fields=('ship_name',)

class SourceVoyageSerializer(serializers.ModelSerializer):
	voyage_ship=SourceVoyageShipSerializer(many=False,read_only=True)
	voyage_id=serializers.IntegerField(read_only=True)
	id=serializers.IntegerField(read_only=True)
	class Meta:
		model=Voyage
		fields=('voyage_ship','voyage_id','id')

class SourceVoyageConnectionSerializer(serializers.ModelSerializer):
# 	voyage=SourceVoyageSerializer(many=False,read_only=True)
	class Meta:
		model=SourceVoyageConnection
		fields=('voyage_id',)

class SourceVoyageConnectionResponseSerializer(serializers.ModelSerializer):
	class Meta:
		model=SourceVoyageConnection
		fields=('voyage',)


class SourceEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields='__all__'

class SourceEnslavedConnectionSerializer(serializers.ModelSerializer):
	enslaved=SourceEnslavedSerializer(many=False,read_only=True)
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'

class SourceEnslavementRelationSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class SourceEnslavementRelationConnectionSerializer(serializers.ModelSerializer):
	enslavement_relation=SourceEnslavementRelationSerializer(many=False)
	class Meta:
		model=SourceEnslavementRelationConnection
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

class PageSerializer(serializers.ModelSerializer):
	class Meta:
		model=Page
		fields='__all__'			

class SourcePageConnectionSerializer(serializers.ModelSerializer):
	page=PageSerializer(many=False,read_only=True)
	class Meta:
		model=SourcePageConnection
		fields='__all__'

class ShortRefSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Source
		fields='__all__'

class ShortRefSerializer(serializers.ModelSerializer):
	short_ref_sources=ShortRefSourceSerializer(many=True,read_only=True)
	class Meta:
		model=ShortRef
		fields='__all__'

class SourceShortRefSerializer(serializers.ModelSerializer):
	class Meta:
		model=ShortRef
		fields=['id','name']

class SourceSerializer(serializers.ModelSerializer):
	source_type=SourceTypeSerializer(many=False)
	page_connections=SourcePageConnectionSerializer(many=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializer(many=True)
	source_voyage_connections=SourceVoyageConnectionSerializer(many=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializer(many=True)
	source_enslavement_relation_connections=SourceEnslavementRelationConnectionSerializer(many=True)
	short_ref=SourceShortRefSerializer(many=False,allow_null=False)
	date=DocSparseDateSerializer(many=False,allow_null=True)
	iiif_manifest_url=SerializerMethodField()
	class Meta:
		model=Source
		fields='__all__'
	def get_iiif_manifest_url(self,obj):
		if obj.has_published_manifest and obj.zotero_group_id and obj.zotero_item_id is not None:
			return(f'{OPEN_API_BASE_API}{STATIC_URL}iiif_manifests/{obj.zotero_group_id}__{obj.zotero_item_id}.json')
		else:
			return None

class SourceResponseSerializer(serializers.ModelSerializer):
	source_type=SourceTypeSerializer(many=False,read_only=True)
	page_connections=SourcePageConnectionSerializer(many=True,read_only=True)
	source_enslaver_connections=SourceEnslaverConnectionSerializer(many=True,read_only=True)
	source_voyage_connections=SourceVoyageConnectionSerializer(many=True,read_only=True)
	source_enslaved_connections=SourceEnslavedConnectionSerializer(many=True,read_only=True)
	source_enslavement_relation_connections=SourceEnslavementRelationConnectionSerializer(many=True,read_only=True)
	short_ref=SourceShortRefSerializer(many=False,allow_null=False,read_only=True)
	date=DocSparseDateSerializer(many=False,allow_null=True,read_only=True)
	iiif_manifest_url=SerializerMethodField()
	class Meta:
		model=Source
		fields='__all__'
	def get_iiif_manifest_url(self,obj):
		if obj.has_published_manifest and obj.zotero_group_id and obj.zotero_item_id is not None:
			return(f'{OPEN_API_BASE_API}{STATIC_URL}iiif_manifests/{obj.zotero_group_id}__{obj.zotero_item_id}.json')
		else:
			return None

############ REQUEST FIILTER OBJECTS
class AnyField(Field):
	def to_representation(self, value):
		return value
	def to_internal_value(self, data):
		return data

class SourceFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw","andlist"])
	varName=serializers.ChoiceField(choices=[k for k in Source_options])
	searchTerm=AnyField()


@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Filtered search for docs with manifests',
            summary='Filtered search for docs with manifests',
            description='Here, we search for documents a) whose titles containing a substring like "creole" and b) have manifests (there is only one result, from the Texas/OMNO data).',
            value={
			  "filter": [
				{
				  "varName": "has_published_manifest",
				  "op": "exact",
				  "searchTerm": True
				},
				{
				  "varName": "title",
				  "op": "icontains",
				  "searchTerm": "creole"
				}
			  ]
			},
			request_only=True,
			response_only=False
        ),
		OpenApiExample(
            'Exact match on a nested field (short_ref)',
            summary='Exact match on a nested field (short_ref)',
            description='Here, we search for an exact match on the short valuefield.',
            value={
            	"filter":[
					{
						"varName":"short_ref__name",
						"op":"in",
						"searchTerm":["1713Poll"]
					}
            	]
			},
			request_only=True,
			response_only=False
        ),
		OpenApiExample(
            'Exact match on a nested ship field (ship_name)',
            summary='Exact match on a nested field (ship_name)',
            description='Here, we search for an exact match on the short valuefield.',
            value={
            	"filter":[
					{
						"varName":"source_voyage_connections__voyage__voyage_ship__ship_name",
						"op":"in",
						"searchTerm":["Brazos","Nelson"]
					}
            	]
			},
			request_only=True,
			response_only=False
        )
    ]
)
class SourceRequestSerializer(serializers.Serializer):
	filter=SourceFilterItemSerializer(many=True,allow_null=True,required=False)
	order_by=serializers.ListField(child=serializers.CharField(allow_null=True),required=False,allow_null=True)
	page=serializers.IntegerField(required=False,allow_null=True)
	page_size=serializers.IntegerField(required=False,allow_null=True)
	
class SourceListResponseSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	count=serializers.IntegerField()
	results=SourceResponseSerializer(many=True,read_only=True)

############ AUTOCOMPLETE SERIALIZERS
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Filtered, paginated autocomplete on sources',
			summary='Filtered, paginated autocomplete on enslaver names',
			description='Here, we are requesting 20 suggested values, starting with the 41st item, ship names like "manif" in the Outward Manifests from New Orleans collection',
			value={
				"varName": "source_voyage_connections__voyage__voyage_ship__ship_name",
				"querystr": "zong",
				"offset": 0,
				"limit": 20,
				"filter": [
					{
						"varName": "source_voyage_connections__voyage__dataset",
						"op": "exact",
						"searchTerm": 0
					},
				]
			},
			request_only=True
		)
    ]
)
class SourceAutoCompleteRequestSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=get_all_model_autocomplete_fields('Source'))
	querystr=serializers.CharField(allow_null=True,allow_blank=True)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=SourceFilterItemSerializer(many=True,allow_null=True,required=False)
# 	global_search=serializers.CharField(allow_null=True,required=False)

class SourceAutoCompletekvSerializer(serializers.Serializer):
	value=serializers.CharField()

class SourceAutoCompleteResponseSerializer(serializers.Serializer):
	suggested_values=SourceAutoCompletekvSerializer(many=True)
	
	
	


class DocumentSearchSerializer(serializers.Serializer):
	order_by=serializers.ListField(child=serializers.CharField(allow_null=True),required=False,allow_null=True)
	page=serializers.IntegerField(required=False,allow_null=True)
	page_size=serializers.IntegerField(required=False,allow_null=True)
	title=serializers.CharField(required=False,allow_null=True)
	fullText=serializers.CharField(required=False,allow_null=True)
	bib=serializers.CharField(required=False,allow_null=True)
	enslavers=serializers.ListField(child=serializers.CharField(),required=False,allow_null=True)
	voyageIds=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True)

