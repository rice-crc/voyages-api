from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *

class LocationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=LocationType
		fields='__all__'

class PolygonSerializer(serializers.ModelSerializer):
	class Meta:
		model=Polygon
		fields='__all__'

class LocationParentSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

class LocationChildSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

class LocationSerializerDeep(serializers.ModelSerializer):
	child_of=LocationParentSerializer(many=False)
	parent_of=LocationChildSerializer(many=True)
	spatial_extent=PolygonSerializer(many=False)
	location_type=LocationTypeSerializer(many=False)
	class Meta:
		model=Location
		fields='__all__'

##REMOVING CHILD_OF AND PARENT_OF RECORDS FROM THE MAIN LOCATION SERIALIZER
##IT HUGELY REDUCES THE OVERHEAD HERE
class LocationSerializer(serializers.ModelSerializer):
	spatial_extent=PolygonSerializer(many=False)
	location_type=LocationTypeSerializer(many=False)
	class Meta:
		model=Location
		fields='__all__'

class AdjacencySerializer(serializers.ModelSerializer):
	source=LocationSerializer(many=False)
	target=LocationSerializer(many=False)
	class Meta:
		model=Adjacency
		fields='__all__'