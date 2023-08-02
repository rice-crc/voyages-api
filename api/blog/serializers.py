from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import *
from geo.models import *
from common.models import SparseDate
from .models import *
from filebrowser.base import FileListing,FileObject

# def filter_listing(item):
# 	return item.filetype != "Folder"
# filelisting=FileListing(site.directory,filter_func=filter_listing)
# for f in filelisting.files_walk_filtered():
# 	print(f)
# 
# 
# 
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 


class PostAuthorSerializer(serializers.ModelSerializer):
	photo = serializers.SerializerMethodField('get_photo_url')
	def get_photo_url(self, obj):
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
	def get_thumbnail_url(self, obj):
		if obj.thumbnail not in ["",None]:
			return obj.thumbnail.url
	class Meta:
		model=Post
		fields='__all__'





class AuthorPostSerializer(serializers.ModelSerializer):
	tags = TagSerializer(many=True,read_only=True)
	thumbnail = serializers.SerializerMethodField('get_thumbnail_url')
	def get_thumbnail_url(self, obj):
		if obj.thumbnail not in ["",None]:
			return obj.thumbnail.url
	class Meta:
		model=Post
		exclude=['authors',]

class AuthorSerializer(serializers.ModelSerializer):
	posts = AuthorPostSerializer(many=True,read_only=True)
	photo = serializers.SerializerMethodField('get_photo_url')
	def get_photo_url(self, obj):
		if obj.photo not in ["",None]:
			return obj.photo.url
	class Meta:
		model=Author
		fields='__all__'

