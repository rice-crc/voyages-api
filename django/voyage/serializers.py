from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from document.models import *
# import pprint
# import gc
from common.nest import nest_selected_fields
from common.models import SparseDate
from past.models import *

#### GEO

class LocationSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

# ##### VESSEL VARIABLES ##### 
# 
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
	rig_of_vessel=RigOfVesselSerializer(many=False)
	imputed_nationality=NationalitySerializer(many=False)
	ton_type=TonTypeSerializer(many=False)
	vessel_construction_place=LocationSerializer(many=False)
	vessel_construction_region=LocationSerializer(many=False)
	registered_place=LocationSerializer(many=False)
	registered_region=LocationSerializer(many=False)
	
	class Meta:
		model=VoyageShip
		fields='__all__'

# ##### ENSLAVED NUMBERS ##### 

class VoyageSlavesNumbersSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageSlavesNumbers
		fields='__all__'

# ##### CREW NUMBERS ##### 

class VoyageCrewSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageCrew
		fields='__all__'



##### ITINERARY #####
# I TRIED TO USE THE LEGACY VOYAGES GEO MODELS
# BUT HAVING UNIQUE ID'S DISTRIBUTED ACROSS 3 NESTED TABLES IS SUCH A BRAIN-BREAKINGLY BAD DESIGN THAT IT'S NOT GOING TO FLY
# WE NOW HAVE A UNIFIED LOCATION OBJECT
# I HOPE THIS DOESN'T BREAK IMPUTATIONS (IT WILL)

class PlaceSerializer(serializers.ModelSerializer):
	geo_location=LocationSerializer(many=False)
	class Meta:
		model=Place
		fields=['geo_location',]

class RegionSerializer(serializers.ModelSerializer):
	geo_location=LocationSerializer(many=False)
	class Meta:
		model=Region
		fields=['geo_location',]

class BroadRegionSerializer(serializers.ModelSerializer):
	geo_location=LocationSerializer(many=False)
	class Meta:
		model=BroadRegion
		fields=['geo_location',]

class VoyageItinerarySerializer(serializers.ModelSerializer):
	port_of_departure=PlaceSerializer(many=False)
	int_first_port_emb=PlaceSerializer(many=False)
	int_second_port_emb=PlaceSerializer(many=False)
	int_first_region_purchase_slaves=RegionSerializer(many=False)
	int_second_region_purchase_slaves=RegionSerializer(many=False)
	int_first_port_dis=PlaceSerializer(many=False)
	int_second_port_dis=PlaceSerializer(many=False)
	int_first_region_slave_landing=RegionSerializer(many=False)
	imp_principal_region_slave_dis=RegionSerializer(many=False)
	int_second_place_region_slave_landing=PlaceSerializer(many=False)
	first_place_slave_purchase=PlaceSerializer(many=False)
	second_place_slave_purchase=PlaceSerializer(many=False)
	third_place_slave_purchase=PlaceSerializer(many=False)
	first_region_slave_emb=RegionSerializer(many=False)
	second_region_slave_emb=RegionSerializer(many=False)
	third_region_slave_emb=RegionSerializer(many=False)
	port_of_call_before_atl_crossing=PlaceSerializer(many=False)
	first_landing_place=PlaceSerializer(many=False)
	second_landing_place=PlaceSerializer(many=False)
	third_landing_place=PlaceSerializer(many=False)
	first_landing_region=RegionSerializer(many=False)
	second_landing_region=RegionSerializer(many=False)
	third_landing_region=RegionSerializer(many=False)
	place_voyage_ended=PlaceSerializer(many=False)
	region_of_return=RegionSerializer(many=False)
	broad_region_of_return=BroadRegionSerializer(many=False)
	imp_port_voyage_begin=PlaceSerializer(many=False)
	imp_region_voyage_begin=RegionSerializer(many=False)
	imp_broad_region_voyage_begin=BroadRegionSerializer(many=False)
	principal_place_of_slave_purchase=PlaceSerializer(many=False)
	imp_principal_place_of_slave_purchase=PlaceSerializer(many=False)
	imp_principal_region_of_slave_purchase=RegionSerializer(many=False)
	imp_broad_region_of_slave_purchase=BroadRegionSerializer(many=False)
	principal_port_of_slave_dis=PlaceSerializer(many=False)
	imp_principal_port_slave_dis=PlaceSerializer(many=False)
	imp_broad_region_slave_dis=BroadRegionSerializer(many=False)
	class Meta:
		model=VoyageItinerary
		fields='__all__'

# ##### OUTCOMES #####

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
	outcome_owner=OwnerOutcomeSerializer(many=False)
	outcome_slaves=SlavesOutcomeSerializer(many=False)
	particular_outcome=ParticularOutcomeSerializer(many=False)
	resistance=ResistanceSerializer(many=False)
	vessel_captured_outcome=VesselCapturedOutcomeSerializer(many=False)
	class Meta:
		model=VoyageOutcome
		fields='__all__'

#### ENSLAVERS

class EnslaverRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class EnslaverAliasSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslaverVoyageConnectionSerializer(serializers.ModelSerializer):
	enslaver_alias=EnslaverAliasSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverVoyageConnection
		fields=['enslaver_alias','role']

class SparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=SparseDate
		exclude=['id',]

class VoyageDatesSerializer(serializers.ModelSerializer):
	voyage_began_sparsedate=SparseDateSerializer(many=False)
	slave_purchase_began_sparsedate=SparseDateSerializer(many=False)
	vessel_left_port_sparsedate=SparseDateSerializer(many=False)
	first_dis_of_slaves_sparsedate=SparseDateSerializer(many=False)
	date_departed_africa_sparsedate=SparseDateSerializer(many=False)
	arrival_at_second_place_landing_sparsedate=SparseDateSerializer(many=False)
	third_dis_of_slaves_sparsedate=SparseDateSerializer(many=False)
	departure_last_place_of_landing_sparsedate=SparseDateSerializer(many=False)
	voyage_completed_sparsedate=SparseDateSerializer(many=False)
	imp_voyage_began_sparsedate=SparseDateSerializer(many=False)
	imp_departed_africa_sparsedate=SparseDateSerializer(many=False)
	imp_arrival_at_port_of_dis_sparsedate=SparseDateSerializer(many=False)
	class Meta:
		model=VoyageDates
		fields='__all__'

class SourcePageSerializer(serializers.ModelSerializer):
	class Meta:
		model=SourcePage
		fields='__all__'

class ZoteroPageConnectionSerializer(serializers.ModelSerializer):
	source_page=SourcePageSerializer(many=False)
	class Meta:
		model=SourcePageConnection
		fields=['source_page',]

class VoyageZoteroSerializer(serializers.ModelSerializer):
	page_connection=ZoteroPageConnectionSerializer(many=True,read_only=True)
	class Meta:
		model=ZoteroSource
		exclude=['enslaved_people','voyages','enslavers',]

class VoyageSerializer(serializers.ModelSerializer):
	voyage_zoterorefs=VoyageZoteroSerializer(many=True,read_only=True)
	voyage_itinerary=VoyageItinerarySerializer(many=False)
	voyage_dates=VoyageDatesSerializer(many=False)
	voyage_enslaver_connection=EnslaverVoyageConnectionSerializer(many=True,read_only=True)
	voyage_crew=VoyageCrewSerializer(many=False)
	voyage_ship=VoyageShipSerializer(many=False)
	voyage_slaves_numbers=VoyageSlavesNumbersSerializer(many=False)
	#WHY! WHY??? THERE'S ONLY ONE OUTCOME PER VOYAGE! WHY??????
	voyage_name_outcome=VoyageOutcomeSerializer(many=True,read_only=True)
	class Meta:
		model=Voyage
		fields='__all__'
