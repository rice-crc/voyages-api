from voyage.models import Place, Region, BroadRegion
from geo.models import *
import requests
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os

class Command(BaseCommand):
	help = 'This is a one-off that I wanted to have live in manual_db_migrations. But it needs to be in django commands or else it won\'t work. I love this framework.'
	def handle(self, *args, **options):

		locations=Location.objects.all()
		
		print("-----------LOCATIONS-----------")
		
		for location in locations:
			loc_id=location.id
			loc_typename=location.location_type
			#as of june 1 the loc typenames are "Port", "Region", "Broad Region"
			loc_spss_code=location.value
			print(loc_id,loc_typename,loc_spss_code)
			break
		
		print("-----------PLACES-----------")
		
		places=Place.objects.all()
		
		for place in places:
			place_id=place.id
			place_name=place.place
			place_spss_code=place.value
			kwargs={'value':place_spss_code}
			matching_location=locations.filter(**kwargs)[0]
			
			matching_location_name=matching_location.name
			matching_location_id=56
			matching_location_spss_code=67
			
			print(matching_location_name)
			break

		print("-----------REGIONS-----------")

		regions=Region.objects.all()
		
		for region in regions:
			region_id=region.id
			region_spss_code=region.value
			print(region_id,region_spss_code)
			break
		
		print("-----------BROAD REGIONS-----------")

		broadregions=BroadRegion.objects.all()

		for broadregion in broadregions:
			broadregion_id=broadregion.id
			broadregion_spss_code=broadregion.value
			print(broadregion_id,broadregion_spss_code)
			break
