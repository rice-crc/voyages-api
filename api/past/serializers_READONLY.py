from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from geo.models import Location
from voyage.models import *
from document.models import Source, SourceEnslavedConnection, SourceEnslaverConnection
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from common.static.Enslaver_options import Enslaver_options
from common.static.Enslaved_options import Enslaved_options
		
class PASTSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=PASTSparseDate
		fields='__all__'
		
class RegisterCountrySerializer(serializers.ModelSerializer):
	class Meta:
		model=RegisterCountry
		fields='__all__'


############ SERIALIZERS COMMON TO BOTH ENSLAVERS AND ENSLAVED

class EnslaverRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'


class EnslavementRelationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class PastLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model=Location
		fields='__all__'

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
	voyage_outcome=PastVoyageOutcomeSerializer(many=False)
	class Meta:
		model=Voyage
		fields=[
			'voyage_id',
			'id',
			'dataset',
			'voyage_itinerary',
			'voyage_dates',
			'voyage_ship',
			'voyage_outcome'
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
	roles=EnslaverRoleSerializer(many=True)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslavedEnslavementRelationSerializer(serializers.ModelSerializer):
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

class CaptiveFateSerializer(serializers.ModelSerializer):
	
	class Meta:
		model=CaptiveFate
		fields='__all__'



class CaptiveStatusSerializer(serializers.ModelSerializer):

	class Meta:
		model=CaptiveStatus
		fields='__all__'

class LanguageGroupSerializer(serializers.ModelSerializer):
	class Meta:
		model=LanguageGroup
		fields='__all__'

class RegisterCountrySerializer(serializers.ModelSerializer):
	class Meta:
		model=RegisterCountry
		fields='__all__'

class EnslavedInRelationSerializer(serializers.ModelSerializer):
	relation=EnslavedEnslavementRelationSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslavedSerializer(serializers.ModelSerializer):
	post_disembark_location=PastLocationSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	enslaved_relations=EnslavedInRelationSerializer(many=True)
	captive_status=CaptiveStatusSerializer(many=False)
	language_group=LanguageGroupSerializer(many=False)
	enslaved_source_connections=PastSourceEnslavedConnectionSerializer(many=True)
	class Meta:
		model=Enslaved
		fields='__all__'

class EnslavedPKSerializer(serializers.ModelSerializer):
	post_disembark_location=PastLocationSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	enslaved_relations=EnslavedInRelationSerializer(many=True)
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
		fields=['documented_name','enslaved_id','id']
	
class EnslaverEnslavedInRelationSerializer(serializers.ModelSerializer):
	enslaved=EnslaverEnslavedSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslaverEnslavementRelationSerializer(serializers.ModelSerializer):
	enslaved_in_relation=EnslaverEnslavedInRelationSerializer(many=True)
	relation_type=EnslavementRelationTypeSerializer(many=False)
	place=PastLocationSerializer(many=False)
	voyage=PastVoyageSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslaverInRelationSerializer(serializers.ModelSerializer):
	relation = EnslaverEnslavementRelationSerializer(many=False)
	roles=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslaverIdentitySerializer(serializers.ModelSerializer):
	birth_place=PastLocationSerializer(many=False,read_only=True)
	death_place=PastLocationSerializer(many=False,read_only=True)
	principal_location=PastLocationSerializer(many=False,read_only=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslaverAliasSerializer(serializers.ModelSerializer):
	enslaver_relations=EnslaverInRelationSerializer(many=True)
	identity=EnslaverIdentitySerializer(many=False)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslaverSerializer(serializers.ModelSerializer):
	principal_location=PastLocationSerializer(many=False)
	enslaver_source_connections=PastSourceEnslaverConnectionSerializer(many=True)
	aliases=EnslaverAliasSerializer(many=True)
	birth_place=PastLocationSerializer(many=False)
	death_place=PastLocationSerializer(many=False)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'
		

class EnslaverPKSerializer(serializers.ModelSerializer):
	principal_location=PastLocationSerializer(many=False)
	enslaver_source_connections=PastSourceEnslaverConnectionSerializer(many=True)
	aliases=EnslaverAliasSerializer(many=True)
	birth_place=PastLocationSerializer(many=False)
	death_place=PastLocationSerializer(many=False)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'



class EnslavementRelationSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=VoyageSparseDate
		fields='__all__'

class EnslavementRelationPKSerializer(serializers.ModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False,allow_null=True)
	place=PastLocationSerializer(many=False,allow_null=True)
	date=EnslavementRelationSparseDateSerializer(many=False,allow_null=True)
	relation_enslavers=EnslaverInRelationSerializer(many=True)
	enslaved_in_relation=EnslavedInRelationSerializer(many=True)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

#################################### THE BELOW SERIALIZERS ARE USED FOR API REQUEST VALIDATION. SOME ARE JUST THIN WRAPPERS ON THE ABOVE, LIKE THAT FOR THE PAGINATED VOYAGE LIST ENDPOINT. OTHERS ARE ALMOST ENTIRELY HAND-WRITTEN/HARD-CODED FOR OUR CUSTOMIZED ENDPOINTS LIKE GEOTREEFILTER AND AUTOCOMPLETE, AND WILL HAVE TO BE KEPT IN ALIGNMENT WITH THE MODELS, VIEWS, AND CUSTOM FUNCTIONS THEY INTERACT WITH.



############ REQUEST FIILTER OBJECTS
class EnslaverFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["gte","lte","exact","icontains","in","btw"])
	varName=serializers.ChoiceField(choices=[k for k in Enslaver_options])
	searchTerm=serializers.ReadOnlyField(read_only=True)

class EnslavedFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["gte","lte","exact","icontains","in","btw"])
	varName=serializers.ChoiceField(choices=[k for k in Enslaved_options])
	searchTerm=serializers.ReadOnlyField(read_only=True)

########### PAGINATED ENSLAVED LISTS 
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated, filtered list of enslaved people',
			summary='Paginated, filtered list of enslaved people',
			description='Here, we request page 2 (with 5 items per page) of enslaved people who were recorded as between 5-15 years of age when their information was recorded.',
			value={
			  "filter": [
					{
						"varName":"age",
						"searchTerm":[5,15],
						"op":"btw"
					}
				],
				"page": 2,
				"page_size": 5
			},
			request_only=True
		)
    ]
)
class EnslavedListRequestSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	filter=EnslavedFilterItemSerializer(many=True)

class EnslavedListResponseSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	count=serializers.IntegerField()
	results=EnslavedSerializer(many=True,read_only=True)

########### PAGINATED ENSLAVER LISTS 
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated, filtered list of enslavers',
			summary='Paginated request for filtered voyages.',
			description='Here, we request page 2 (with 5 items per page) of enslavers who are associated with voyages that disembarked captives between 1820-1830 in Cuba.',
			value={
			  "filter": [
					{
						"varName":"aliases__enslaver_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"searchTerm":[1820,1830],
						"op":"btw"
					},
					{
						"varName":"aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name",
						"searchTerm":["Cuba"],
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
class EnslaverListRequestSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	filter=EnslaverFilterItemSerializer(many=True)

class EnslaverListResponseSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	count=serializers.IntegerField()
	results=EnslaverSerializer(many=True,read_only=True)

############ AUTOCOMPLETE SERIALIZERS
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated autocomplete on enslaver aliases',
			summary='Paginated autocomplete on enslaver aliases',
			description='Here, we are requesting 5 suggested values, starting with the 10th item, of enslaver aliases (names) like "george" associated with voyages that disembarked captives between the years 1820-40.',
			value={
				"varName": "aliases__alias",
				"querystr": "george",
				"offset": 10,
				"limit": 5,
				"filter": [
					{
						"varName": "aliases__enslaver_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"op": "btw",
						"searchTerm": [1820,1840]
					}
				]
			},
			request_only=True
		)
    ]
)
class EnslaverAutoCompleteRequestSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[
		k for k in Enslaver_options if Enslaver_options[k]['type'] in [
			'string'
		]
	])
	querystr=serializers.CharField(max_length=255,allow_null=True)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=EnslaverFilterItemSerializer(many=True,allow_null=True)

class EnslaverAutoCompletekvSerializer(serializers.Serializer):
	value=serializers.CharField(max_length=255)

class EnslaverAutoCompleteResponseSerializer(serializers.Serializer):
	suggested_values=EnslaverAutoCompletekvSerializer(many=True)
	
	
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated autocomplete on enslaved names',
			summary='Paginated filtered autocomplete on enslaved names',
			description='Here, we are requesting the first 5 suggested values, of the recorded names of enslaved people, when those names are like "george", for people we know to have been transported from Baltimore.',
			value={
				"varName": "documented_name",
				"querystr": "george",
				"offset": 0,
				"limit": 5,
				"filter": [
					{
						"varName":"enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__name",
						"op":"in",
						"searchTerm":["Baltimore"]
					}
				]
			},
			request_only=True
		)
    ]
)
class EnslavedAutoCompleteRequestSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[
		k for k in Enslaved_options if Enslaved_options[k]['type'] in [
			'string'
		]
	])
	querystr=serializers.CharField(max_length=255,allow_null=True)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=EnslavedFilterItemSerializer(many=True,allow_null=True)

class EnslavedAutoCompletekvSerializer(serializers.Serializer):
	value=serializers.CharField(max_length=255)

class EnslavedAutoCompleteResponseSerializer(serializers.Serializer):
	suggested_values=EnslavedAutoCompletekvSerializer(many=True)



############ AGGREGATION ON FIELDS
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Filtered request for min/max',
			summary='Filtered request for min/max',
			description='Here, we request the min and max year on which enslaved individuals whose names we know disembarked from a voyage.',
			value={
				"varName": "enslaved_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
				"filter": [
				]
			},
			request_only=True
		)
    ]
)
class EnslavedFieldAggregationRequestSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[
		k for k in Enslaved_options if Enslaved_options[k]['type'] in [
			'integer',
			'number'
		]
	])

	
class EnslavedFieldAggregationResponseSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[
		k for k in Enslaved_options if Enslaved_options[k]['type'] in [
			'integer',
			'number'
		]
	])
	min=serializers.IntegerField(allow_null=True)
	max=serializers.IntegerField(allow_null=True)
	
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Filtered request for min/max',
			summary='Filtered request for min/max',
			description='Here, we request the min and max year on which voyages that we have named enslavers listed for',
			value={
				"varName": "aliases__enslaver_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
				"filter": [
				]
			},
			request_only=True
		)
    ]
)
class EnslaverFieldAggregationRequestSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[
		k for k in Enslaver_options if Enslaver_options[k]['type'] in [
			'integer',
			'number'
		]
	])

	
class EnslaverFieldAggregationResponseSerializer(serializers.Serializer):
	varName=serializers.ChoiceField(choices=[
		k for k in Enslaver_options if Enslaver_options[k]['type'] in [
			'integer',
			'number'
		]
	])
	min=serializers.IntegerField(allow_null=True)
	max=serializers.IntegerField(allow_null=True)