from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import Source,Page,SourcePageConnection,SourceVoyageConnection
from geo.models import Location
from past.models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from common.static.Voyage_options import Voyage_options

#### GEO

class VoyageLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

##### VESSEL VARIABLES ##### 

class RigOfVesselSerializer(serializers.ModelSerializer):
	class Meta:
		model=RigOfVessel
		fields='__all__'

class NationalitySerializer(serializers.ModelSerializer):
	class Meta:
		model=Nationality
		fields='__all__'


class TonTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=TonType
		fields='__all__'

class VoyageShipSerializer(serializers.ModelSerializer):
	rig_of_vessel=RigOfVesselSerializer(many=False,read_only=True)
	imputed_nationality=NationalitySerializer(many=False,read_only=True)
	nationality_ship=NationalitySerializer(many=False,read_only=True)
	ton_type=TonTypeSerializer(many=False,read_only=True)
	vessel_construction_place=VoyageLocationSerializer(many=False,read_only=True)
	vessel_construction_region=VoyageLocationSerializer(many=False,read_only=True)
	registered_place=VoyageLocationSerializer(many=False,read_only=True)
	registered_region=VoyageLocationSerializer(many=False,read_only=True)
	class Meta:
		model=VoyageShip
		fields='__all__'


##### ENSLAVED NUMBERS ##### 

class VoyageSlavesNumbersSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageSlavesNumbers
		fields='__all__'

##### CREW NUMBERS ##### 

class VoyageCrewSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageCrew
		fields='__all__'



##### ITINERARY #####

class VoyageItinerarySerializer(serializers.ModelSerializer):
	port_of_departure=VoyageLocationSerializer(many=False,read_only=True)
	int_first_port_emb=VoyageLocationSerializer(many=False,read_only=True)
	int_second_port_emb=VoyageLocationSerializer(many=False,read_only=True)
	int_first_region_purchase_slaves=VoyageLocationSerializer(many=False,read_only=True)
	int_second_region_purchase_slaves=VoyageLocationSerializer(many=False,read_only=True)
	int_first_port_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_second_port_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_first_region_slave_landing=VoyageLocationSerializer(many=False,read_only=True)
	imp_principal_region_slave_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_second_place_region_slave_landing=VoyageLocationSerializer(many=False,read_only=True)
	first_place_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	second_place_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	third_place_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	first_region_slave_emb=VoyageLocationSerializer(many=False,read_only=True)
	second_region_slave_emb=VoyageLocationSerializer(many=False,read_only=True)
	third_region_slave_emb=VoyageLocationSerializer(many=False,read_only=True)
	port_of_call_before_atl_crossing=VoyageLocationSerializer(many=False,read_only=True)
	first_landing_place=VoyageLocationSerializer(many=False,read_only=True)
	second_landing_place=VoyageLocationSerializer(many=False,read_only=True)
	third_landing_place=VoyageLocationSerializer(many=False,read_only=True)
	first_landing_region=VoyageLocationSerializer(many=False,read_only=True)
	second_landing_region=VoyageLocationSerializer(many=False,read_only=True)
	third_landing_region=VoyageLocationSerializer(many=False,read_only=True)
	place_voyage_ended=VoyageLocationSerializer(many=False,read_only=True)
	region_of_return=VoyageLocationSerializer(many=False,read_only=True)
	broad_region_of_return=VoyageLocationSerializer(many=False,read_only=True)
	imp_port_voyage_begin=VoyageLocationSerializer(many=False,read_only=True)
	imp_region_voyage_begin=VoyageLocationSerializer(many=False,read_only=True)
	imp_broad_region_voyage_begin=VoyageLocationSerializer(many=False,read_only=True)
	principal_place_of_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	imp_principal_place_of_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	imp_principal_region_of_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	imp_broad_region_of_slave_purchase=VoyageLocationSerializer(many=False,read_only=True)
	principal_port_of_slave_dis=VoyageLocationSerializer(many=False,read_only=True)
	imp_principal_port_slave_dis=VoyageLocationSerializer(many=False,read_only=True)
	imp_broad_region_slave_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_fourth_port_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_third_port_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_fourth_port_dis=VoyageLocationSerializer(many=False,read_only=True)
	int_third_place_region_slave_landing=VoyageLocationSerializer(many=False,read_only=True)
	int_fourth_place_region_slave_landing=VoyageLocationSerializer(many=False,read_only=True)
	class Meta:
		model=VoyageItinerary
		fields='__all__'

##### OUTCOMES #####

class ParticularOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=ParticularOutcome
		fields='__all__'

class SlavesOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=SlavesOutcome
		fields='__all__'
		
class ResistanceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Resistance
		fields='__all__'

class OwnerOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=OwnerOutcome
		fields='__all__'

class VesselCapturedOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=VesselCapturedOutcome
		fields='__all__'
		
class VoyageOutcomeSerializer(serializers.ModelSerializer):
	outcome_owner=OwnerOutcomeSerializer(many=False,read_only=True)
	outcome_slaves=SlavesOutcomeSerializer(many=False,read_only=True)
	particular_outcome=ParticularOutcomeSerializer(many=False,read_only=True)
	resistance=ResistanceSerializer(many=False,read_only=True)
	vessel_captured_outcome=VesselCapturedOutcomeSerializer(many=False,read_only=True)
	class Meta:
		model=VoyageOutcome
		fields='__all__'


#### DATES #####
class VoyageSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageSparseDate
		fields='__all__'
		
class VoyageDatesSerializer(serializers.ModelSerializer):
	voyage_began_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	slave_purchase_began_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	vessel_left_port_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	first_dis_of_slaves_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	date_departed_africa_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	arrival_at_second_place_landing_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	third_dis_of_slaves_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	departure_last_place_of_landing_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	voyage_completed_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	imp_voyage_began_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	imp_departed_africa_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	imp_arrival_at_port_of_dis_sparsedate=VoyageSparseDateSerializer(many=False,read_only=True)
	class Meta:
		model=VoyageDates
		fields='__all__'
	
	

class VoyageSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Source
		fields='__all__'

class VoyageVoyageSourceConnectionSerializer(serializers.ModelSerializer):
	source=VoyageSourceSerializer(many=False,read_only=True)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class VoyageEnslaverRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class VoyageEnslaverIdentitySerializer(serializers.ModelSerializer):
	birth_place=VoyageLocationSerializer(many=False,read_only=True)
	death_place=VoyageLocationSerializer(many=False,read_only=True)
	principal_location=VoyageLocationSerializer(many=False,read_only=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class VoyageEnslaverAliasSerializer(serializers.ModelSerializer):
	identity=VoyageEnslaverIdentitySerializer(many=False,read_only=True)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class VoyageEnslaverInRelationSerializer(serializers.ModelSerializer):
	roles=VoyageEnslaverRoleSerializer(many=True,read_only=True)
	enslaver_alias=VoyageEnslaverAliasSerializer(many=False,read_only=True)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class VoyageEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=['id','documented_name']

class VoyageEnslavedInRelationSerializer(serializers.ModelSerializer):
	enslaved=VoyageEnslavedSerializer(many=False,read_only=True)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class VoyageEnslavementRelationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class VoyageEnslavementRelationsSerializer(serializers.ModelSerializer):
	enslaved_in_relation=VoyageEnslavedInRelationSerializer(many=True,read_only=True)
	relation_enslavers=VoyageEnslaverInRelationSerializer(many=True,read_only=True)
	relation_type=VoyageEnslavementRelationTypeSerializer(many=False,read_only=True)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class VoyageGroupingsSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageGroupings
		fields='__all__'

class AfricanInfoSerializer(serializers.ModelSerializer):
	class Meta:
		model=AfricanInfo
		fields='__all__'


class CargoTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=CargoType
		fields='__all__'

class CargoUnitSerializer(serializers.ModelSerializer):
	class Meta:
		model=CargoUnit
		fields='__all__'

class VoyageCargoConnectionSerializer(serializers.ModelSerializer):
	cargo=CargoTypeSerializer(many=False,read_only=True)
	unit=CargoUnitSerializer(many=False,read_only=True)
	amount=serializers.DecimalField(max_digits=7,decimal_places=2,read_only=True)
	class Meta:
		model=VoyageCargoConnection
		fields='__all__'

class VoyageSerializer(serializers.ModelSerializer):
	voyage_source_connections=VoyageVoyageSourceConnectionSerializer(many=True,read_only=True)
	voyage_itinerary=VoyageItinerarySerializer(many=False,read_only=True)
	voyage_dates=VoyageDatesSerializer(many=False,read_only=True)
	voyage_enslavement_relations=VoyageEnslavementRelationsSerializer(many=True,read_only=True)
	voyage_crew=VoyageCrewSerializer(many=False,read_only=True)
	voyage_ship=VoyageShipSerializer(many=False,read_only=True)
	voyage_slaves_numbers=VoyageSlavesNumbersSerializer(many=False,read_only=True)
	voyage_outcome=VoyageOutcomeSerializer(many=False,read_only=True)
	voyage_groupings=VoyageGroupingsSerializer(many=False,read_only=True)
	cargo=VoyageCargoConnectionSerializer(many=True,read_only=True)
	african_info=AfricanInfoSerializer(many=True,read_only=True)
	##DIDN'T DO LINKED VOYAGES YET
	class Meta:
		model=Voyage
		fields='__all__'

@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated request for filtered voyages.',
			summary='Paginated request for filtered voyages.',
			description='Here, we request page 2 (with 5 items per page) of voyages for which enslaved people were purchased in Cuba or Florida between 1820-1822.',
			value={
			  "filter": [
					{
						"varName":"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"searchTerm":1820,
						"op":"gte"
					},
					{
						"varName":"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"searchTerm":1822,
						"op":"lte"
					},
					{
						"varName":"voyage_itinerary__imp_principal_region_of_slave_purchase__name",
						"searchTerm":[
							"Florida",
							"Cuba"
						],
						"op":"in"
					}
				],
				"page": 2,
				"page_size": 5
			},
			request_only=True
		)
    ]
)
class VoyageListReqSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	filter=serializers.JSONField()


class VoyageListRespSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	count=serializers.IntegerField()
	results=VoyageSerializer(many=True,read_only=True)

############ AGGREGATION FIELD
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Filtered request for min/max',
			summary='Filtered request for min/max',
			description='Here, we request the min and max number of people who were embarked on individual voyages before the year 1620.',
			value={
				"varName": "voyage_slaves_numbers__imp_total_num_slaves_embarked",
				"filter": [
					{
						"varName":"voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"op":"lte",
						"searchTerm":1620
					}
				]
			},
			request_only=True
		)
    ]
)
class VoyageFieldAggregationRequestSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[k for k in Voyage_options])
	
class VoyageFieldAggregationResponseSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[k for k in Voyage_options])
	min=serializers.IntegerField()
	max=serializers.IntegerField()

############ REQUEST FILTER OBJECT ITEM SERIALIZERS
class VoyageFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["gte","lte","exact","icontains","in"])
	varName=serializers.ChoiceField(choices=[k for k in Voyage_options])
	searchTerm=serializers.ReadOnlyField(read_only=True)

############ OFFSET PAGINATION SERIALIZERS
class VoyageOffsetPaginationSerializer(serializers.Serializer):
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	total_results_count=serializers.IntegerField()

############ CROSSTAB SERIALIZERS
class VoyageCrossTabRequestSerializer(serializers.Serializer):
	columns=serializers.ListField(child=serializers.CharField())
	rows=serializers.CharField(max_length=500)
	binsize=serializers.IntegerField()
	rows_label=serializers.CharField(max_length=500,allow_null=True)
	agg_fn=serializers.CharField(max_length=500)
	value_field=serializers.CharField(max_length=500)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	
class VoyageCrossTabResponseSerializer(serializers.Serializer):
	tablestructure=serializers.JSONField()
	data=serializers.JSONField()
	medatadata=VoyageOffsetPaginationSerializer(many=False)

############ AUTOCOMPLETE SERIALIZERS
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated autocomplete on enslaver names',
			summary='Paginated autocomplete on enslaver names',
			description='Here, we are requesting 5 suggested values, starting with the 10th item, of enslaver aliases (names) associated with voyages between 1820-1840',
			value={
				"varname": "voyage_enslavement_relations__relation_enslavers__enslaver_alias__identity__principal_alias",
				"querystr": "george",
				"offset": 10,
				"limit": 5,
				"filter": [
					{
						"varName": "voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"op": "gte",
						"searchTerm": 1820
					},
					{
						"varName": "voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"op": "lte",
						"searchTerm": 1840
					}
				]
			},
			request_only=True
		)
    ]
)
class VoyageAutoCompleteRequestSerializer(serializers.Serializer):
	varname=serializers.CharField(max_length=500)
	querystr=serializers.CharField(max_length=255,allow_null=True,allow_blank=True)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=VoyageFilterItemSerializer(many=True,allow_null=True,allow_blank=True)

class VoyageAutoCompletekvSerializer(serializers.Serializer):
	value=serializers.CharField(max_length=255)

class VoyageAutoCompleteResponseSerializer(serializers.Serializer):
	suggested_values=VoyageAutoCompletekvSerializer(many=True)

