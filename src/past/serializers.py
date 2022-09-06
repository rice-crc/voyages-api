from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from voyage.serializers import *
			
class CaptiveFateSerializer(serializers.ModelSerializer):
	class Meta:
		model=CaptiveFate
		fields='__all__'

class CaptiveStatusSerializer(serializers.ModelSerializer):
	class Meta:
		model=CaptiveStatus
		fields='__all__'

class EnslaverIdentitySourceConnectionSerializer(serializers.ModelSerializer):
	source=VoyageSourcesSerializer(many=False)
	class Meta:
		model=EnslaverIdentitySourceConnection
		fields='__all__'

class EnslaverRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class EnslavementRelationTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class EnslaverEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=['id','documented_name']

class EnslaverEnslavedInRelationSerializer(serializers.ModelSerializer):
	enslaved=EnslaverEnslavedSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslaverEnslavementRelationSerializer(serializers.ModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	source=VoyageSourcesSerializer(many=False)
	place=PlaceSerializer(many=False)
	enslaved_person=EnslaverEnslavedInRelationSerializer(many=True,read_only=True)
	class Meta:
		model=EnslavementRelation
		fields=['relation_type','source','voyage','place','enslaved_person','amount']

class EnslaverInRelationSerializer(serializers.ModelSerializer):
	transaction=EnslaverEnslavementRelationSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'


class EnslavedEnslaverSerializer(serializers.ModelSerializer):
	principal_location=PlaceSerializer(many=False)
	enslaver_sources=EnslaverIdentitySourceConnectionSerializer(many=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslavedEnslaverAliasSerializer(serializers.ModelSerializer):
	identity=EnslavedEnslaverSerializer(many=False)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslavedEnslaverInRelationSerializer(serializers.ModelSerializer):
	enslaver_alias=EnslavedEnslaverAliasSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslavedEnslavedInRelationEnslavedSerializer(serializers.ModelSerializer):
	class Meta:
		model=Enslaved
		fields=('documented_name','id')

class EnslavedEnslavedInRelationSerializer(serializers.ModelSerializer):
	enslaved=EnslavedEnslavedInRelationEnslavedSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslavedEnslavementRelationSerializer(serializers.ModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	enslavers=EnslavedEnslaverInRelationSerializer(many=True,read_only=False)
	enslaved_person=EnslavedEnslavedInRelationSerializer(many=True,read_only=False)
	source=VoyageSourcesSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	place=PlaceSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslavedInRelationSerializer(serializers.ModelSerializer):
	transaction=EnslavedEnslavementRelationSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslavedSourceConnectionSerializer(serializers.ModelSerializer):
	source=VoyageSourcesSerializer(many=False)
	class Meta:
		model=EnslavedSourceConnection
		fields='__all__'

class EnslaverVoyageConnectionSerializer(serializers.ModelSerializer):
	voyage=VoyageSerializer(many=True,read_only=True)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverVoyageConnection
		fields='__all__'

class EnslavedSerializer(serializers.ModelSerializer):
	post_disembark_location=PlaceSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	sources_conn=EnslavedSourceConnectionSerializer(many=True,read_only=True)
	transactions=EnslavedInRelationSerializer(many=True,read_only=True)
	captive_status=CaptiveStatusSerializer(many=False)
	class Meta:
		model=Enslaved
		fields='__all__'

class EnslaverAliasSerializer(serializers.ModelSerializer):
	transactions=EnslaverInRelationSerializer(many=True,read_only=True)
	enslaver_voyage=EnslaverVoyageConnectionSerializer(many=True,read_only=True)
	class Meta:
		model=EnslaverAlias
		#including the 'identity' field here breaks it, so i'm excluding
		fields=['transactions','id','alias','enslaver_voyage']


class EnslaverSerializer(serializers.ModelSerializer):
	principal_location=PlaceSerializer(many=False)
	alias=EnslaverAliasSerializer(many=True,read_only=True)
	enslaver_sources=EnslaverIdentitySourceConnectionSerializer(many=True,read_only=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'
		




