from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from voyage.serializers import *


class ImportAreaSerializer(serializers.ModelSerializer):
	class Meta:
		model=ImportArea
		fields='__all__'

class DisembarkationRegionSerializer(serializers.ModelSerializer):
	import_area=ImportAreaSerializer(many=False)
	class Meta:
		model=ImportRegion
		fields='__all__'

class ExportAreaSerializer(serializers.ModelSerializer):
	class Meta:
		model=ExportArea
		fields='__all__'

class EmbarkationRegionSerializer(serializers.ModelSerializer):
	export_area=ExportAreaSerializer(many=False)
	class Meta:
		model=ExportRegion
		fields='__all__'

class NationSerializer(serializers.ModelSerializer):
	class Meta:
		model=Nation
		fields='__all__'

class EstimateSerializer(serializers.ModelSerializer):
	nation=NationSerializer(many=False)
	embarkation_region=EmbarkationRegionSerializer(many=False)
	disembarkation_region=DisembarkationRegionSerializer(many=False)
	class Meta:
		model=Estimate
		fields='__all__'