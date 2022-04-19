import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage
import time
import os

class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		#this one will run off api calls -- likely df calls
		#the goal is to set up super fast access to items
		##based on pk autoincrement ids
		##to enable performant rendering of tailored views
		#like voyage_ids
		##to enable the voyage map animations
		#we'll use it to build
		##"index" tables storing json blobs [takes a while to build and even then slower than a live call it turns out]
		####indexed 11 fields (for voyage animations) in 22 seconds
		####indexed 67 fields (for full list of current data table vars) in 104 seconds
		##flat files w line ids corresponding to the pk ids [fast to build, fast to read]
		##redis caches or solr indices
		
		
		#FIRST FIELD MUST BE THE PK ON THE TOP TABLE BEING INDEXED
		
		indices={
			'voyage_animations': {
				'vars':	[
					'id',
					'voyage_itinerary__imp_principal_port_slave_dis__longitude',
					'voyage_itinerary__imp_principal_port_slave_dis__latitude',
					'voyage_itinerary__imp_principal_port_slave_dis__place',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__place',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__longitude',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__latitude',
					'voyage_ship__imputed_nationality__name',
					'voyage_ship__tonnage',
					'voyage_ship__ship_name',
					'voyage_slaves_numbers__imp_total_num_slaves_embarked'
					],
				'fname':'voyage_animation.json'
			},
			'voyage_alltablevariables': {
				'vars': [
					'id',
					'voyage_captainconnection__captain__name',
					'voyage_crew__crew_died_complete_voyage',
					'voyage_crew__crew_first_landing',
					'voyage_crew__crew_voyage_outset',
					'voyage_dates__date_departed_africa',
					'voyage_dates__departure_last_place_of_landing',
					'voyage_dates__first_dis_of_slaves',
					'voyage_itinerary__first_landing_place__place',
					'voyage_itinerary__first_place_slave_purchase__place',
					'voyage_ship__guns_mounted',
					'voyage_dates__imp_arrival_at_port_of_dis',
					'voyage_dates__imp_length_home_to_disembark',
					'voyage_itinerary__port_of_departure__place',
					'voyage_itinerary__principal_place_of_slave_purchase__place',
					'voyage_itinerary__principal_port_of_slave_dis__place',
					'voyage_slaves_numbers__imp_total_num_slaves_embarked',
					'voyage_slaves_numbers__imp_total_num_slaves_disembarked',
					'voyage_slaves_numbers__imp_mortality_during_voyage',
					'voyage_slaves_numbers__imp_mortality_ratio',
					'voyage_ship__imputed_nationality__name',
					'voyage_slaves_numbers__percentage_boys_among_embarked_slaves',
					'voyage_slaves_numbers__child_ratio_among_embarked_slaves',
					'voyage_slaves_numbers__percentage_girls_among_embarked_slaves',
					'voyage_slaves_numbers__male_ratio_among_embarked_slaves',
					'voyage_slaves_numbers__percentage_men_among_embarked_slaves',
					'voyage_slaves_numbers__percentage_women_among_embarked_slaves',
					'voyage_slaves_numbers__imp_jamaican_cash_price',
					'voyage_dates__length_middle_passage_days',
					'voyage_ship__nationality_ship',
					'voyage_slaves_numbers__num_slaves_carried_first_port',
					'voyage_slaves_numbers__num_slaves_carried_second_port',
					'voyage_slaves_numbers__num_slaves_carried_third_port',
					'voyage_slaves_numbers__num_slaves_disembark_first_place',
					'voyage_slaves_numbers__num_slaves_disembark_second_place',
					'voyage_slaves_numbers__num_slaves_disembark_third_place',
					'voyage_slaves_numbers__num_slaves_intended_first_port',
					'voyage_outcome__outcome_owner__name',
					'voyage_outcome__vessel_captured_outcome__name',
					'voyage_outcome__outcome_slaves__name',
					'voyage_outcome__particular_outcome__name',
					'voyage_shipownerconnection__owner__name',
					'voyage_itinerary__place_voyage_ended__place',
					'voyage_itinerary__port_of_call_before_atl_crossing',
					'voyage_ship__registered_place__place',
					'voyage_ship__registered_year',
					'voyage_outcome__resistance__name',
					'voyage_ship__rig_of_vessel__name',
					'voyage_itinerary__second_landing_place__place',
					'voyage_itinerary__second_place_slave_purchase__place',
					'voyage_ship__ship_name',
					'voyage_dates__slave_purchase_began',
					'voyage_sourceconnection__source__full_ref',
					'voyage_itinerary__third_landing_place__place',
					'voyage_itinerary__third_place_slave_purchase__place',
					'voyage_ship__tonnage',
					'voyage_ship__tonnage_mod',
					'voyage_slaves_numbers__total_num_slaves_arr_first_port_embark',
					'voyage_ship__vessel_construction_place__place',
					'voyage_dates__voyage_began',
					'voyage_dates__voyage_completed',
					'voyage_id',
					'voyage_ship__year_of_construction',
					'voyage_itinerary__imp_port_voyage_begin__place',
					'voyage_itinerary__imp_principal_place_of_slave_purchase__place',
					'voyage_itinerary__imp_principal_port_slave_dis__place'
				],
				'fname':'voyage_export.json'
			}
		}
		
		base_filepath='static/customcache'
		os.makedirs(base_filepath,exist_ok=True)
		
		url='http://127.0.0.1:8000/voyage/dataframes'
		from .app_secrets import headers
		
		for ind in indices:
			st=time.time()
			vars=indices[ind]['vars']
			fname=indices[ind]['fname']
			print('fetching all',ind)
			data={'selected_fields':vars}
			r=requests.post(url=url,headers=headers,data=data)
			columns=json.loads(r.text)
			pk=vars[0]
			
			number_entries=len(columns[pk])
			
			print("fetched %d fields on %d entries" %(len(vars),number_entries))
			
			print("indexing...")
			
			try:
				os.remove(fname)
			except:
				pass
			
			def listflattener(inputval):
				#m2m fields are still returned in nested format
				###(should I fix this at the serializer level?)
				#usually as lists of dicts with a single key across them
				
				if type(inputval)==list:
					outputlist=[]
					for i in inputval:
						if type(i)==list:
							outputlist+=i
						elif type(i)==dict:
							intermedlist=[i[k] for k in i]
							outputlist += intermedlist
					return(' | '.join([str(i) for i in outputlist]))
				else:
					return(inputval)
			
			j={"ordered_keys":[v for v in vars],"items":{}}
			for row_idx in range(number_entries):
				row=[listflattener(columns[col][row_idx]) for col in vars]
				id=columns[pk][row_idx]
				j['items'][id]=row
			d=open(os.path.join(base_filepath,fname),'w')
			d.write(json.dumps(j))
			d.close()
			elapsed_seconds=int(time.time()-st)
			print("...finished in %d minutes %d seconds" %(int(elapsed_seconds/60),elapsed_seconds%60))