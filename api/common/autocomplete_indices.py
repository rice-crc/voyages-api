from voyage.models import Voyage,VoyageShip
from past.models import EnslaverAlias,Enslaved
from blog.models import Post
from document.models import Source

autocomplete_indices=[
	{
		"model":Source,
		"core_name":"autocomplete_source_titles",
		"fields":[
			'id',
			'title',
			'short_ref__name'
		],
		"related_fields":[
			'enslaved_source_connections__source__title',
			'aliases__enslaver_voyage_connection__voyage__voyage_source_connections__source__title',
			'aliases__enslaver_relations__relation__voyage__voyage_source_connections__source__title',
			'voyage_source_connections__source__title'
		]
	},
	{
		"model":EnslaverAlias,
		"core_name":"autocomplete_enslaver_aliases",
		"fields":[
			'id',
			'alias',
			'identity__principal_alias'
		],
		"related_fields":[
			'enslaved_relations__relation__relation_enslavers__enslaver_alias__alias',
			'voyage__voyage_enslaver_connection__enslaver_alias__alias',
			'enslavers__enslaver_alias__alias',
			'voyage_enslavement_relations__relation_enslavers__enslaver_alias__alias',
			'aliases__alias',
			'voyage_enslavement_relations__relation_enslavers__enslaver_alias__alias',
			'voyage_enslaver_connection__enslaver_alias__alias'
		]
	},
	{
		"model":Enslaved,
		"core_name":"autocomplete_enslaved_names",
		"fields":[
			'id',
			'documented_name',
			'modern_name'
		],
		"related_fields":[
			'aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__documented_name',
			'aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__modern_name',
			'voyage_enslavement_relations__enslaved_in_relation__enslaved__documented_name',
			'voyage_enslavement_relations__enslaved_in_relation__enslaved__modern_name',
			'modern_name',
			'documented_name'
		]
	},
	{
		"model":VoyageShip,
		"core_name":"autocomplete_ship_names",
		"fields":[
			'ship_name'
		],
		"related_fields":[
			'voyage__voyage_ship__ship_name',
			'voyage_ship__ship_name',
			'aliases__enslaver_relations__relation__voyage__voyage_ship__ship_name',
			'enslaved_relations__relation__voyage__voyage_ship__ship_name'
		]
	}
]

def get_inverted_autocomplete_indices():
	inverted_autocomplete_indices={
		field:{
			'model':ac_index['model'],
			'core_name':ac_index['core_name'],
			'fields':ac_index['fields']
		}
		for ac_index in autocomplete_indices for field in ac_index['related_fields']
	}
	return inverted_autocomplete_indices