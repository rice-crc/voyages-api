import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage,VoyageAnimationIndex
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
		#we'll use it to build either
		##"index" tables storing json blobs
		##flat files w line ids corresponding to the pk ids
		##redis caches or solr indices
		###(but solr may not be able to handle thousands of pk's as a search query? i've seen it break on queries like that before)
		#FIRST FIELD MUST BE THE PK ON THE TOP TABLE BEING INDEXED
		#AND THE INDEXED JSON DUMP FIELD NAME WILL ALWAYS BE 'json_dump'
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
				'indexing_model': VoyageAnimationIndex,
				'fname':'voyage/voyage_animations__index.json',
				'indexed_model': Voyage,
				'index_fk_fieldname':'voyage_animation_index'
			}
		}
		
		url='http://127.0.0.1:8000/voyage/dataframes'
		from .app_secrets import headers
		
		for ind in indices:
			st=time.time()
			vars=indices[ind]['vars']
			indexing_model=indices[ind]['indexing_model']
			indexed_model=indices[ind]['indexed_model']
			fname=indices[ind]['fname']
			index_fk_fieldname=indices[ind]['index_fk_fieldname']
			print('deleting all',ind)
			indexing_model.objects.all().delete()
			
			print('fetching all',ind)
			data={'selected_fields':vars}
			r=requests.post(url=url,headers=headers,data=data)
			columns=json.loads(r.text)
			fk=vars[0]
			
			number_entries=len(columns[fk])
			
			print("fetched %d fields on %d entries" %(len(vars),number_entries))
			
			print("indexing...")
			
			try:
				os.remove(fname)
			except:
				pass
			d=open(fname,'w')
			
			j={}
			for row_idx in range(number_entries):
				row=[columns[col][row_idx] for col in vars]
				id=columns[fk][row_idx]
				j[id]=row
			d.write(json.dumps(j))
			d.close()
			elapsed_seconds=int(time.time()-st)
			print("...finished in %d minutes %d seconds" %(int(elapsed_seconds/60),elapsed_seconds%60))
			
			
			#this seemed like it could be a slick solution but it's not a fast retrieval
			#for row_idx in range(number_entries):
			#	row=[columns[col][row_idx] for col in vars]
			#	id=columns[fk][row_idx]
			#	
			#	#keep it light in this prelim test, only do every 50th
			#	indexing_object=indexing_model(json_dump=json.dumps(row))
			#	indexing_object.save()
			#	indexed_object=indexed_model.objects.get(pk=id)
			#	setattr(indexed_object,index_fk_fieldname,indexing_object)
			#	indexed_object.save()
			#	if row_idx%1000==0:
			#		print(row_idx)
			#elapsed_seconds=int(time.time()-st)
			#print("...finished in %d minutes %d seconds" %(int(elapsed_seconds/60),elapsed_seconds%60))
					