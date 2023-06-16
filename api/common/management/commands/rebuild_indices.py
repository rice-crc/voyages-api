import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage
from past.models import Enslaved,EnslaverIdentity
import pysolr
import numpy as np

class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		indices=[
			{
				"model":Voyage,
				"core_name":"voyages",
				"fields":[
					"id",
					"voyage_enslaver_connection__enslaver_alias__alias",
					"voyage_itinerary__port_of_departure__geo_location__name",
					"voyage_itinerary__int_first_port_emb__geo_location__name",
					"voyage_itinerary__int_second_port_emb__geo_location__name",
					"voyage_itinerary__int_first_region_purchase_slaves__geo_location__name",
					"voyage_itinerary__int_second_region_purchase_slaves__geo_location__name",
					"voyage_itinerary__int_first_port_dis__geo_location__name",
					"voyage_itinerary__int_second_port_dis__geo_location__name",
					"voyage_itinerary__int_first_region_slave_landing__geo_location__name",
					"voyage_itinerary__imp_principal_region_slave_dis__geo_location__name",
					"voyage_itinerary__int_second_place_region_slave_landing__geo_location__name",
					"voyage_itinerary__first_place_slave_purchase__geo_location__name",
					"voyage_itinerary__second_place_slave_purchase__geo_location__name",
					"voyage_itinerary__third_place_slave_purchase__geo_location__name",
					"voyage_itinerary__first_region_slave_emb__geo_location__name",
					"voyage_itinerary__second_region_slave_emb__geo_location__name",
					"voyage_itinerary__third_region_slave_emb__geo_location__name",
					"voyage_itinerary__port_of_call_before_atl_crossing__geo_location__name",
					"voyage_itinerary__first_landing_place__geo_location__name",
					"voyage_itinerary__second_landing_place__geo_location__name",
					"voyage_itinerary__third_landing_place__geo_location__name",
					"voyage_itinerary__first_landing_region__geo_location__name",
					"voyage_itinerary__second_landing_region__geo_location__name",
					"voyage_itinerary__third_landing_region__geo_location__name",
					"voyage_itinerary__place_voyage_ended__geo_location__name",
					"voyage_itinerary__region_of_return__geo_location__name",
					"voyage_itinerary__broad_region_of_return__geo_location__name",
					"voyage_itinerary__imp_port_voyage_begin__geo_location__name",
					"voyage_itinerary__imp_region_voyage_begin__geo_location__name",
					"voyage_itinerary__imp_broad_region_voyage_begin__geo_location__name",
					"voyage_itinerary__principal_place_of_slave_purchase__geo_location__name",
					"voyage_itinerary__imp_principal_place_of_slave_purchase__geo_location__name",
					"voyage_itinerary__imp_principal_region_of_slave_purchase__geo_location__name",
					"voyage_itinerary__imp_broad_region_of_slave_purchase__geo_location__name",
					"voyage_itinerary__principal_port_of_slave_dis__geo_location__name",
					"voyage_itinerary__imp_principal_port_slave_dis__geo_location__name",
					"voyage_itinerary__imp_broad_region_slave_dis__geo_location__name",
					"voyage_enslaver_connection__role__name",
					"voyage_enslaved_people__documented_name",
					"voyage_ship__rig_of_vessel__name",
					"voyage_ship__imputed_nationality__name",
					"voyage_ship__ton_type__name",
					"voyage_ship__vessel_construction_place__geo_location__name",
					"voyage_ship__vessel_construction_region__geo_location__name",
					"voyage_ship__registered_place__geo_location__name",
					"voyage_ship__registered_region__geo_location__name",
					"voyage_ship__ship_name",
					"voyage_name_outcome__outcome_owner__name",
					"voyage_name_outcome__outcome_slaves__name",
					"voyage_name_outcome__particular_outcome__name",
					"voyage_name_outcome__resistance__name",
					"voyage_name_outcome__vessel_captured_outcome__name"
				]
			}
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
			
			batch_size=5000
			
			pagecount=int(len(ids)/batch_size)
			
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