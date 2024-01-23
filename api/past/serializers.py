# from rest_framework import serializers
# from rest_framework.fields import SerializerMethodField,IntegerField,CharField
# import re
# from .models import *
# from geo.models import Location
# from voyage.models import *
# from document.models import Source, SourceEnslavedConnection, SourceEnslaverConnection
# from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
# from django.core.exceptions import ObjectDoesNotExist
# from drf_writable_nested.serializers import WritableNestedModelSerializer
# from drf_writable_nested.mixins import UniqueFieldsMixin
# 
# 
# class CRUDPASTSparseDateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	class Meta:
# 		model=PASTSparseDate
# 		fields='__all__'
# 		
# class CRUDRegisterCountrySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	class Meta:
# 		model=RegisterCountry
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return RegisterCountry.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDRegisterCountrySerializer, self).create(validated_data)
# 
# 
# ############ SERIALIZERS COMMON TO BOTH ENSLAVERS AND ENSLAVED
# 
# class CRUDEnslaverRoleSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	name=serializers.CharField(allow_null=False)
# 	class Meta:
# 		model=EnslaverRole
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return EnslaverRole.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDEnslaverRoleSerializer, self).create(validated_data)
# 
# 
# class CRUDEnslavementRelationTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	class Meta:
# 		model=EnslavementRelationType
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return EnslavementRelationType.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDEnslavementRelationTypeSerializer, self).create(validated_data)
# 
# class CRUDPastLocationSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	class Meta:
# 		model=Location
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return Location.objects.get(value=validated_data['value'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDPastLocationSerializer, self).create(validated_data)
# 
# class CRUDPastSourceSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=Source
# 		fields='__all__'
#  
# ############ VOYAGES
# 
# class CRUDPastVoyageItinerarySerializer(serializers.ModelSerializer):
# 	imp_port_voyage_begin=CRUDPastLocationSerializer(many=False)
# 	imp_principal_place_of_slave_purchase=CRUDPastLocationSerializer(many=False)
# 	imp_principal_port_slave_dis=CRUDPastLocationSerializer(many=False)
# 	imp_principal_region_slave_dis=CRUDPastLocationSerializer(many=False)
# 	imp_principal_region_of_slave_purchase=CRUDPastLocationSerializer(many=False)
# 	int_first_port_dis=CRUDPastLocationSerializer(many=False)
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
# class CRUDPastVoyageDatesSerializer(serializers.ModelSerializer):
# 	imp_arrival_at_port_of_dis_sparsedate=CRUDPASTSparseDateSerializer(many=False)
# 	class Meta:
# 		model=VoyageDates
# 		fields=['imp_arrival_at_port_of_dis_sparsedate',]
# 
# class CRUDPastVoyageShipSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageShip
# 		fields=['ship_name',]
# 
# class CRUDPastVoyageParticularOutcomeSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=ParticularOutcome
# 		fields='__all__'
# 
# class CRUDPastVoyageOutcomeSerializer(serializers.ModelSerializer):
# 	particular_outcome=CRUDPastVoyageParticularOutcomeSerializer(many=False)
# 	class Meta:
# 		model=VoyageOutcome
# 		fields=['particular_outcome']
# 
# class CRUDPastVoyageSerializer(serializers.ModelSerializer):
# 	voyage_itinerary=CRUDPastVoyageItinerarySerializer(many=False)
# 	voyage_dates=CRUDPastVoyageDatesSerializer(many=False)
# 	voyage_ship=CRUDPastVoyageShipSerializer(many=False)
# 	voyage_outcome=CRUDPastVoyageOutcomeSerializer(many=False)
# 	class Meta:
# 		model=Voyage
# 		fields=[
# 			'voyage_id',
# 			'id',
# 			'dataset',
# 			'voyage_itinerary',
# 			'voyage_dates',
# 			'voyage_ship',
# 			'voyage_outcome'
# 		]
# 
# ####################### ENSLAVED M2M CONNECTIONS
# 
# #### FROM ENSLAVED TO ENSLAVERS
# class CRUDEnslavedEnslaverIdentitySerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=EnslaverIdentity
# 		fields='__all__'
# 
# class CRUDEnslavedEnslaverAliasSerializer(serializers.ModelSerializer):
# 	identity=CRUDEnslavedEnslaverIdentitySerializer(many=False)
# 	class Meta:
# 		model=EnslaverAlias
# 		fields='__all__'
# 
# class CRUDEnslavedEnslaverInRelationSerializer(serializers.ModelSerializer):
# 	enslaver_alias=CRUDEnslavedEnslaverAliasSerializer(many=False)
# 	roles=CRUDEnslaverRoleSerializer(many=True)
# 	class Meta:
# 		model=EnslaverInRelation
# 		fields='__all__'
# 
# class CRUDEnslavedEnslavementRelationSerializer(WritableNestedModelSerializer):
# 	relation_type=CRUDEnslavementRelationTypeSerializer(many=False)
# 	relation_enslavers=CRUDEnslavedEnslaverInRelationSerializer(many=True)
# 	voyage=CRUDPastVoyageSerializer(many=False)
# 	place=CRUDPastLocationSerializer(many=False)
# 	class Meta:
# 		model=EnslavementRelation
# 		fields='__all__'
# 
# #### FROM ENSLAVED TO SOURCES
# class CRUDPastSourceEnslavedConnectionSerializer(serializers.ModelSerializer):
# 	source=CRUDPastSourceSerializer(many=False)
# 	class Meta:
# 		model=SourceEnslavedConnection
# 		fields='__all__'
# 
# #######################
# 
# #### ENSLAVED & ONE-TO-ONE RELATIONS
# 
# class CRUDCaptiveFateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	
# 	class Meta:
# 		model=CaptiveFate
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return CaptiveFate.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDCaptiveFateSerializer, self).create(validated_data)
# 
# 
# 
# class CRUDCaptiveStatusSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 
# 	class Meta:
# 		model=CaptiveStatus
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return CaptiveStatus.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDCaptiveStatusSerializer, self).create(validated_data)
# 
# class CRUDLanguageGroupSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	longitude=serializers.FloatField(allow_null=True)
# 	latitude=serializers.FloatField(allow_null=True)
# 	class Meta:
# 		model=LanguageGroup
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return LanguageGroup.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDLanguageGroupSerializer, self).create(validated_data)
# 
# class CRUDRegisterCountrySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	class Meta:
# 		model=RegisterCountry
# 		fields='__all__'
# 	def create(self, validated_data):
# 		try:
# 			return RegisterCountry.objects.get(name=validated_data['name'])
# 		except ObjectDoesNotExist:
# 			return super(CRUDRegisterCountrySerializer, self).create(validated_data)
# 
# class CRUDEnslavedInRelationSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
# 	relation=CRUDEnslavedEnslavementRelationSerializer(many=False)
# 	class Meta:
# 		model=EnslavedInRelation
# 		fields='__all__'
# 
# #######################
# 
# #### FROM ENSLAVERS TO ENSLAVED
# 
# class CRUDPastSourceEnslaverConnectionSerializer(serializers.ModelSerializer):
# 	source=CRUDPastSourceSerializer(many=False)
# 	class Meta:
# 		model=SourceEnslaverConnection
# 		fields='__all__'
# 
# 
# ####################### ENSLAVED M2M CONNECTIONS
# 
# #### FROM ENSLAVERS TO ENSLAVED
# 
# class CRUDEnslaverEnslavedSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model=Enslaved
# 		fields=['id','documented_name']
# 
# class CRUDEnslaverEnslavementRelationSerializer(serializers.ModelSerializer):
# 	enslaved_in_relation=CRUDEnslaverEnslavedSerializer(many=True)
# 	relation_type=CRUDEnslavementRelationTypeSerializer(many=False)
# 	place=CRUDPastLocationSerializer(many=False)
# 	voyage=CRUDPastVoyageSerializer(many=False)
# 	class Meta:
# 		model=EnslavementRelation
# 		fields='__all__'
# 
# class CRUDEnslaverInRelationSerializer(serializers.ModelSerializer):
# 	relation = CRUDEnslaverEnslavementRelationSerializer(many=False)
# 	roles=CRUDEnslaverRoleSerializer(many=True)
# 	class Meta:
# 		model=EnslaverInRelation
# 		fields='__all__'
# 
# class CRUDEnslaverAliasSerializer(WritableNestedModelSerializer):
# 	id=serializers.IntegerField(allow_null=False)
# 	enslaver_relations=CRUDEnslaverInRelationSerializer(many=True,allow_null=True)
# 	alias=serializers.CharField(allow_null=False)
# 	manual_id=serializers.CharField(allow_null=True)
# 	human_reviewed=serializers.BooleanField(allow_null=True)
# 	legacy_id=serializers.IntegerField(allow_null=True)
# 	class Meta:
# 		model=EnslaverAlias
# 		fields='__all__'
# 
# #### FROM ENSLAVERS TO SOURCES
# 
# 
# class EnslaverInRelationCRUDSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
# 	roles=CRUDEnslaverRoleSerializer(many=True,allow_null=False)
# 	class Meta:
# 		model=EnslaverInRelation
# 		exclude=['relation']
# 	def create(self, validated_data):
# 		try:
# 			return EnslaverInRelation.objects.get(id=validated_data['id'])
# 		except:
# 			return super(EnslaverInRelationCRUDSerializer, self).create(validated_data)
# 	def update(self, instance,validated_data):
# 		try:
# 			return EnslaverInRelation.objects.get(id=validated_data['id'])
# 		except:
# 			return super(EnslaverInRelationCRUDSerializer, self).create(validated_data)
# 
# class EnslavedInRelationCRUDSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
# 	class Meta:
# 		model=EnslavedInRelation
# 		exclude=['relation']
# 	def create(self, validated_data):
# 		try:
# 			return EnslavedInRelation.objects.get(id=validated_data['id'])
# 		except:
# 			return super(EnslavedInRelationCRUDSerializer, self).create(validated_data)
# 	def update(self, instance,validated_data):
# 		try:
# 			return EnslavedInRelation.objects.get(id=validated_data['id'])
# 		except:
# 			return super(EnslavedInRelationCRUDSerializer, self).create(validated_data)
# 
# 
# 
# class CRUDEnslavementRelationSparseDateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
# 	class Meta:
# 		model=VoyageSparseDate
# 		fields='__all__'
# 
# class EnslavementRelationCRUDSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
# 	relation_type=CRUDEnslavementRelationTypeSerializer(many=False,allow_null=True)
# 	place=CRUDPastLocationSerializer(many=False,allow_null=True)
# 	date=CRUDEnslavementRelationSparseDateSerializer(many=False,allow_null=True)
# 	amount=serializers.FloatField(allow_null=True)
# 	relation_enslavers=EnslaverInRelationCRUDSerializer(many=True)
# 	enslaved_in_relation=EnslavedInRelationCRUDSerializer(many=True)
# 	class Meta:
# 		model=EnslavementRelation
# 		fields='__all__'
# 
# 
# 
# class EnslaverCRUDSerializer(WritableNestedModelSerializer):
# 	id=serializers.IntegerField(allow_null=True)
# 	principal_location=CRUDPastLocationSerializer(many=False,allow_null=True)
# 	aliases=CRUDEnslaverAliasSerializer(many=True,allow_null=True)
# 	birth_place=CRUDPastLocationSerializer(many=False,allow_null=True)
# 	death_place=CRUDPastLocationSerializer(many=False,allow_null=True)
# 	principal_alias=serializers.CharField(allow_null=True)
# 	birth_year=serializers.IntegerField(allow_null=True)
# 	birth_month=serializers.IntegerField(allow_null=True)
# 	birth_day=serializers.IntegerField(allow_null=True)
# 	death_year=serializers.IntegerField(allow_null=True)
# 	death_month=serializers.IntegerField(allow_null=True)
# 	death_day=serializers.IntegerField(allow_null=True)
# 	father_name=serializers.CharField(allow_null=True)
# 	father_occupation=serializers.CharField(allow_null=True)
# 	mother_name=serializers.CharField(allow_null=True)
# 	probate_date=serializers.CharField(allow_null=True)
# 	will_value_pounds=serializers.CharField(allow_null=True)
# 	will_value_dollars=serializers.CharField(allow_null=True)
# 	will_court=serializers.CharField(allow_null=True)
# 	notes=serializers.CharField(allow_null=True)
# 	is_natural_person=serializers.BooleanField(allow_null=True)
# 	human_reviewed=serializers.BooleanField(allow_null=True)
# 	legacy_id=serializers.IntegerField(allow_null=True)
# 	class Meta:
# 		model=EnslaverIdentity
# 		fields='__all__'
# 
# class EnslavedCRUDSerializer(WritableNestedModelSerializer):
# 	id=serializers.IntegerField(allow_null=True)
# 	enslaved_id=serializers.IntegerField(allow_null=True)
# 	post_disembark_location=CRUDPastLocationSerializer(many=False,allow_null=True)
# 	captive_fate=CRUDCaptiveFateSerializer(many=False,allow_null=True)
# 	enslaved_relations=CRUDEnslavedInRelationSerializer(many=True,allow_null=True)
# 	captive_status=CRUDCaptiveStatusSerializer(many=False,allow_null=True)
# 	language_group=CRUDLanguageGroupSerializer(many=False,allow_null=True)
# 	enslaved_source_connections=CRUDPastSourceEnslavedConnectionSerializer(many=True,allow_null=True)
# 	last_known_date = CRUDPASTSparseDateSerializer(many=False,allow_null=True)
# 	register_country = CRUDRegisterCountrySerializer(many=False,allow_null=True)
# 	documented_name = serializers.CharField(allow_null=True)
# 	name_first = serializers.CharField(allow_null=True)
# 	name_second = serializers.CharField(allow_null=True)
# 	name_third = serializers.CharField(allow_null=True)
# 	modern_name = serializers.CharField(allow_null=True)
# 	editor_modern_names_certainty = serializers.CharField(allow_null=True)
# 	age = serializers.IntegerField(allow_null=True)
# 	gender = serializers.IntegerField(allow_null=True)
# 	height = serializers.FloatField(allow_null=True)
# 	skin_color = serializers.CharField(allow_null=True)
# 	dataset = serializers.IntegerField(allow_null=True)
# 	notes = serializers.CharField(allow_null=True)
# 	human_reviewed=serializers.BooleanField(allow_null=True)
# 	class Meta:
# 		model=Enslaved
# 		fields='__all__'
