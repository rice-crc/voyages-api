from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField,Field
import re
from .models import *
from common.static.Estimate_options import Estimate_options
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

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

#################################### THE BELOW SERIALIZERS ARE USED FOR API REQUEST VALIDATION. SOME ARE JUST THIN WRAPPERS ON THE ABOVE, LIKE THAT FOR THE PAGINATED VOYAGE LIST ENDPOINT. OTHERS ARE ALMOST ENTIRELY HAND-WRITTEN/HARD-CODED FOR OUR CUSTOMIZED ENDPOINTS LIKE GEOTREEFILTER AND AUTOCOMPLETE, AND WILL HAVE TO BE KEPT IN ALIGNMENT WITH THE MODELS, VIEWS, AND CUSTOM FUNCTIONS THEY INTERACT WITH.


class AnyField(Field):
	def to_representation(self, value):
		return value
	def to_internal_value(self, data):
		return data

############ REQUEST FIILTER OBJECTS
class EstimateFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw"])
	varName=serializers.ChoiceField(choices=[k for k in Estimate_options])
	searchTerm=AnyField()


############ DATAFRAMES ENDPOINT
@extend_schema_serializer(
	examples=[
		OpenApiExample(
			'Filtered request for 3 columns',
			summary="Filtered req for 3 cols",
			description="Here, we are looking the continent on which voyages embarked people, in which year, and how many people were disembarked from those voyages.",
			value={
				"selected_fields":[
					'embarkation_region__export_area__name',
					'embarked_slaves',
					'disembarked_slaves'
				],
				"filter":[
					{
						"varName":"year",
						"op":"btw",
						"searchTerm":[1750,1775]
					}
				]
			}
		)
	]
)
class EstimateDataframesRequestSerializer(serializers.Serializer):
	selected_fields=serializers.ListField(
		child=serializers.ChoiceField(choices=[
			k for k in Estimate_options
		])
	)
	filter=EstimateFilterItemSerializer(many=True,allow_null=True,required=False)

############ OFFSET PAGINATION SERIALIZERS
class EstimateOffsetPaginationSerializer(serializers.Serializer):
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	total_results_count=serializers.IntegerField()

############ CROSSTAB SERIALIZERS
class EstimateCrossTabRequestSerializer(serializers.Serializer):
	columns=serializers.ListField(child=serializers.CharField())
	rows=serializers.CharField()
	binsize=serializers.IntegerField(required=False)
	rows_label=serializers.CharField(allow_null=True)
	agg_fn=serializers.CharField()
	value_field=serializers.CharField()
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	
class EstimateCrossTabResponseSerializer(serializers.Serializer):
	tablestructure=serializers.JSONField()
	data=serializers.JSONField()
	metadata=EstimateOffsetPaginationSerializer()
