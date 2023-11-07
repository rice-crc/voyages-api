import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage
from past.models import *
from blog.models import Post
import pysolr
import numpy as np


class Command(BaseCommand):
	help = 'rebuilds the solr indices'
	def handle(self, *args, **options):
		indices=[
			{
				"model":Voyage,
				"core_name":"voyages",
				"fields":[
					"id",
					"voyage_itinerary__port_of_departure__name",
					"voyage_itinerary__int_first_port_emb__name",
					"voyage_itinerary__int_second_port_emb__name",
					"voyage_itinerary__int_first_region_purchase_slaves__name",
					"voyage_itinerary__int_second_region_purchase_slaves__name",
					"voyage_itinerary__int_first_port_dis__name",
					"voyage_itinerary__int_second_port_dis__name",
					"voyage_itinerary__int_first_region_slave_landing__name",
					"voyage_itinerary__imp_principal_region_slave_dis__name",
					"voyage_itinerary__int_second_place_region_slave_landing__name",
					"voyage_itinerary__first_place_slave_purchase__name",
					"voyage_itinerary__second_place_slave_purchase__name",
					"voyage_itinerary__third_place_slave_purchase__name",
					"voyage_itinerary__first_region_slave_emb__name",
					"voyage_itinerary__second_region_slave_emb__name",
					"voyage_itinerary__third_region_slave_emb__name",
					"voyage_itinerary__port_of_call_before_atl_crossing__name",
					"voyage_itinerary__first_landing_place__name",
					"voyage_itinerary__second_landing_place__name",
					"voyage_itinerary__third_landing_place__name",
					"voyage_itinerary__first_landing_region__name",
					"voyage_itinerary__second_landing_region__name",
					"voyage_itinerary__third_landing_region__name",
					"voyage_itinerary__place_voyage_ended__name",
					"voyage_itinerary__region_of_return__name",
					"voyage_itinerary__broad_region_of_return__name",
					"voyage_itinerary__imp_port_voyage_begin__name",
					"voyage_itinerary__imp_region_voyage_begin__name",
					"voyage_itinerary__imp_broad_region_voyage_begin__name",
					"voyage_itinerary__principal_place_of_slave_purchase__name",
					"voyage_itinerary__imp_principal_place_of_slave_purchase__name",
					"voyage_itinerary__imp_principal_region_of_slave_purchase__name",
					"voyage_itinerary__imp_broad_region_of_slave_purchase__name",
					"voyage_itinerary__principal_port_of_slave_dis__name",
					"voyage_itinerary__imp_principal_port_slave_dis__name",
					"voyage_itinerary__imp_broad_region_slave_dis__name",
					"voyage_enslavement_relations__relation_enslavers__enslaver_alias__alias",
					"voyage_enslavement_relations__enslaved_in_relation__enslaved__documented_name",
					"voyage_ship__rig_of_vessel__name",
					"voyage_ship__imputed_nationality__name",
					"voyage_ship__ton_type__name",
					"voyage_ship__vessel_construction_place__name",
					"voyage_ship__vessel_construction_region__name",
					"voyage_ship__registered_place__name",
					"voyage_ship__registered_region__name",
					"voyage_ship__ship_name",
					"voyage_outcome__outcome_owner__name",
					"voyage_outcome__outcome_slaves__name",
					"voyage_outcome__particular_outcome__name",
					"voyage_outcome__resistance__name",
					"voyage_outcome__vessel_captured_outcome__name"
				]
			},
			{
				"model":EnslaverIdentity,
				"core_name":"enslavers",
				"fields":[
					'id',
					'principal_location__name',
					'enslaver_source_connections__source__short_ref__name',
					'enslaver_source_connections__source__title',
					'enslaver_source_connections__source__notes',
					'aliases__enslaver_relations__relation__enslaved_in_relation__enslaved__documented_name',
					'aliases__enslaver_relations__relation__relation_type__name',
					'aliases__enslaver_relations__relation__place__name',
					'aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__name',
					'aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__name',
					'aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__name',
					'aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__name',
					'aliases__enslaver_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name',
					'aliases__enslaver_relations__relation__voyage__voyage_itinerary__int_first_port_dis__name',
					'aliases__enslaver_relations__relation__voyage__voyage_ship__ship_name',
					'aliases__enslaver_relations__relation__voyage__voyage_outcome__particular_outcome__name',
					'aliases__alias',
					'birth_place__name',
					'death_place__name',
					'principal_alias',
					'father_name',
					'father_occupation',
					'mother_name',
					'notes'
				]
			},
			{
				"model":Enslaved,
				"core_name":"enslaved",
				"fields":[
					'id',
					'post_disembark_location__name',
					'enslaved_relations__relation__voyage__voyage_itinerary__imp_port_voyage_begin__name',
					'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__name',
					'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_port_slave_dis__name',
					'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_of_slave_purchase__name',
					'enslaved_relations__relation__voyage__voyage_itinerary__imp_principal_region_slave_dis__name',
					'enslaved_relations__relation__voyage__voyage_itinerary__int_first_port_dis__name',
					'enslaved_relations__relation__voyage__voyage_ship__ship_name',
					'enslaved_relations__relation__voyage__voyage_outcome__particular_outcome__name',
					'enslaved_relations__relation__relation_enslavers__enslaver_alias__alias',
					'captive_fate__name',
					'enslaved_relations__relation__relation_type__name',
					'enslaved_relations__relation__place__name',
					'captive_status__name',
					'language_group__name',
					'enslaved_source_connections__source__short_ref__name',
					'enslaved_source_connections__source__title',
					'enslaved_source_connections__source__notes',
					'enslaved_source_connections__page_range',
					'documented_name',
					'name_first',
					'name_second',
					'name_third',
					'modern_name',
					'skin_color',
					'notes'
				]
			},
			{
				"model":Post,
				"core_name":"blog",
				"fields":[
					'id',
					'authors__name',
					'authors__description',
					'authors__role',
					'tags__name',
					'tags__intro',
					'title',
					'subtitle',
					'content'
				]
			},
			

			
			
		]
		
		results_per_page=1000
		
		for idx in indices:
			
			model=idx["model"]
			fields=idx["fields"]
			core_name=idx["core_name"]
			print("INDEXING",core_name,"on",len(fields),"fields")
			
			if fields[0]!="id":
				print("FIRST FIELD INDEX MUST BE NAMED `ID`")
				exit()

			solr = pysolr.Solr(
				'http://voyages-solr:8983/solr/%s/' %core_name,
				always_commit=True,
				timeout=10
			)
			
			queryset=model.objects.all()
			
			ids=[i[0] for i in queryset.values_list('id')]
			
			if len(ids)>0:
			
				batch_size=5000
			
				pagecount=int(len(ids)/batch_size)
				if pagecount==0:
					pagecount=1
				
				pages=np.array_split(np.array(ids),pagecount)
			
				p=1
			
				for page in pages:
					print("--page",p,'of',pagecount)
				
					pageidlist=[int(v) for v in page]
				
					pagedict={v:[] for v in pageidlist}
				
					pagequeryset=queryset.filter(id__in=pageidlist)
				
					for f in fields:
						vl=pagequeryset.values_list('id',f)
						for v in vl:
							id,i=v
							if i!=None:
								pagedict[id].append(str(i))
				
					solrpage=[
						{
							"id":k,
							"text":" ".join(pagedict[k])
						}
						for k in pagedict
					]
				
					solr.add(solrpage)
					p+=1
			else:
				print("-----FOUND NO RESULTS----")