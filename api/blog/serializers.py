from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import *
from geo.models import *
from .models import *
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class AuthorInstitutionSerializer(serializers.ModelSerializer):
	class Meta:
		model=Institution
		fields='__all__'

class PostAuthorSerializer(serializers.ModelSerializer):
	photo = serializers.SerializerMethodField('get_photo_url')
	institution = AuthorInstitutionSerializer(many=False)
	@extend_schema_field(serializers.CharField)
	def get_photo_url(self, obj) -> str:
		if obj.photo not in ["",None]:
			return obj.photo.url
	class Meta:
		model=Author
		fields='__all__'

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model=Tag
		fields='__all__'

@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Ex. 1: array of str vals',
            summary='OR Filter on exact matches of known str values',
            description='Here, we search on str value fields for known exact matches to ANY of those values. Specifically, we are searching for blog posts with the tag Introductory Maps written in English',
            value={
				"tags__name__in":["Introductory Maps"],
				"language__exact":"en"
			},
			request_only=True,
			response_only=False,
        )
    ]
)
class PostSerializer(serializers.ModelSerializer):
	authors = PostAuthorSerializer(many=True,read_only=True)
	tags = TagSerializer(many=True,read_only=True)
	thumbnail = serializers.SerializerMethodField('get_thumbnail_url')
	@extend_schema_field(serializers.CharField)
	def get_thumbnail_url(self, obj) -> str:
		if obj.thumbnail not in ["",None]:
			return obj.thumbnail.url
	class Meta:
		model=Post
		fields='__all__'

class AuthorPostSerializer(serializers.ModelSerializer):
	tags = TagSerializer(many=True,read_only=True)
	thumbnail = serializers.SerializerMethodField('get_thumbnail_url')
	@extend_schema_field(serializers.CharField)
	def get_thumbnail_url(self, obj) -> str:
		if obj.thumbnail not in ["",None]:
			return obj.thumbnail.url
	class Meta:
		model=Post
		exclude=['authors',]

@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Ex. 1: array of str vals',
            summary='OR Filter on exact matches of known str values',
            description='Here, we are searching for authors who are affiliated with UCSC',
            value={
				"institution__name__exact":"University of California, Santa Cruz"
			},
			request_only=True,
			response_only=False,
        )
    ]
)
class AuthorSerializer(serializers.ModelSerializer):
	posts = AuthorPostSerializer(many=True,read_only=True)
	photo = serializers.SerializerMethodField('get_photo_url')
	institution = AuthorInstitutionSerializer(many=False)
	@extend_schema_field(serializers.CharField)
	def get_photo_url(self, obj) -> str:
		if obj.photo not in ["",None]:
			return obj.photo.url
	class Meta:
		model=Author
		fields='__all__'

@extend_schema_serializer(
	examples = [
		OpenApiExample(
            'Ex. 1: array of str vals',
            summary='OR Filter on exact matches of known str values',
            description='Here, we are searching for instutions whose authors wrote blog posts that have the tag Introductory Maps',
            value={
				"institution_authors__posts__tags__name__exact":"Introductory Maps"
			},
			request_only=True,
			response_only=False,
        )
    ]
)
class InstitutionSerializer(serializers.ModelSerializer):
	institution_authors=AuthorSerializer(many=True)
	class Meta:
		model=Institution
		fields='__all__'

