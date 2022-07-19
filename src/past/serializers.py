from rest_framework import serializers
from rest_framework.fields import SerializerMethodField,IntegerField,CharField
import re
from .models import *
from voyage.serializers import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
	def __init__(self, *args, **kwargs):
		selected_fields = kwargs.pop('selected_fields', None)
		super().__init__(*args, **kwargs)
		pp = pprint.PrettyPrinter(indent=4)
		if selected_fields is not None:
			def nestthis(keychain,thisdict={}):
				while keychain:
					k=keychain.pop(0)
					kvs=k.split('__')
					if len(kvs)==2:
						i,v=kvs
						if i in thisdict:
							thisdict[i][v]={}
						else:
							thisdict[i]={v:{}}
					
					elif len(kvs)==1:
						thisdict[kvs[0]]={}
					else:
						i=kvs[0]
						j=['__'.join(kvs[1:])]
						if i in thisdict:
							thisdict[i]=nestthis(j,thisdict[i])
						else:
							thisdict[i]=nestthis(j,{})
				return thisdict
			
			selected_fields_dict=nestthis(selected_fields)
			print("--selected fields--")
			pp.pprint(selected_fields_dict)
			self=nest_selected_fields(self,selected_fields_dict)

class EnslaverIdentitySourceConnectionSerializer(DynamicFieldsModelSerializer):
	source=VoyageSourcesSerializer(many=False)
	class Meta:
		model=EnslaverIdentitySourceConnection
		fields='__all__'

class EnslaverRoleSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=EnslaverRole
		fields='__all__'

class EnslavementRelationTypeSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=EnslavementRelationType
		fields='__all__'

class EnslaverEnslavementRelationSerializer(DynamicFieldsModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	source=VoyageSourcesSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	place=PlaceSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslaverInRelationSerializer(DynamicFieldsModelSerializer):
	transaction=EnslaverEnslavementRelationSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslaverAliasSerializer(DynamicFieldsModelSerializer):
	transactions=EnslaverInRelationSerializer(many=True,read_only=True)
	class Meta:
		model=EnslaverAlias
		#including the 'identity' field here breaks it, so i'm excluding
		fields=['transactions','id','alias']

class EnslavedEnslaverSerializer(DynamicFieldsModelSerializer):
	principal_location=PlaceSerializer(many=False)
	enslaver_sources=EnslaverIdentitySourceConnectionSerializer(many=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'

class EnslavedEnslaverAliasSerializer(DynamicFieldsModelSerializer):
	identity=EnslavedEnslaverSerializer(many=False)
	class Meta:
		model=EnslaverAlias
		fields='__all__'

class EnslavedEnslaverInRelationSerializer(DynamicFieldsModelSerializer):
	enslaver_alias=EnslavedEnslaverAliasSerializer(many=False)
	role=EnslaverRoleSerializer(many=False)
	class Meta:
		model=EnslaverInRelation
		fields='__all__'

class EnslavedEnslavementRelationSerializer(DynamicFieldsModelSerializer):
	relation_type=EnslavementRelationTypeSerializer(many=False)
	enslavers=EnslavedEnslaverInRelationSerializer(many=True,read_only=False)
	source=VoyageSourcesSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	place=PlaceSerializer(many=False)
	class Meta:
		model=EnslavementRelation
		fields='__all__'

class EnslavedInRelationSerializer(DynamicFieldsModelSerializer):
	transaction=EnslavedEnslavementRelationSerializer(many=False)
	class Meta:
		model=EnslavedInRelation
		fields='__all__'

class EnslavedSourceConnectionSerializer(DynamicFieldsModelSerializer):
	source=VoyageSourcesSerializer(many=False)
	class Meta:
		model=EnslavedSourceConnection
		fields='__all__'

class CaptiveFateSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=CaptiveFate
		fields='__all__'

class CaptiveStatusSerializer(DynamicFieldsModelSerializer):
	class Meta:
		model=CaptiveStatus
		fields='__all__'

class EnslavedSerializer(DynamicFieldsModelSerializer):
	post_disembark_location=PlaceSerializer(many=False)
	voyage=VoyageSerializer(many=False)
	captive_fate=CaptiveFateSerializer(many=False)
	sources_conn=EnslavedSourceConnectionSerializer(many=True,read_only=True)
	transactions=EnslavedInRelationSerializer(many=True,read_only=True)
	captive_status=CaptiveStatusSerializer(many=False)
	class Meta:
		model=Enslaved
		fields='__all__'

class EnslaverSerializer(DynamicFieldsModelSerializer):
	principal_location=PlaceSerializer(many=False)
	alias=EnslaverAliasSerializer(many=True,read_only=True)
	enslaver_sources=EnslaverIdentitySourceConnectionSerializer(many=True,read_only=True)
	class Meta:
		model=EnslaverIdentity
		fields='__all__'
		




