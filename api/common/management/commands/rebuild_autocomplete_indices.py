import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage,VoyageShip
from past.models import EnslaverAlias,Enslaved
from blog.models import Post
from document.models import Source
import pysolr
import numpy as np
from voyages3.localsettings import SOLR_ENDPOINT

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
			'ship_name',
			'voyage__voyage_ship__ship_name',
			'voyage_ship__ship_name',
			'aliases__enslaver_relations__relation__voyage__voyage_ship__ship_name',
			'enslaved_relations__relation__voyage__voyage_ship__ship_name'
		]
	}
]

inverted_autocomplete_indices={}

for ac_index in autocomplete_indices:
	ac_index_model=ac_index['model']
	ac_index_core_name=ac_index['core_name']
	ac_index_fields=ac_index['fields']
	for rf in ac_index['related_fields']:
		inverted_autocomplete_indices[rf]={
			'model':ac_index_model,
			'core_name':ac_index_core_name,
			'fields':ac_index_fields
		}

class Command(BaseCommand):
	help = 'rebuilds the solr indices'
	def handle(self, *args, **options):
		for idx in autocomplete_indices:
			model=idx["model"]
			fields=idx["fields"]
			if fields[0] != 'id':
				print("FIRST INDEXED FIELD MUST BE INTEGER PK ('id')")
			
			core_name=idx["core_name"]
			print("INDEXING",core_name,"on",len(fields),"fields")
			solr = pysolr.Solr(
				f'{SOLR_ENDPOINT}/{core_name}/',
				always_commit=True,
				timeout=10
			)
			queryset=model.objects.all()
			if queryset.count()>0:
				#here, we're not interested in id's per se but rather the unique text values
				valtuples=list(eval('queryset.values_list("'+'","'.join(fields)+'")'))
				indexdictionary={}
				solrindex=[]
				#so for our reference we'll just keep one good id for each unique str value
				for valtuple in valtuples:
					id=valtuple[0]
					valstr=' '.join([v for v in valtuple[1:] if v is not None])
					indexdictionary[valstr]=id
				for k in indexdictionary:
					solrindex.append({"id":indexdictionary[k],"text":k})
				solr.add(solrindex)
			else:
				print("-----FOUND NO RESULTS----")
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				