from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
import pprint
import gc
from common.serializers import *
from voyage.models import *
from past.models import *




class ZoteroVoyageSerializer(serializers.ModelSerializer):
	class Meta:
		model=Voyage
		fields='__all__'

class ZoteroVoyageConnectionSerializer(serializers.ModelSerializer):
	voyage=ZoteroVoyageSerializer(many=False,read_only=True)
	class Meta:
		model=ZoteroVoyageConnection
		fields='__all__'







class ZoteroEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields='__all__'

class ZoteroEnslavedConnectionSerializer(serializers.ModelSerializer):
	enslaved=ZoteroEnslavedSerializer(many=False,read_only=True)
	class Meta:
		model=ZoteroEnslavedConnection
		fields='__all__'






class ZoteroEnslaverIdentitySerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class ZoteroEnslaverConnectionSerializer(serializers.ModelSerializer):
	enslaver=ZoteroEnslaverIdentitySerializer(many=False,read_only=True)
	class Meta:
		model=ZoteroEnslaverConnection
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

class ZoteroSourceSerializer(serializers.ModelSerializer):
	page_connection=SourcePageConnectionSerializer(many=True,read_only=True)
	zotero_enslaver_connections=ZoteroEnslaverConnectionSerializer(many=True,read_only=True)
	zotero_voyage_connections=ZoteroVoyageConnectionSerializer(many=True,read_only=True)
	zotero_enslaved_connections=ZoteroEnslavedConnectionSerializer(many=True,read_only=True)
	class Meta:
		model=ZoteroSource
		fields='__all__'

