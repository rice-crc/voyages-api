from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import Source,Page,SourcePageConnection,SourceVoyageConnection
from geo.models import Location
from past.models import *
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin

#### GEO

class VoyageLocationSerializerCRUD(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Location
		exclude=('parent',)

##### VESSEL VARIABLES ##### 

class RigOfVesselSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=RigOfVessel
		fields='__all__'

class NationalitySerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=Nationality
		fields='__all__'

class TonTypeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=TonType
		fields='__all__'

class VoyageShipSerializerCRUD(serializers.ModelSerializer):
	rig_of_vessel=RigOfVesselSerializerCRUD(many=False,allow_null=True)
	imputed_nationality=NationalitySerializerCRUD(many=False,allow_null=True)
	nationality_ship=NationalitySerializerCRUD(many=False,allow_null=True)
	ton_type=TonTypeSerializerCRUD(many=False,allow_null=True)
	vessel_construction_place=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	vessel_construction_region=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	registered_place=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	registered_region=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	class Meta:
		model=VoyageShip
		fields='__all__'

##### ENSLAVED NUMBERS #####

class VoyageSlavesNumbersSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=VoyageSlavesNumbers
		fields='__all__'

##### CREW NUMBERS #####

class VoyageCrewSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=VoyageCrew
		fields='__all__'

##### ITINERARY #####

class VoyageItinerarySerializerCRUD(serializers.ModelSerializer):
	port_of_departure=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_first_port_emb=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_second_port_emb=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_first_region_purchase_slaves=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_second_region_purchase_slaves=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_first_port_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_second_port_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_first_region_slave_landing=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_principal_region_slave_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_second_place_region_slave_landing=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	first_place_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	second_place_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	third_place_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	first_region_slave_emb=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	second_region_slave_emb=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	third_region_slave_emb=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	port_of_call_before_atl_crossing=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	first_landing_place=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	second_landing_place=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	third_landing_place=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	first_landing_region=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	second_landing_region=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	third_landing_region=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	place_voyage_ended=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	region_of_return=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	broad_region_of_return=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_port_voyage_begin=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_region_voyage_begin=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_broad_region_voyage_begin=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	principal_place_of_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_principal_place_of_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_principal_region_of_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_broad_region_of_slave_purchase=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	principal_port_of_slave_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_principal_port_slave_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	imp_broad_region_slave_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_fourth_port_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_third_port_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_fourth_port_dis=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_third_place_region_slave_landing=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	int_fourth_place_region_slave_landing=VoyageLocationSerializerCRUD(many=False,allow_null=True)
	class Meta:
		model=VoyageItinerary
		fields='__all__'

##### OUTCOMES #####

class ParticularOutcomeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=ParticularOutcome
		fields='__all__'

class SlavesOutcomeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=SlavesOutcome
		fields='__all__'
		
class ResistanceSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=Resistance
		fields='__all__'

class OwnerOutcomeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=OwnerOutcome
		fields='__all__'

class VesselCapturedOutcomeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=VesselCapturedOutcome
		fields='__all__'
		
class VoyageOutcomeSerializerCRUD(serializers.ModelSerializer):
	outcome_owner=OwnerOutcomeSerializerCRUD(many=False,allow_null=True)
	outcome_slaves=SlavesOutcomeSerializerCRUD(many=False,allow_null=True)
	particular_outcome=ParticularOutcomeSerializerCRUD(many=False,allow_null=True)
	resistance=ResistanceSerializerCRUD(many=False,allow_null=True)
	vessel_captured_outcome=VesselCapturedOutcomeSerializerCRUD(many=False,allow_null=True)
	class Meta:
		model=VoyageOutcome
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageOutcome.objects.get(voyage=validated_data['voyage'])
		except ObjectDoesNotExist:
			return super(VoyageOutcomeSerializerCRUD, self).create(validated_data)

#### DATES #####
class VoyageCRUDSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageSparseDate
		fields='__all__'
		
class VoyageDatesSerializerCRUD(UniqueFieldsMixin,WritableNestedModelSerializer):
	voyage_began_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	slave_purchase_began_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	vessel_left_port_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	first_dis_of_slaves_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	date_departed_africa_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	arrival_at_second_place_landing_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	third_dis_of_slaves_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	departure_last_place_of_landing_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	voyage_completed_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	imp_voyage_began_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	imp_departed_africa_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	imp_arrival_at_port_of_dis_sparsedate=VoyageCRUDSparseDateSerializer(many=False,allow_null=True)
	class Meta:
		model=VoyageDates
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageDates.objects.get(voyage=validated_data['voyage'])
		except ObjectDoesNotExist:
			return super(VoyageDatesSerializerCRUD, self).create(validated_data)

class VoyageSourceConnectionSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class VoyageEnslavementRelationsSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class VoyageGroupingsSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=VoyageGroupings
		fields='__all__'

class AfricanInfoSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=AfricanInfo
		fields='__all__'

class CargoTypeSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=CargoType
		fields='__all__'

class CargoUnitSerializerCRUD(serializers.ModelSerializer):
	class Meta:
		model=CargoUnit
		fields='__all__'
		
class VoyageCargoConnectionSerializerCRUD(serializers.ModelSerializer):
	cargo=CargoTypeSerializerCRUD(many=False,allow_null=True)
	unit=CargoUnitSerializerCRUD(many=False,allow_null=True)
	class Meta:
		model=VoyageCargoConnection
		fields='__all__'

class VoyageSerializerCRUD(WritableNestedModelSerializer):
	voyage_source_connections=VoyageSourceConnectionSerializerCRUD(many=True)
	voyage_itinerary=VoyageItinerarySerializerCRUD(many=False)
	voyage_dates=VoyageDatesSerializerCRUD(many=False)
	voyage_enslavement_relations=VoyageEnslavementRelationsSerializerCRUD(many=True,allow_null=True)
	voyage_crew=VoyageCrewSerializerCRUD(many=False)
	voyage_ship=VoyageShipSerializerCRUD(many=False)
	voyage_slaves_numbers=VoyageSlavesNumbersSerializerCRUD(many=False)
	voyage_outcome=VoyageOutcomeSerializerCRUD(many=False)
	voyage_groupings=VoyageGroupingsSerializerCRUD(many=False)
	cargo=VoyageCargoConnectionSerializerCRUD(many=True,allow_null=True)
	african_info=AfricanInfoSerializerCRUD(many=True,allow_null=True)
	class Meta:
		model=Voyage
		fields='__all__'