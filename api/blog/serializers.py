from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import *
from geo.models import *
from common.nest import nest_selected_fields
from common.models import SparseDate
from .models import *

class AuthorSerializer(serializers.ModelSerializer):
	class Meta:
		model=Author
		fields='__all__'

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model=Tag
		fields='__all__'

class PostSerializer(serializers.ModelSerializer):
	authors = AuthorSerializer(many=True,read_only=True)
	tags = TagSerializer(many=True,read_only=True)
	class Meta:
		model=Post
		fields='__all__'
