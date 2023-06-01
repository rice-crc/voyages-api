# from rest_framework import serializers
# from rest_framework.fields import SerializerMethodField,IntegerField,CharField
# import re
# from .models import *
# import pprint
# import gc
# from common.nest import nest_selected_fields
# from common.serializers import *
# from geo.serializers import *
# # from docs.serializers import *
# 
# ##### VESSEL VARIABLES ##### 
# 
# class RigOfVesselSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=RigOfVessel
# 		fields='__all__'
# 
# class NationalitySerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=Nationality
# 		fields='__all__'
# 
# class TonTypeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=TonType
# 		fields='__all__'
# 
# class VoyageShipSerializer(serializers.ModelSerializer):
# 	rig_of_vessel=RigOfVesselSerializer(many=False)
# 	imputed_nationality=NationalitySerializer(many=False)
# 	ton_type=TonTypeSerializer(many=False)
# 	vessel_construction_place=LocationSerializer(many=False)
# 	vessel_construction_region=LocationSerializer(many=False)
# 	registered_place=LocationSerializer(many=False)
# 	registered_region=LocationSerializer(many=False)
# 	
# 	class Meta:
# 		model=VoyageShip
# 		fields='__all__'
# 
# ##### NUMBERS ##### 
# 
# class VoyageSlavesNumbersSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageSlavesNumbers
# 		fields='__all__'
# 
# 
# 
# ##### ITINERARY #####
# # I TRIED TO USE THE LEGACY VOYAGES GEO MODELS
# # BUT HAVING UNIQUE ID'S DISTRIBUTED ACROSS 3 NESTED TABLES IS SUCH A BRAIN-BREAKINGLY BAD DESIGN THAT IT'S NOT GOING TO FLY
# # WE NOW HAVE A UNIFIED LOCATION OBJECT
# # I HOPE THIS DOESN'T BREAK IMPUTATIONS (IT WILL)
# 
# class VoyageItinerarySerializer(serializers.ModelSerializer):
# 	port_of_departure=LocationSerializer(many=False)
# 	int_first_port_emb=LocationSerializer(many=False)
# 	int_second_port_emb=LocationSerializer(many=False)
# 	int_first_region_purchase_slaves=LocationSerializer(many=False)
# 	int_second_region_purchase_slaves=LocationSerializer(many=False)
# 	int_first_port_dis=LocationSerializer(many=False)
# 	int_second_port_dis=LocationSerializer(many=False)
# 	int_first_region_slave_landing=LocationSerializer(many=False)
# 	imp_principal_region_slave_dis=LocationSerializer(many=False)
# 	int_second_place_region_slave_landing=LocationSerializer(many=False)
# 	first_place_slave_purchase=LocationSerializer(many=False)
# 	second_place_slave_purchase=LocationSerializer(many=False)
# 	third_place_slave_purchase=LocationSerializer(many=False)
# 	first_region_slave_emb=LocationSerializer(many=False)
# 	second_region_slave_emb=LocationSerializer(many=False)
# 	third_region_slave_emb=LocationSerializer(many=False)
# 	port_of_call_before_atl_crossing=LocationSerializer(many=False)
# 	first_landing_place=LocationSerializer(many=False)
# 	second_landing_place=LocationSerializer(many=False)
# 	third_landing_place=LocationSerializer(many=False)
# 	first_landing_region=LocationSerializer(many=False)
# 	second_landing_region=LocationSerializer(many=False)
# 	third_landing_region=LocationSerializer(many=False)
# 	place_voyage_ended=LocationSerializer(many=False)
# 	region_of_return=LocationSerializer(many=False)
# 	broad_region_of_return=LocationSerializer(many=False)
# 	imp_port_voyage_begin=LocationSerializer(many=False)
# 	imp_region_voyage_begin=LocationSerializer(many=False)
# 	imp_broad_region_voyage_begin=LocationSerializer(many=False)
# 	principal_place_of_slave_purchase=LocationSerializer(many=False)
# 	imp_principal_place_of_slave_purchase=LocationSerializer(many=False)
# 	imp_principal_region_of_slave_purchase=LocationSerializer(many=False)
# 	imp_broad_region_of_slave_purchase=LocationSerializer(many=False)
# 	principal_port_of_slave_dis=LocationSerializer(many=False)
# 	imp_principal_port_slave_dis=LocationSerializer(many=False)
# 	imp_broad_region_slave_dis=LocationSerializer(many=False)
# 	class Meta:
# 		model=VoyageItinerary
# 		fields='__all__'
# 
# ##### SOURCES ##### 
# 
# class VoyageSourcesSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageSources
# 		fields='__all__'
# 		
# ##### OUTCOMES #####
# 
# class ParticularOutcomeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=ParticularOutcome
# 		fields='__all__'
# 
# 
# class SlavesOutcomeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=SlavesOutcome
# 		fields='__all__'
# 		
# class ResistanceSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=Resistance
# 		fields='__all__'
# 
# class OwnerOutcomeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=OwnerOutcome
# 		fields='__all__'
# 
# class VesselCapturedOutcomeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VesselCapturedOutcome
# 		fields='__all__'
# 		
# class VoyageOutcomeSerializer(serializers.ModelSerializer):
# 	outcome_owner=OwnerOutcomeSerializer(many=False)
# 	outcome_slaves=SlavesOutcomeSerializer(many=False)
# 	particular_outcome=ParticularOutcomeSerializer(many=False)
# 	resistance=ResistanceSerializer(many=False)
# 	vessel_captured_outcome=VesselCapturedOutcomeSerializer(many=False)
# 	class Meta:
# 		model=VoyageOutcome
# 		fields='__all__'
# 
# ##### GROUPINGS ##### 
# 
# class VoyageGroupingsSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageGroupings
# 		fields='__all__'
# 
# ##### CREW, CAPTAIN, OWNER ##### 
# 
# class VoyageCrewSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageCrew
# 		fields='__all__'
# 
# class VoyageCaptainSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageCaptain
# 		fields='__all__'
# 
# class VoyageCaptainConnectionSerializer(serializers.ModelSerializer):
# 	captain=VoyageCaptainSerializer(many=False)
# 	class Meta:
# 		model=VoyageCaptainConnection
# 		fields='__all__'
# 	
# class VoyageShipOwnerSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageShipOwner
# 		fields='__all__'
# 
# 
# class VoyageShipOwnerConnectionSerializer(serializers.ModelSerializer):
# 	owner=VoyageShipOwnerSerializer(many=False)
# 	class Meta:
# 		model=VoyageShipOwnerConnection
# 		fields='__all__'
# 
# class VoyageDatesSerializer(serializers.ModelSerializer):
# 	voyage_began=SparseDateSerializer(many=False)
# 	slave_purchase_began=SparseDateSerializer(many=False)
# 	vessel_left_port=SparseDateSerializer(many=False)
# 	first_dis_of_slaves=SparseDateSerializer(many=False)
# 	date_departed_africa=SparseDateSerializer(many=False)
# 	arrival_at_second_place_landing=SparseDateSerializer(many=False)
# 	third_dis_of_slaves=SparseDateSerializer(many=False)
# 	departure_last_place_of_landing=SparseDateSerializer(many=False)
# 	voyage_completed=SparseDateSerializer(many=False)
# 	class Meta:
# 		model=VoyageDates
# 		fields='__all__'
# 
# class VoyageSourcesConnectionSerializer(serializers.ModelSerializer):
# 	source=VoyageSourcesSerializer(many=False)
# 	class Meta:
# 		model=VoyageSourcesConnection
# 		fields='__all__'
# 
# class VoyageSerializer(serializers.ModelSerializer):
# 	voyage_itinerary=VoyageItinerarySerializer(many=False)
# 	voyage_dates=VoyageDatesSerializer(many=False)
# 	voyage_groupings=VoyageGroupingsSerializer(many=False)
# 	voyage_crew=VoyageCrewSerializer(many=False)
# 	voyage_ship=VoyageShipSerializer(many=False)
# 	voyage_captainconnection=VoyageCaptainConnectionSerializer(many=True,read_only=True)
# 	voyage_shipownerconnection=VoyageShipOwnerConnectionSerializer(many=True,read_only=True)
# 	voyage_slaves_numbers=VoyageSlavesNumbersSerializer(many=False)
# 	voyage_outcome=VoyageOutcomeSerializer(many=False)
# 	voyage_sourceconnection=VoyageSourcesConnectionSerializer(many=True,read_only=True)
# # 	
# 	class Meta:
# 		model=Voyage
# 		fields='__all__'
# # 		
# # 		
