from geo.models import *
from voyage.models import *
from geo.models import *
from django.db.models import Avg,Sum,Min,Max,Count,Q
import mysql.connector
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os
import re
from math import sqrt






class Command(BaseCommand):
	help = '\
		This syncs the legacy geo data into the new geo application. \
		Provide it with a connection to the legacy sql in dbconf.json \
		Then let it rip. \
		Does not deal with the "show on map" variables. \
		It also nulls out all lat/longs that have been set to 0,0 \
	'
	def handle(self, *args, **options):
		
		conf={
		  "user": "root",
		  "password": "voyages",
		  "host": "voyages-mysql",
		  "database":"voyages_legacy"
		}
		
		cnx = mysql.connector.connect(**conf)
		cursor = cnx.cursor()
		
		#get all broad regions and insert into db, keeping a running list of keys
		location_types_mappings=[["Port","voyage_place","place"],["Region","voyage_region","region"],["Broad Region","voyage_broadregion","broad_region"]]
		
		for location_types_mapping in location_types_mappings:
			location_type_name,legacy_db_table,legacy_locationtype_name=location_types_mapping
		
			cursor.execute("select id,%s,`value`,longitude,latitude from %s;" %(legacy_locationtype_name,legacy_db_table))
			resp=cursor.fetchall()
			location_types=LocationType.objects.all()
			locations=Location.objects.all()
			
			locationtype=location_types.filter(**{'name':location_type_name})[0]
			
			for location_entry in resp:
				legacy_id,legacy_name,legacy_spss_code,legacy_long,legacy_lat=location_entry
				queryset=locations.filter(**{'value':legacy_spss_code})
				if len(queryset)==1:
					location=queryset[0]
					new_name=location.name
					new_lat=location.latitude
					new_long=location.longitude
					print('----')
					if new_name != legacy_name or new_lat != legacy_lat or new_long != legacy_long:
						print('conflict:')
						print('OLD:',legacy_name,legacy_long,legacy_lat)
						print('NEW:',new_name,new_long,new_lat)
						location.name=legacy_name
						location.latitude=legacy_lat
						location.longitude=legacy_long
						location.save()
					else:
						print('no change for',legacy_name,legacy_spss_code)
					print('----')
				elif len(queryset)==0:
					
					print("----\nnew location:",legacy_name)
					
					location=Location(
						name=legacy_name,
						latitude=legacy_lat,
						longitude=legacy_long,
						location_type=locationtype,
						value=legacy_spss_code
					)
					
					location.save()
					
					print('----')
				
				else:
					print("ERROR -- NON-UNIQUE SPSS CODES:",queryset)
		
		#here we sweep all the bad entries into nulled lat/long pairs
		#2 cases are handled.
		##1. for some godforsaken reason they have some entries with one coordinate null and another not
		##2. 0,0 was frequently used in place of nulls
		
		locations=Location.objects.all()
		null_lats=locations.filter(latitude=None).update(longitude=None)
		null_longs=locations.filter(longitude=None).update(latitude=None)
					
		zeroes=locations.filter(latitude__gte=-.5)
		zeroes=zeroes.filter(latitude__lte=.5)
		zeroes=zeroes.filter(longitude__gte=-.5)
		zeroes=zeroes.filter(longitude__lte=.5)
		zeroes.update(latitude=None)
		zeroes.update(longitude=None)
			