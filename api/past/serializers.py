# from rest_framework import serializers
# from rest_framework.fields import SerializerMethodField,IntegerField,CharField
# import re
# from .models import *
# from geo.models import *
# from voyage.models import *
# from voyage.serializers import *
# from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
# 
# #### SERIALIZERS COMMON TO BOTH ENSLAVERS AND ENSLAVED
# 
# class EnslaverRoleSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=EnslaverRole
# 		fields='__all__'
# 
# class EnslavementRelationTypeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=EnslavementRelationType
# 		fields='__all__'
# 
# ############VOYAGES
# class PastVoyageItinerarySerializer(serializers.ModelSerializer):
# 	imp_port_voyage_begin=PlaceSerializer(many=False)
# 	imp_principal_place_of_slave_purchase=PlaceSerializer(many=False)
# 	imp_principal_port_slave_dis=PlaceSerializer(many=False)
# 	imp_principal_region_slave_dis=RegionSerializer(many=False)
# 	imp_principal_region_of_slave_purchase=RegionSerializer(many=False)
# 	int_first_port_dis=PlaceSerializer(many=False)
# 	class Meta:
# 		model=VoyageItinerary
# 		fields=[
# 			'imp_port_voyage_begin',
# 			'imp_principal_place_of_slave_purchase',
# 			'imp_principal_port_slave_dis',
# 			'imp_principal_region_of_slave_purchase',
# 			'imp_principal_region_slave_dis',
# 			'int_first_port_dis'
# 		]
# 		
# class PastVoyageDatesSerializer(serializers.ModelSerializer):
# 	imp_arrival_at_port_of_dis_sparsedate=VoyageSparseDateSerializer(many=False)
# 	class Meta:
# 		model=VoyageDates
# 		fields=['imp_arrival_at_port_of_dis_sparsedate',]
# 
# class PastVoyageShipSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageShip
# 		fields=['ship_name',]
# 
# class PastVoyageParticularOutcomeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=ParticularOutcome
# 		fields='__all__'
# 
# class PastVoyageOutcomeSerializer(serializers.ModelSerializer):
# 	particular_outcome=PastVoyageParticularOutcomeSerializer(many=False)
# 	class Meta:
# 		model=VoyageOutcome
# 		fields=['particular_outcome']
# 
# class PastVoyageSerializer(serializers.ModelSerializer):
# 	voyage_itinerary=PastVoyageItinerarySerializer(many=False)
# 	voyage_dates=PastVoyageDatesSerializer(many=False)
# 	voyage_ship=PastVoyageShipSerializer(many=False)
# 	voyage_name_outcome=PastVoyageOutcomeSerializer(many=True,read_only=True)
# 	class Meta:
# 		model=Voyage
# 		fields=[
# 			'voyage_id',
# 			'id',
# 			'dataset',
# 			'voyage_itinerary',
# 			'voyage_dates',
# 			'voyage_ship',
# 			'voyage_name_outcome'
# 		]
# 
# 
# ############## SOURCES
# 
# class PastSourcePageSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=SourcePage
# 		exclude=['transcription']
# 
# class PastSourcePageConnectionSerializer(serializers.ModelSerializer):
# 	source_page=PastSourcePageSerializer(many=False)
# 	class Meta:
# 		model=SourcePageConnection
# 		fields='__all__'
# 
# class PastSourceSerializer(serializers.ModelSerializer):
# 	page_connection=PastSourcePageConnectionSerializer(many=True,read_only=True)
# 	class Meta:
# 		model=ZoteroSource
# 		fields='__all__'
# 
# class PastZoteroEnslaverConnectionSerializer(serializers.ModelSerializer):
# 	zotero_source=PastSourceSerializer(many=False)
# 	class Meta:
# 		model=ZoteroEnslaverConnection
# 		fields='__all__'
# 
# class PastZoteroEnslavedConnectionSerializer(serializers.ModelSerializer):
# 	zotero_source=PastSourceSerializer(many=False)
# 	class Meta:
# 		model=ZoteroEnslavedConnection
# 		fields='__all__'
# 
# 
# 
# 
# #######################
# 
# #### FROM ENSLAVED TO ENSLAVERS
# 
# 
# class CaptiveFateSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=CaptiveFate
# 		fields='__all__'
# 		
# class CaptiveStatusSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=CaptiveStatus
# 		fields='__all__'
# 
# class EnslavedEnslaverIdentitySerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=EnslaverIdentity
# 		fields='__all__'
# 
# class EnslavedEnslaverAliasSerializer(serializers.ModelSerializer):
# 	identity=EnslavedEnslaverIdentitySerializer(many=False)
# 	class Meta:
# 		model=EnslaverAlias
# 		fields='__all__'
# 
# class EnslavedEnslaverInRelationSerializer(serializers.ModelSerializer):
# 	enslaver_alias=EnslavedEnslaverAliasSerializer(many=False)
# 	role=EnslaverRoleSerializer(many=False)
# 	class Meta:
# 		model=EnslaverInRelation
# 		fields='__all__'
# 
# class EnslavedEnslavementRelationSerializer(serializers.ModelSerializer):
# 	relation_type=EnslavementRelationTypeSerializer(many=False)
# 	relation_enslavers=EnslavedEnslaverInRelationSerializer(many=True,read_only=False)
# 	voyage=PastVoyageSerializer(many=False)
# 	place=PlaceSerializer(many=False)
# 	class Meta:
# 		model=EnslavementRelation
# 		fields='__all__'
# 
# class EnslavedInRelationSerializer(serializers.ModelSerializer):
# 	relation=EnslavedEnslavementRelationSerializer(many=False)
# 	class Meta:
# 		model=EnslavedInRelation
# 		fields='__all__'
# 
# class LanguageGroupSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=LanguageGroup
# 		fields='__all__'
# 
# 
# @extend_schema_serializer(
# 	examples = [
# 		 OpenApiExample(
# 			'Ex. 1: numeric range',
# 			summary='Filter on a numeric range',
# 			description='Here, we search for named enslaved individualas who were, at the time of the transportation that we have recorded for them, between 5 and 15 years of age.',
# 			value={
# 				"age":
# 				[
# 					5,15
# 				]
# 			},
# 			request_only=True,
# 			response_only=False
# 		),
# 		OpenApiExample(
# 			'Ex. 2: array of str vals',
# 			summary='OR Filter on exact matches of known str values',
# 			description='Here, we search on str value fields for known exact matches to ANY of those values. Specifically, we are searching on a highly nested value: all named enslaved individuals who were on voyages that were principally disembarked in the Bahamas',
# 			value={
# 				"enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__name":
# 				[
# 					"Bahamas, port unspecified"
# 				]
# 			},
# 			request_only=True,
# 			response_only=False
# 		)
# 	]
# )
# class EnslavedSerializer(serializers.ModelSerializer):
# 	post_disembark_location=PlaceSerializer(many=False)
# 	captive_fate=CaptiveFateSerializer(many=False)
# 	enslaved_relations=EnslavedInRelationSerializer(many=True,read_only=True)
# 	captive_status=CaptiveStatusSerializer(many=False)
# 	language_group=LanguageGroupSerializer(many=False)
# 	enslaved_zotero_connections=PastZoteroEnslavedConnectionSerializer(many=True,read_only=True)
# 	class Meta:
# 		model=Enslaved
# 		fields='__all__'
# 
# 
# #######################
# 
# #### FROM ENSLAVERS TO ENSLAVED
# 
# class EnslaverEnslavedSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=Enslaved
# 		fields=['id','documented_name']
# 
# class EnslaverEnslavedInRelationSerializer(serializers.ModelSerializer):
# 	enslaved=EnslaverEnslavedSerializer(many=False)
# 	class Meta:
# 		model=EnslavedInRelation
# 		fields='__all__'
# 
# class EnslaverEnslavementRelationSerializer(serializers.ModelSerializer):
# 	enslaved_in_relation=EnslaverEnslavedInRelationSerializer(many=True,read_only=True)
# 	relation_type=EnslavementRelationTypeSerializer(many=False)
# 	place=PlaceSerializer(many=False)
# 	voyage=PastVoyageSerializer(many=False)
# 	class Meta:
# 		model=EnslavementRelation
# 		exclude=['text_ref','unnamed_enslaved_count']
# 
# class EnslaverInRelationSerializer(serializers.ModelSerializer):
# 	relation = EnslaverEnslavementRelationSerializer(many=False)
# 	role=EnslaverRoleSerializer(many=False)
# 	class Meta:
# 		model=EnslaverInRelation
# 		fields=['relation','role',]
# 
# class EnslaverAliasSerializer(serializers.ModelSerializer):
# 	enslaver_relations=EnslaverInRelationSerializer(
# 		many=True,
# 		read_only=True
# 	)
# 	class Meta:
# 		model=EnslaverAlias
# 		fields='__all__'
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# @extend_schema_serializer(
# 	examples = [
# 		 OpenApiExample(
# 			'Ex. 1: numeric range',
# 			summary='Filter on a numeric range',
# 			description='Here, we search for enslavers who participated in slave-trading voyages between the years of 1720-1722',
# 			value={
# 				"aliases__enslaver_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year":[1720,1722]
# 			},
# 			request_only=True,
# 			response_only=False
# 		),
# 		OpenApiExample(
# 			'Ex. 2: array of str vals',
# 			summary='OR Filter on exact matches of known str values',
# 			description='Here, we search for enslavers who participated in the enslavement of anyone named Bora',
# 			value={
# 				"aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__documented_name":["Bora"]
# 			},
# 			request_only=True,
# 			response_only=False
# 		)
# 	]
# )
# class EnslaverSerializer(serializers.ModelSerializer):
# 	principal_location=PlaceSerializer(many=False)
# 	enslaver_zotero_connections=PastZoteroEnslaverConnectionSerializer(many=True,read_only=True)
# 	aliases=EnslaverAliasSerializer(many=True,read_only=True)
# 	birth_place=PlaceSerializer(many=False)
# 	death_place=PlaceSerializer(many=False)
# 	class Meta:
# 		model=EnslaverIdentity
# 		fields='__all__'