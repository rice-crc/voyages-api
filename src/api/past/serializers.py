from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField,Field
import re
from .models import *
from geo.models import Location
from voyage.models import *
from document.models import Source, ShortRef,SourceEnslavedConnection, SourceEnslaverConnection,SourceVoyageConnection
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from common.static.EnslaverIdentity_options import EnslaverIdentity_options
from common.static.Enslaved_options import Enslaved_options
from common.static.EnslavementRelation_options import EnslavementRelation_options
from common.autocomplete_indices import get_all_model_autocomplete_fields
from past.cross_filter_fields import EnslaverBasicFilterVarNames,EnslavedBasicFilterVarNames

############ SERIALIZERS COMMON TO ENSLAVERS, ENSLAVED, & RELATIONS

class PASTSparseDateSerializer(serializers.ModelSerializer):
	class Meta:
		model=PASTSparseDate
		fields='__all__'
		
class RegisterCountrySerializer(serializers.ModelSerializer):
	class Meta:
		model=RegisterCountry
		fields='__all__'

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

class PastSourceShortRefSerializer(serializers.ModelSerializer):
	class Meta:
		model=ShortRef
		fields=['id','name']


class PastSourceSerializer(serializers.ModelSerializer):
	page_ranges=serializers.ListField(child=serializers.CharField(),allow_null=True,required=False)
	short_ref=PastSourceShortRefSerializer(many=False)
	class Meta:
		model=Source
		fields='__all__'
 
############ VOYAGES

class PastVoyageItinerarySerializer(serializers.ModelSerializer):
# 	imp_port_voyage_begin=PastLocationSerializer(many=False)
	imp_principal_place_of_slave_purchase=PastLocationSerializer(many=False)
	imp_principal_port_slave_dis=PastLocationSerializer(many=False)
# 	imp_principal_region_slave_dis=PastLocationSerializer(many=False)
	imp_principal_region_of_slave_purchase=PastLocationSerializer(many=False)
	int_first_port_dis=PastLocationSerializer(many=False)
	class Meta:
		model=VoyageItinerary
		fields=[
# 			'imp_port_voyage_begin',
			'imp_principal_place_of_slave_purchase',
			'imp_principal_port_slave_dis',
			'imp_principal_region_of_slave_purchase',
# 			'imp_principal_region_slave_dis',
			'int_first_port_dis'
		]


class PastVoyageSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model=Source
		fields='__all__'

class PastVoyageSourceConnectionSerializer(serializers.ModelSerializer):
	source=PastVoyageSourceSerializer(many=False,read_only=True)
	class Meta:
		model=SourceVoyageConnection
		fields='__all__'

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

class PastEnslavedVoyageSerializer(serializers.ModelSerializer):
	voyage_itinerary=PastVoyageItinerarySerializer(many=False)
	voyage_dates=PastVoyageDatesSerializer(many=False)
	voyage_ship=PastVoyageShipSerializer(many=False)
	voyage_outcome=PastVoyageOutcomeSerializer(many=False)
# 	voyage_source_connections=PastVoyageSourceConnectionSerializer(many=True,read_only=True)
	class Meta:
		model=Voyage
		fields=[
			'voyage_id',
			'id',
			'dataset',
			'voyage_itinerary',
			'voyage_dates',
			'voyage_ship',
			'voyage_outcome',
# 			'voyage_source_connections'
		]

class PastEnslaverVoyageSerializer(serializers.ModelSerializer):
	voyage_itinerary=PastVoyageItinerarySerializer(many=False)
	voyage_dates=PastVoyageDatesSerializer(many=False)
	voyage_ship=PastVoyageShipSerializer(many=False)
# 	voyage_outcome=PastVoyageOutcomeSerializer(many=False)
# 	voyage_source_connections=PastVoyageSourceConnectionSerializer(many=True,read_only=True)
	enslaver_roles=EnslaverRoleSerializer(many=True,read_only=True)
	class Meta:
		model=Voyage
		fields=[
			'voyage_id',
			'id',
			'dataset',
			'voyage_itinerary',
			'voyage_dates',
			'voyage_ship',
# 			'voyage_outcome',
# 			'voyage_source_connections',
			'enslaver_roles'
		]



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

class EnslavedEnslaverIdentitySerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverIdentity
		fields='__all__'


class EnslavedEnslaversInRelationListResponseSerializer(serializers.Serializer):
	enslaver=EnslavedEnslaverIdentitySerializer(many=False,read_only=True)
	roles=serializers.CharField()

	
	
class EnslavedSerializer(serializers.ModelSerializer):
	enslaved_id=serializers.IntegerField(read_only=True)
	post_disembark_location=PastLocationSerializer(many=False,read_only=True)
	captive_fate=CaptiveFateSerializer(many=False,read_only=True)
	voyages=serializers.SerializerMethodField()
	enslavers=serializers.SerializerMethodField()
	captive_status=CaptiveStatusSerializer(many=False,read_only=True)
	language_group=LanguageGroupSerializer(many=False,read_only=True)
	sources=serializers.SerializerMethodField()
	def get_sources(self,instance) -> PastSourceSerializer(many=True):
		escs=instance.enslaved_source_connections.all()
		sources_dict={}
		for esc in escs:
			page_range=esc.page_range
			s=esc.source
			s_id=s.id
			s.page_ranges=[page_range]
			if s_id not in sources_dict:
				sources_dict[s_id]=s
			else:
				sources_dict[s_id].page_ranges.append(page_range)
		return PastSourceSerializer([sources_dict[i] for i in sources_dict],many=True,read_only=True).data

	def get_voyages(self,instance) -> PastEnslavedVoyageSerializer(many=True):
		eirs=instance.enslaved_relations.all().exclude(relation__voyage__isnull=True)
		voyages=list(set([eir.relation.voyage for eir in eirs]))
		return PastEnslavedVoyageSerializer(voyages,many=True,read_only=True).data
	def get_enslavers(self,instance) -> EnslavedEnslaversInRelationListResponseSerializer:
		edrs=instance.enslaved_relations.all()
		edrs=edrs.prefetch_related('relation__relation_enslavers__roles','relation__relation_enslavers__enslaver_alias__identity')
		enslaver_roles_and_identity_pks=edrs.values_list('relation__relation_enslavers__roles__id','relation__relation_enslavers__enslaver_alias__identity_id')
		enslavers_and_roles={}
		for eraipk in enslaver_roles_and_identity_pks:
			rolepk,enslaverpk=eraipk
			if rolepk is not None and enslaverpk is not None:
				if enslaverpk not in enslavers_and_roles:
					enslavers_and_roles[enslaverpk]=[rolepk]
				else:
					enslavers_and_roles[enslaverpk].append(rolepk)
		enslavers_and_roles_list=[{'roles':", ".join([EnslaverRole.objects.get(id=rolepk).name for rolepk in enslavers_and_roles[enslaverpk]]),'enslaver':EnslaverIdentity.objects.get(id=enslaverpk)} for enslaverpk in enslavers_and_roles]
		enslavers_in_relation=EnslavedEnslaversInRelationListResponseSerializer(enslavers_and_roles_list,many=True,read_only=True).data		
		return enslavers_in_relation
				

	class Meta:
		model=Enslaved
		fields='__all__'

#######################

#### FROM ENSLAVERS TO ENSLAVED


####################### ENSLAVERS M2M CONNECTIONS

#### FROM ENSLAVERS OUTWARDS

class EnslaverEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=['documented_name','enslaved_id','id']
	
class EnslaverEnslavedInRelationSerializer(serializers.ModelSerializer):
	enslaved=EnslaverEnslavedSerializer(many=False)
	enslaver_roles=EnslaverRoleSerializer(many=True,read_only=True)
	class Meta:
		model=EnslavedInRelation
		fields=('enslaved','enslaver_roles')

class EnslaverAliasSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverAlias
		fields=('alias',)

class EnslaverIdentitySerializer(serializers.ModelSerializer):
	birth_place=PastLocationSerializer(many=False)
	death_place=PastLocationSerializer(many=False)
	aliases=EnslaverAliasSerializer(many=True)
	principal_location=PastLocationSerializer(many=False)
	named_enslaved_people=serializers.SerializerMethodField()
	voyages=serializers.SerializerMethodField()
	sources=serializers.SerializerMethodField()
	def get_sources(self,instance) -> PastSourceSerializer(many=True):
		escs=instance.enslaver_source_connections.all()
		sources_dict={}
		for esc in escs:
			page_range=esc.page_range
			s=esc.source
			s_id=s.id
			s.page_ranges=[page_range]
			if s_id not in sources_dict:
				sources_dict[s_id]=s
			else:
				sources_dict[s_id].page_ranges.append(page_range)
		return PastSourceSerializer([sources_dict[i] for i in sources_dict],many=True,read_only=True).data

	def get_named_enslaved_people(self,instance) -> EnslaverEnslavedInRelationSerializer(many=True):
		aliases=instance.aliases.all()
		eirs=[]
		for alias in aliases:
			alias_eirs=alias.enslaver_relations.all()
			for aeir in alias_eirs:
				eirs.append(aeir)
		eirs=list(set(eirs))
		enslaver_enslaved_dict={}
		for eir in eirs:
			enslaved_people_in_relation=eir.relation.enslaved_in_relation.all()
			for e in enslaved_people_in_relation:
				print("e",e)
				e.enslaver_roles=eir.roles.all()
				enslaver_enslaved_dict[e.id]=e
		return EnslaverEnslavedInRelationSerializer([enslaver_enslaved_dict[e] for e in enslaver_enslaved_dict],many=True,read_only=True).data

	def get_voyages(self,instance) -> PastEnslaverVoyageSerializer(many=True):
		aliases=instance.aliases.all()
		eirs=[]
		for alias in aliases:
			alias_eirs=alias.enslaver_relations.all()
			for aeir in alias_eirs:
				eirs.append(aeir)
		eirs=list(set(eirs))
		
		enslaver_voyages_dict={}
		for eir in eirs:
			voyage=eir.relation.voyage
			if voyage is not None:
				voyage.enslaver_roles=eir.roles.all()
				enslaver_voyages_dict[voyage.id]=voyage

		return PastEnslaverVoyageSerializer([enslaver_voyages_dict[v] for v in enslaver_voyages_dict],many=True,read_only=True).data

	class Meta:
		model=EnslaverIdentity
		fields='__all__'


#################################### THE BELOW SERIALIZERS ARE USED FOR API REQUEST VALIDATION. SOME ARE JUST THIN WRAPPERS ON THE ABOVE, LIKE THAT FOR PAGINATED LISTS. OTHERS ARE ALMOST ENTIRELY HAND-WRITTEN/HARD-CODED FOR OUR CUSTOMIZED ENDPOINTS LIKE GEOTREEFILTER AND AUTOCOMPLETE, AND WILL HAVE TO BE KEPT IN ALIGNMENT WITH THE MODELS, VIEWS, AND CUSTOM FUNCTIONS THEY INTERACT WITH.

class AnyField(Field):
	def to_representation(self, value):
		return value

	def to_internal_value(self, data):
		return data

############ REQUEST FIILTER OBJECTS
class EnslaverBasicFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw","andlist"])
	##It's rather costly for our filter requests like autocomplete and geotree to themselves "cross-filter" on too many nested variables
	##At the same time, some cross-filters are essential to build the menus properly
	varName=serializers.CharField(required=False,allow_null=True)
	searchTerm=AnyField()

class EnslaverFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw","andlist"])
	varName=serializers.CharField(required=False,allow_null=True)
	searchTerm=AnyField()

class EnslavedBasicFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw","andlist"])
	varName=serializers.CharField(required=False,allow_null=True)
	searchTerm=AnyField()

class EnslavedFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw","andlist"])
	varName=serializers.CharField(required=False,allow_null=True)
	searchTerm=AnyField()

class EnslavementRelationFilterItemSerializer(serializers.Serializer):
	op=serializers.ChoiceField(choices=["in","gte","lte","exact","icontains","btw","andlist"])
	varName=serializers.CharField(required=False,allow_null=True)
	searchTerm=AnyField()

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
	filter=EnslavedFilterItemSerializer(many=True,required=False,allow_null=True)
	order_by=serializers.ListField(child=serializers.CharField(allow_null=True),required=False,allow_null=True)
	global_search=serializers.CharField(allow_null=True,required=False)

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
	page=serializers.IntegerField(required=False,allow_null=True)
	page_size=serializers.IntegerField(required=False,allow_null=True)
	filter=EnslaverFilterItemSerializer(many=True,required=False,allow_null=True)
	order_by=serializers.ListField(child=serializers.CharField(allow_null=True),required=False,allow_null=True)
	global_search=serializers.CharField(allow_null=True,required=False)
	
class EnslaverListResponseSerializer(serializers.Serializer):
	page=serializers.IntegerField()
	page_size=serializers.IntegerField()
	count=serializers.IntegerField()
	results=EnslaverIdentitySerializer(many=True,read_only=True)

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
	varName=serializers.CharField(required=False,allow_null=True)
	querystr=serializers.CharField(allow_null=True,allow_blank=True)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=EnslaverBasicFilterItemSerializer(many=True,required=False,allow_null=True)
	global_search=serializers.CharField(allow_null=True,required=False)

class EnslaverAutoCompletekvSerializer(serializers.Serializer):
	value=serializers.CharField()

class EnslaverAutoCompleteResponseSerializer(serializers.Serializer):
	suggested_values=EnslaverAutoCompletekvSerializer(many=True)
	
@extend_schema_serializer(
	examples = [
         OpenApiExample(
			'Paginated autocomplete on enslaved names',
			summary='Paginated filtered autocomplete on enslaved names',
			description='Here, we are requesting the first 5 suggested values, of the recorded names of enslaved people, when those names are like "george", for records entered in the "Intra-American" enslaved dataset(s)',
			value={
				"varName": "documented_name",
				"querystr": "george",
				"offset": 0,
				"limit": 5,
				"filter": [
					{
						"varName":"dataset",
						"op":"exact",
						"searchTerm":0
					}
				]
			},
			request_only=True
		)
    ]
)
class EnslavedAutoCompleteRequestSerializer(serializers.Serializer):
	varName=serializers.CharField(required=False,allow_null=True)
	querystr=serializers.CharField(allow_null=True,allow_blank=True)
	offset=serializers.IntegerField()
	limit=serializers.IntegerField()
	filter=EnslavedBasicFilterItemSerializer(many=True,required=False,allow_null=True)
	global_search=serializers.CharField(allow_null=True,required=False)

class EnslavedAutoCompletekvSerializer(serializers.Serializer):
	value=serializers.CharField()

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
	varName=serializers.CharField(required=False,allow_null=True)


	
class EnslavedFieldAggregationResponseSerializer(serializers.Serializer):
	varName=serializers.CharField(required=False,allow_null=True)

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
	varName=serializers.CharField(required=False,allow_null=True)


	
class EnslaverFieldAggregationResponseSerializer(serializers.Serializer):
	varName=serializers.CharField(required=False,allow_null=True)
	min=serializers.IntegerField(allow_null=True)
	max=serializers.IntegerField(allow_null=True)






############ DATAFRAMES ENDPOINTS
@extend_schema_serializer(
	examples=[
		OpenApiExample(
			'Filtered request for 2 columns',
			summary="Filtered req for 2 cols",
			description="Here, we are looking for the enslaved person\'s documented name, and the region in which they disembarked, for individuals whose names we know who were transported between 1810-15.",
			value={
				"selected_fields":[
					"documented_name",
					"enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name"
				],
				"filter":[
					{
						"varName": "enslaved_relations__relation__voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"op": "btw",
						"searchTerm": [1810,1815]
					}
				]
			}
		)
	]
)
class EnslavedDataframesRequestSerializer(serializers.Serializer):
	selected_fields=serializers.ListField(
		child=serializers.ChoiceField(choices=[
			k for k in Enslaved_options
		])
	)
	filter=EnslavedFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)

@extend_schema_serializer(
	examples=[
		OpenApiExample(
			'Filtered request for 2 columns',
			summary="Filtered req for 2 cols",
			description="Here, we are looking for the name and date of birth for enslavers associated with voyages to Barbados.",
			value={
				"selected_fields":[
					"birth_year",
					"principal_alias"
				],
				"filter":[
					{
						"varName": "aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name",
						"op": "in",
						"searchTerm": ["Barbados"]
					}
				]
			}
		)
	]
)
class EnslaverDataframesRequestSerializer(serializers.Serializer):
	selected_fields=serializers.ListField(
		child=serializers.ChoiceField(choices=[
			k for k in EnslaverIdentity_options
		])
	)
	filter=EnslaverFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)


@extend_schema_serializer(
	examples=[
		OpenApiExample(
			'Filtered request for 3 columns',
			summary="Filtered req for 3 cols",
			description="Here, we are looking for the enslaved person\'s documented name, the ship's name, and the pk of the relation for people who were transported between 1810-15.",
			value={
				"selected_fields":[
					"id",
					"voyage__voyage_ship__ship_name",
					"enslaved_in_relation__enslaved__documented_name"
				],
				"filter":[
					{
						"varName": "voyage__voyage_dates__imp_arrival_at_port_of_dis_sparsedate__year",
						"op": "btw",
						"searchTerm": [1810,1815]
					}
				]
			}
		)
	]
)
class EnslavementRelationDataframesRequestSerializer(serializers.Serializer):
	selected_fields=serializers.ListField(
		child=serializers.ChoiceField(choices=[
			k for k in EnslavementRelation_options
		])
	)
	filter=EnslavementRelationFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)




	
	



############ GEOTREE REQUESTS
@extend_schema_serializer(
	examples=[
		OpenApiExample(
			"Filtered req for enslaved people geo vals",
			summary="Filtered req for enslaved people geo vals",
			description="Here, we are looking for a tree of all the values used for the 'port of departure' variable for named enslaved individuals who were disembarked in Texas.",
			value={
				"geotree_valuefields":["enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__value"],
				"filter":[
					{
						"varName": "enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name",
						"op": "in",
						"searchTerm": ["Texas"]
					}
				]
			}
		)
	]
)
class EnslavedGeoTreeFilterRequestSerializer(serializers.Serializer):
	geotree_valuefields=serializers.ListField(
		child=serializers.ChoiceField(
			choices=[
				k for k in Enslaved_options
				if (("post_disembark_location" in k or "voyage_itinerary" in k) and k.endswith("value"))
			]
		)
	)
	filter=EnslavedBasicFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)
	

############ GEOTREE REQUESTS
@extend_schema_serializer(
	examples=[
		OpenApiExample(
			"Filtered req for enslaver geo vals",
			summary="Filtered req for enslaver geo vals",
			description="Here, we are looking for a tree of all the values used for the 'port of departure' variable (used for tracking the triangular trade) for enslavers who are associated with Intra-American voyages.",
			value={
				"geotree_valuefields":["aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__value"],
				"filter":[
					{
						"varName": "aliases__enslaver_relations__relation__voyage__dataset",
						"op": "exact",
						"searchTerm": 1
					}
				]
			}
		)
	]
)
class EnslaverGeoTreeFilterRequestSerializer(serializers.Serializer):
	geotree_valuefields=serializers.ListField(
		child=serializers.ChoiceField(
			choices=[
				k for k in EnslaverIdentity_options
				if (("voyage_itinerary" in k or "place" in k) and k.endswith("value"))
			]
		)
	)
	filter=EnslaverBasicFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)
	
	
############ PAST AGGREGATION ROUTE MAPS
@extend_schema_serializer(
	examples=[
		OpenApiExample(
			'filtered request for people disembarked in barbados',
			summary="Filtered request for people disembarked in Barbados",
			description="Here we request the routes taken by enslaved individuals whose names we know who disembarked in Barbados (in this case, only one individual, Broteer Furro).",
			value={
				"zoomlevel": "region",
				"filter":[
					{
						"varName":"enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__name",
						"op":"in",
						"searchTerm":["Barbados, place unspecified"]
					}
				]
			}
		)
	]

)
class EnslavedAggRoutesRequestSerializer(serializers.Serializer):
	zoomlevel=serializers.ChoiceField(choices=(('region','region'),('place','place')))
	filter=EnslavedFilterItemSerializer(many=True,allow_null=True,required=False)
	global_search=serializers.CharField(allow_null=True,required=False)

class EnslavedAggRoutesEdgesSerializer(serializers.Serializer):
	source=serializers.CharField()
	target=serializers.CharField()
	type=serializers.CharField()
	weight=serializers.IntegerField()
	controls=serializers.ListField(child=serializers.ListField(child=serializers.FloatField(allow_null=False)))

class EnslavedAggRoutesNodesDataSerializer(serializers.Serializer):
	lat=serializers.FloatField(allow_null=False)
	lon=serializers.FloatField(allow_null=False)
	name=serializers.CharField(allow_null=True)
	tags=serializers.ListField(child=serializers.CharField(),allow_null=True,required=False)

class EnslavedAggRoutesNodesWeightsSerializer(serializers.Serializer):
	disembarkation=serializers.IntegerField()
	embarkation=serializers.IntegerField()
	origin=serializers.IntegerField()
	post_disembarkation=serializers.IntegerField()

class EnslavedAggRoutesNodesSerializer(serializers.Serializer):
	id=serializers.CharField()
	weights=EnslavedAggRoutesNodesWeightsSerializer()
	data=EnslavedAggRoutesNodesDataSerializer()
	
class EnslavedAggRoutesResponseSerializer(serializers.Serializer):
	edges=serializers.ListField(child=EnslavedAggRoutesEdgesSerializer())
	nodes=serializers.ListField(child=EnslavedAggRoutesNodesSerializer())

############### NETWORK GRAPHS

@extend_schema_serializer(
	examples=[
		OpenApiExample(
			"Connections to Robert N. Henderson",
			summary="Connections to Robert N. Henderson",
			description="Here we request the connections to enslaver #55232, Robert N. Henderson.",
			value={
				"enslavers": [55232]
			}
		)
	]
)
class PASTNetworksRequestSerializer(serializers.Serializer):
	enslaved=serializers.ListField(
		child=serializers.IntegerField(), required=False
	)
	enslavers=serializers.ListField(
		child=serializers.IntegerField(), required=False
	)
	voyages=serializers.ListField(
		child=serializers.IntegerField(), required=False
	)
	enslavement_relations=serializers.ListField(
		child=serializers.IntegerField(), required=False
	)

class PASTNetworksResponseNodeSerializer(serializers.Serializer):
	id=serializers.IntegerField()
	node_class=serializers.CharField()
	uuid=serializers.CharField()
	data=serializers.JSONField()

class PASTNetworksResponseEdgeSerializer(serializers.Serializer):
	source=serializers.CharField()
	target=serializers.CharField()
	data=serializers.JSONField()
	
class PASTNetworksResponseSerializer(serializers.Serializer):
	nodes=PASTNetworksResponseNodeSerializer(many=True)
	edges=PASTNetworksResponseEdgeSerializer(many=True)
