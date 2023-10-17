from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import *
from geo.models import *
from common.models import SparseDate
from .models import *
from drf_spectacular.utils import extend_schema_field

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

class InstitutionSerializer(serializers.ModelSerializer):
	institution_authors=AuthorSerializer(many=True)
	class Meta:
		model=Institution
		fields='__all__'

