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

class VoyageCRUDLocationSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Location
		fields=['value',]
	def create(self, validated_data):
		return Location.objects.get(value=validated_data['value'])
	def update(self, instance,validated_data):
		return Location.objects.get(value=validated_data['value'])

##### VESSEL VARIABLES ##### 

class CRUDRigOfVesselSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=RigOfVessel
		fields='__all__'
	def create(self, validated_data):
		try:
			return RigOfVessel.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CRUDRigOfVesselSerializer, self).create(validated_data)

class CRUDNationalitySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Nationality
		fields='__all__'
	def create(self, validated_data):
		try:
			return Nationality.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CRUDNationalitySerializer, self).create(validated_data)


class CRUDTonTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=TonType
		fields='__all__'
	def create(self, validated_data):
		try:
			return TonType.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CRUDTonTypeSerializer, self).create(validated_data)

class VoyageCRUDShipSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
	rig_of_vessel=CRUDRigOfVesselSerializer(many=False,allow_null=True)
	imputed_nationality=CRUDNationalitySerializer(many=False,allow_null=True)
	nationality_ship=CRUDNationalitySerializer(many=False,allow_null=True)
	ton_type=CRUDTonTypeSerializer(many=False,allow_null=True)
	vessel_construction_place=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	vessel_construction_region=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	registered_place=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	registered_region=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	class Meta:
		model=VoyageShip
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageShip.objects.get(voyage=validated_data['voyage'])
		except ObjectDoesNotExist:
			return super(VoyageCRUDShipSerializer, self).create(validated_data)


##### ENSLAVED NUMBERS ##### 

class VoyageCRUDSlavesNumbersSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=VoyageSlavesNumbers
		fields='__all__'

##### CREW NUMBERS ##### 

class VoyageCRUDCrewSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=VoyageCrew
		fields='__all__'



##### ITINERARY #####

class VoyageCRUDItinerarySerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
	port_of_departure=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_first_port_emb=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_second_port_emb=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_first_region_purchase_slaves=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_second_region_purchase_slaves=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_first_port_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_second_port_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_first_region_slave_landing=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_principal_region_slave_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_second_place_region_slave_landing=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	first_place_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	second_place_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	third_place_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	first_region_slave_emb=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	second_region_slave_emb=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	third_region_slave_emb=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	port_of_call_before_atl_crossing=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	first_landing_place=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	second_landing_place=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	third_landing_place=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	first_landing_region=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	second_landing_region=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	third_landing_region=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	place_voyage_ended=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	region_of_return=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	broad_region_of_return=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_port_voyage_begin=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_region_voyage_begin=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_broad_region_voyage_begin=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	principal_place_of_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_principal_place_of_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_principal_region_of_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_broad_region_of_slave_purchase=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	principal_port_of_slave_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_principal_port_slave_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	imp_broad_region_slave_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_fourth_port_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_third_port_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_fourth_port_dis=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_third_place_region_slave_landing=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	int_fourth_place_region_slave_landing=VoyageCRUDLocationSerializer(many=False,allow_null=True)
	class Meta:
		model=VoyageItinerary
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageItinerary.objects.get(voyage=validated_data['voyage'])
		except ObjectDoesNotExist:
			return super(VoyageCRUDItinerarySerializer, self).create(validated_data)

##### OUTCOMES #####

class ParticularCRUDOutcomeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=ParticularOutcome
		fields='__all__'
	def create(self, validated_data):
		try:
			return ParticularOutcome.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(ParticularCRUDOutcomeSerializer, self).create(validated_data)

class SlavesCRUDOutcomeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=SlavesOutcome
		fields='__all__'
	def create(self, validated_data):
		try:
			return SlavesOutcome.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(SlavesCRUDOutcomeSerializer, self).create(validated_data)
		
class ResistanceCRUDSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Resistance
		fields='__all__'
	def create(self, validated_data):
		try:
			return Resistance.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(ResistanceCRUDSerializer, self).create(validated_data)

class OwnerCRUDOutcomeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=OwnerOutcome
		fields='__all__'
	def create(self, validated_data):
		try:
			return OwnerOutcome.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(OwnerCRUDOutcomeSerializer, self).create(validated_data)

class VesselCRUDCapturedOutcomeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=VesselCapturedOutcome
		fields='__all__'
	def create(self, validated_data):
		try:
			return VesselCapturedOutcome.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(VesselCRUDCapturedOutcomeSerializer, self).create(validated_data)
		
class VoyageCRUDOutcomeSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
	outcome_owner=OwnerCRUDOutcomeSerializer(many=False,allow_null=True)
	outcome_slaves=SlavesCRUDOutcomeSerializer(many=False,allow_null=True)
	particular_outcome=ParticularCRUDOutcomeSerializer(many=False,allow_null=True)
	resistance=ResistanceCRUDSerializer(many=False,allow_null=True)
	vessel_captured_outcome=VesselCRUDCapturedOutcomeSerializer(many=False,allow_null=True)
	class Meta:
		model=VoyageOutcome
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageOutcome.objects.get(voyage=validated_data['voyage'])
		except ObjectDoesNotExist:
			return super(VoyageCRUDOutcomeSerializer, self).create(validated_data)


#### DATES #####
class VoyageCRUDSparseDateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=VoyageSparseDate
		fields='__all__'
		
class VoyageCRUDDatesSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
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
			return super(VoyageCRUDDatesSerializer, self).create(validated_data)
	
	

class VoyageCRUDSourceSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Source
		fields='__all__'

class VoyageCRUDVoyageSourceConnectionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	source=VoyageCRUDSourceSerializer(many=False,read_only=True)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

class VoyageCRUDEnslaverRoleSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class VoyageCRUDEnslaverIdentitySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class VoyageCRUDEnslaverAliasSerializer(WritableNestedModelSerializer):
	identity=VoyageCRUDEnslaverIdentitySerializer(many=False,)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class VoyageCRUDEnslaverInRelationSerializer(WritableNestedModelSerializer):
	roles=VoyageCRUDEnslaverRoleSerializer(many=True,read_only=False)
	enslaver_alias=VoyageCRUDEnslaverAliasSerializer(many=False,read_only=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class VoyageCRUDEnslavedSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=['id','documented_name']

class VoyageCRUDEnslavementRelationTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class VoyageCRUDEnslavementRelationsSerializer(WritableNestedModelSerializer):
	relation_enslaved=VoyageCRUDEnslavedSerializer(many=True,read_only=True)
	relation_enslavers=VoyageCRUDEnslaverInRelationSerializer(many=True)
	relation_type=VoyageCRUDEnslavementRelationTypeSerializer(many=False,read_only=True)
	class Meta:
		model=EnslavementRelation
		fields='__all__'



class VoyageCRUDGroupingsSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=VoyageGroupings
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageGroupings.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(VoyageCRUDGroupingsSerializer, self).create(validated_data)

class AfricanCRUDInfoSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=AfricanInfo
		fields='__all__'
	def create(self, validated_data):
		try:
			return AfricanInfo.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(AfricanCRUDInfoSerializer, self).create(validated_data)


class CRUDCargoTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=CargoType
		fields='__all__'
	def create(self, validated_data):
		try:
			return CargoType.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CRUDCargoTypeSerializer, self).create(validated_data)

class CRUDCargoUnitSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=CargoUnit
		fields='__all__'
	def create(self, validated_data):
		try:
			return CargoUnit.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CRUDCargoUnitSerializer, self).create(validated_data)

class VoyageCRUDCargoConnectionSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
	cargo=CRUDCargoTypeSerializer(many=False,allow_null=True)
	unit=CRUDCargoUnitSerializer(many=False,allow_null=True)
	amount=serializers.FloatField(allow_null=True)
	class Meta:
		model=VoyageCargoConnection
		fields='__all__'
	def create(self, validated_data):
		try:
			return VoyageCargoConnection.objects.get(voyage_id=validated_data['voyage'],cargo__name=validated_data['cargo']['name'])
		except ObjectDoesNotExist:
			return super(VoyageCRUDCargoConnectionSerializer, self).create(validated_data)


class VoyageCRUDSerializer(WritableNestedModelSerializer):
	voyage_source_connections=VoyageCRUDVoyageSourceConnectionSerializer(many=True,allow_null=True)
	voyage_itinerary=VoyageCRUDItinerarySerializer(many=False,allow_null=True)
	voyage_dates=VoyageCRUDDatesSerializer(many=False,allow_null=True)
	voyage_enslavement_relations=VoyageCRUDEnslavementRelationsSerializer(many=True,allow_null=True)
	voyage_crew=VoyageCRUDCrewSerializer(many=False,allow_null=True)
	voyage_ship=VoyageCRUDShipSerializer(many=False,allow_null=True)
	voyage_slaves_numbers=VoyageCRUDSlavesNumbersSerializer(many=False,allow_null=True)
	voyage_outcome=VoyageCRUDOutcomeSerializer(many=False,allow_null=True)
	voyage_groupings=VoyageCRUDGroupingsSerializer(many=False,allow_null=True)
	cargo=VoyageCRUDCargoConnectionSerializer(many=True,allow_null=True)
	african_info=AfricanCRUDInfoSerializer(many=True,allow_null=True)
	class Meta:
		model=Voyage
		fields='__all__'