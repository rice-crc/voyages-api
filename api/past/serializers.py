from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from geo.models import Location
from voyage.models import *
from document.models import Source, SourceEnslavedConnection, SourceEnslaverConnection
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.core.exceptions import ObjectDoesNotExist
from drf_writable_nested.serializers import WritableNestedModelSerializer
from drf_writable_nested.mixins import UniqueFieldsMixin


class PASTSparseDateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=PASTSparseDate
		fields='__all__'
		
class RegisterCountrySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=RegisterCountry
		fields='__all__'
	def create(self, validated_data):
		try:
			return RegisterCountry.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(RegisterCountrySerializer, self).create(validated_data)


############ SERIALIZERS COMMON TO BOTH ENSLAVERS AND ENSLAVED

class EnslaverRoleSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	name=serializers.CharField(allow_null=False)
	class Meta:
		model=EnslaverRole
		fields='__all__'
	def create(self, validated_data):
		try:
			return EnslaverRole.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(EnslaverRoleSerializer, self).create(validated_data)


class EnslavementRelationTypeSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'
	def create(self, validated_data):
		try:
			return EnslavementRelationType.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(EnslavementRelationTypeSerializer, self).create(validated_data)

class PastLocationSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'
	def create(self, validated_data):
		try:
			return Location.objects.get(value=validated_data['value'])
		except ObjectDoesNotExist:
			return super(PastLocationSerializer, self).create(validated_data)

class PastSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Source
		fields='__all__'
 
############ VOYAGES

class PastVoyageItinerarySerializer(serializers.ModelSerializer):
	imp_port_voyage_begin=PastLocationSerializer(many=False)
	imp_principal_place_of_slave_purchase=PastLocationSerializer(many=False)
	imp_principal_port_slave_dis=PastLocationSerializer(many=False)
	imp_principal_region_slave_dis=PastLocationSerializer(many=False)
	imp_principal_region_of_slave_purchase=PastLocationSerializer(many=False)
	int_first_port_dis=PastLocationSerializer(many=False)
	class Meta:
		model=VoyageItinerary
		fields=[
			'imp_port_voyage_begin',
			'imp_principal_place_of_slave_purchase',
			'imp_principal_port_slave_dis',
			'imp_principal_region_of_slave_purchase',
			'imp_principal_region_slave_dis',
			'int_first_port_dis'
		]
	
class PastVoyageDatesSerializer(serializers.ModelSerializer):
	imp_arrival_at_port_of_dis_sparsedate=PASTSparseDateSerializer(many=False)
	class Meta:
		model=VoyageDates
		fields=['imp_arrival_at_port_of_dis_sparsedate',]

class PastVoyageShipSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageShip
		fields=['ship_name',]

class PastVoyageParticularOutcomeSerializer(serializers.ModelSerializer):
	class Meta:
		model=ParticularOutcome
		fields='__all__'

class PastVoyageOutcomeSerializer(serializers.ModelSerializer):
	particular_outcome=PastVoyageParticularOutcomeSerializer(many=False)
	class Meta:
		model=VoyageOutcome
		fields=['particular_outcome']

class PastVoyageSerializer(serializers.ModelSerializer):
	voyage_itinerary=PastVoyageItinerarySerializer(many=False)
	voyage_dates=PastVoyageDatesSerializer(many=False)
	voyage_ship=PastVoyageShipSerializer(many=False)
	voyage_name_outcome=PastVoyageOutcomeSerializer(many=True)
	class Meta:
		model=Voyage
		fields=[
			'voyage_id',
			'id',
			'dataset',
			'voyage_itinerary',
			'voyage_dates',
			'voyage_ship',
			'voyage_name_outcome'
		]

####################### ENSLAVED M2M CONNECTIONS

#### FROM ENSLAVED TO ENSLAVERS
class EnslavedEnslaverIdentitySerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslavedEnslaverAliasSerializer(serializers.ModelSerializer):
	identity=EnslavedEnslaverIdentitySerializer(many=False)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslavedEnslaverInRelationSerializer(serializers.ModelSerializer):
	enslaver_alias=EnslavedEnslaverAliasSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslavedEnslavementRelationSerializer(WritableNestedModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	relation_enslavers=EnslavedEnslaverInRelationSerializer(many=True)
	voyage=PastVoyageSerializer(many=False)
	place=PastLocationSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

#### FROM ENSLAVED TO SOURCES
class PastSourceEnslavedConnectionSerializer(serializers.ModelSerializer):
	source=PastSourceSerializer(many=False)
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'

#######################

#### ENSLAVED & ONE-TO-ONE RELATIONS

class CaptiveFateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	
	class Meta:
		model=CaptiveFate
		fields='__all__'
	def create(self, validated_data):
		try:
			return CaptiveFate.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CaptiveFateSerializer, self).create(validated_data)



class CaptiveStatusSerializer(UniqueFieldsMixin, serializers.ModelSerializer):

	class Meta:
		model=CaptiveStatus
		fields='__all__'
	def create(self, validated_data):
		try:
			return CaptiveStatus.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(CaptiveStatusSerializer, self).create(validated_data)

class LanguageGroupSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	longitude=serializers.DecimalField(max_digits=10,decimal_places=7,allow_null=True)
	latitude=serializers.DecimalField(max_digits=10,decimal_places=7,allow_null=True)
	class Meta:
		model=LanguageGroup
		fields='__all__'
	def create(self, validated_data):
		try:
			return LanguageGroup.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(LanguageGroupSerializer, self).create(validated_data)

class RegisterCountrySerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=RegisterCountry
		fields='__all__'
	def create(self, validated_data):
		try:
			return RegisterCountry.objects.get(name=validated_data['name'])
		except ObjectDoesNotExist:
			return super(RegisterCountrySerializer, self).create(validated_data)




@extend_schema_serializer(
	examples = [
		 OpenApiExample(
			'Ex. 1: numeric range',
			summary='Filter on a numeric range',
			description='Here, we search for named enslaved individualas who were, at the time of the transportation that we have recorded for them, between 5 and 15 years of age.',
			value={
				"age":
				[
					5,15
				]
			},
			request_only=True,
			response_only=False
		),
		OpenApiExample(
			'Ex. 2: array of str vals',
			summary='OR Filter on exact matches of known str values',
			description='Here, we search on str value fields for known exact matches to ANY of those values. Specifically, we are searching on a highly nested value: all named enslaved individuals who were on voyages that were principally disembarked in the Bahamas',
			value={
				"enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__geo_location__name":
				[
					"Bahamas, port unspecified"
				]
			},
			request_only=True,
			response_only=False
		)
	]
)
class EnslavedSerializer(serializers.ModelSerializer):
	post_disembark_location=PastLocationSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	enslaved_relations=EnslavedEnslavementRelationSerializer(many=True)
	captive_status=CaptiveStatusSerializer(many=False)
	language_group=LanguageGroupSerializer(many=False)
	enslaved_source_connections=PastSourceEnslavedConnectionSerializer(many=True)
	class Meta:
		model=Enslaved
		fields='__all__'


#######################

#### FROM ENSLAVERS TO ENSLAVED

class PastSourceEnslaverConnectionSerializer(serializers.ModelSerializer):
	source=PastSourceSerializer(many=False)
	class Meta:
		model=SourceEnslaverConnection
		fields='__all__'


####################### ENSLAVED M2M CONNECTIONS

#### FROM ENSLAVERS TO ENSLAVED

class EnslaverEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=['id','documented_name']

class EnslaverEnslavementRelationSerializer(serializers.ModelSerializer):
	enslaved_in_relation=EnslaverEnslavedSerializer(many=True)
	relation_type=EnslavementRelationTypeSerializer(many=False)
	place=PastLocationSerializer(many=False)
	voyage=PastVoyageSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslaverInRelationSerializer(serializers.ModelSerializer):
	relation = EnslaverEnslavementRelationSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslaverAliasSerializer(WritableNestedModelSerializer):
	id=serializers.IntegerField(allow_null=False)
	enslaver_relations=EnslaverInRelationSerializer(many=True,allow_null=True)
	alias=serializers.CharField(allow_null=False)
	manual_id=serializers.CharField(allow_null=True)
	human_reviewed=serializers.BooleanField(allow_null=True)
	legacy_id=serializers.IntegerField(allow_null=True)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

#### FROM ENSLAVERS TO SOURCES
class PastSourceEnslaverConnectionSerializer(serializers.ModelSerializer):
	source=PastSourceSerializer(many=False)
	class Meta:
		model=SourceEnslavedConnection
		fields='__all__'

	



@extend_schema_serializer(
	examples = [
		 OpenApiExample(
			'Ex. 1: numeric range',
			summary='Filter on a numeric range',
			description='Here, we search for enslavers who participated in slave-trading voyages between the years of 1720-1722',
			value={
				"aliases__enslaver_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year":[1720,1722]
			},
			request_only=True,
			response_only=False
		),
		OpenApiExample(
			'Ex. 2: array of str vals',
			summary='OR Filter on exact matches of known str values',
			description='Here, we search for enslavers who participated in the enslavement of anyone named Bora',
			value={
				"aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__documented_name":["Bora"]
			},
			request_only=True,
			response_only=False
		)
	]
)
class EnslaverSerializer(serializers.ModelSerializer):
	principal_location=PastLocationSerializer(many=False)
	enslaver_source_connections=PastSourceEnslaverConnectionSerializer(many=True)
	aliases=EnslaverAliasSerializer(many=True)
	birth_place=PastLocationSerializer(many=False)
	death_place=PastLocationSerializer(many=False)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'


class EnslaverInRelationCRUDSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
	roles=EnslaverRoleSerializer(many=True,allow_null=False)
	class Meta:
		model=EnslaverInRelation
		exclude=['relation']
	def create(self, validated_data):
		try:
			return EnslaverInRelation.objects.get(id=validated_data['id'])
		except:
			return super(EnslaverInRelationCRUDSerializer, self).create(validated_data)
	def update(self, instance,validated_data):
		try:
			return EnslaverInRelation.objects.get(id=validated_data['id'])
		except:
			return super(EnslaverInRelationCRUDSerializer, self).create(validated_data)

class EnslavementRelationSparseDateSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
	class Meta:
		model=VoyageSparseDate
		fields='__all__'

class EnslavementRelationCRUDSerializer(UniqueFieldsMixin,WritableNestedModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False,allow_null=True)
	place=PastLocationSerializer(many=False,allow_null=True)
	date=EnslavementRelationSparseDateSerializer(many=False,allow_null=True)
	amount=serializers.DecimalField(decimal_places=2, max_digits=6,allow_null=True)
	relation_enslavers=EnslaverInRelationCRUDSerializer(many=True)
	enslaved_in_relation=serializers.PrimaryKeyRelatedField(
		many=True,
		queryset=Enslaved.objects.all(),
		allow_null=True,
		default=[]
	)
	class Meta:
		model=EnslavementRelation
		fields='__all__'



class EnslaverCRUDSerializer(WritableNestedModelSerializer):
	id=serializers.IntegerField(allow_null=True)
	principal_location=PastLocationSerializer(many=False,allow_null=True)
	aliases=EnslaverAliasSerializer(many=True,allow_null=True)
	birth_place=PastLocationSerializer(many=False,allow_null=True)
	death_place=PastLocationSerializer(many=False,allow_null=True)
	principal_alias=serializers.CharField(allow_null=True)
	birth_year=serializers.IntegerField(allow_null=True)
	birth_month=serializers.IntegerField(allow_null=True)
	birth_day=serializers.IntegerField(allow_null=True)
	death_year=serializers.IntegerField(allow_null=True)
	death_month=serializers.IntegerField(allow_null=True)
	death_day=serializers.IntegerField(allow_null=True)
	father_name=serializers.CharField(allow_null=True)
	father_occupation=serializers.CharField(allow_null=True)
	mother_name=serializers.CharField(allow_null=True)
	probate_date=serializers.CharField(allow_null=True)
	will_value_pounds=serializers.CharField(allow_null=True)
	will_value_dollars=serializers.CharField(allow_null=True)
	will_court=serializers.CharField(allow_null=True)
	notes=serializers.CharField(allow_null=True)
	is_natural_person=serializers.BooleanField(allow_null=True)
	human_reviewed=serializers.BooleanField(allow_null=True)
	legacy_id=serializers.IntegerField(allow_null=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslavedCRUDSerializer(WritableNestedModelSerializer):
	id=serializers.IntegerField(allow_null=True)
	enslaved_id=serializers.IntegerField(allow_null=True)
	post_disembark_location=PastLocationSerializer(many=False,allow_null=True)
	captive_fate=CaptiveFateSerializer(many=False,allow_null=True)
	enslaved_relations=EnslavedEnslavementRelationSerializer(many=True,allow_null=True)
	captive_status=CaptiveStatusSerializer(many=False,allow_null=True)
	language_group=LanguageGroupSerializer(many=False,allow_null=True)
	enslaved_source_connections=PastSourceEnslavedConnectionSerializer(many=True,allow_null=True)
	last_known_date = PASTSparseDateSerializer(many=False,allow_null=True)
	register_country = RegisterCountrySerializer(many=False,allow_null=True)
	documented_name = serializers.CharField(allow_null=True)
	name_first = serializers.CharField(allow_null=True)
	name_second = serializers.CharField(allow_null=True)
	name_third = serializers.CharField(allow_null=True)
	modern_name = serializers.CharField(allow_null=True)
	editor_modern_names_certainty = serializers.CharField(allow_null=True)
	age = serializers.IntegerField(allow_null=True)
	gender = serializers.IntegerField(allow_null=True)
	height = serializers.DecimalField(decimal_places=2, max_digits=6,allow_null=True)
	skin_color = serializers.CharField(allow_null=True)
	dataset = serializers.IntegerField(allow_null=True)
	notes = serializers.CharField(allow_null=True)
	human_reviewed=serializers.BooleanField(allow_null=True)
	class Meta:
		model=Enslaved
		fields='__all__'
