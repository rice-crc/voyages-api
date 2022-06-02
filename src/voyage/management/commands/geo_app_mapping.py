from voyage.models import Place, Region, BroadRegion
from geo.models import *
import requests
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os

#worth noting that they do have one spss code collision -- btw regions and places
#mismatch with: 621 Americas, region unspecified 80200 True --> Americas 2455 80200 Region
#we'll need to patch that by hand and let the team know

class Command(BaseCommand):
	help = 'This is a one-off that I wanted to have live in manual_db_migrations. But it needs to be in django commands or else it won\'t work. I love this framework.'
	def handle(self, *args, **options):

		locations=Location.objects.all()
		
		print("-----------PLACES-----------")
		
		places=Place.objects.all()
		
		for place in places:
			place_id=place.id
			place_name=place.place
			place_spss_code=place.value
			place_loc_link_code=place.geo_location_id
			if place_loc_link_code==None:
				try:
					kwargs={'value':place_spss_code}
					matching_location=locations.filter(**kwargs)[0]
					matching_location_name=matching_location.name
					matching_location_id=matching_location.id
					matching_location_spss_code=matching_location.value
					matching_location_type=matching_location.location_type
					if matching_location_spss_code==place_spss_code and matching_location_name==place_name:
						place.geo_location_id=matching_location_id
						place.save()
					else:
						print("mismatch with:",place_id,place_name,place_spss_code,place_loc_link_code==None,"-->",matching_location_name,matching_location_id,matching_location_spss_code,matching_location_type)
				except:
					print("error updating:",place_id,place_name,place_spss_code)
			else:
				print("link already exists:",place_id,place_name,place_spss_code,place_loc_link_code)

		print("-----------REGIONS-----------")

		regions=Region.objects.all()

		for region in regions:
			region_id=region.id
			region_name=region.region
			region_spss_code=region.value
			region_loc_link_code=region.geo_location_id
			if region_loc_link_code==None:
				try:
					kwargs={'value':region_spss_code}
					matching_location=locations.filter(**kwargs)[0]
					matching_location_name=matching_location.name
					matching_location_id=matching_location.id
					matching_location_spss_code=matching_location.value
					matching_location_type=matching_location.location_type
					if matching_location_spss_code==region_spss_code and matching_location_name==region_name:
						region.geo_location_id=matching_location_id
						region.save()
					else:
						print("mismatch with:",region_id,region_name,region_spss_code,region_loc_link_code==None,"-->",matching_location_name,matching_location_id,matching_location_spss_code,matching_location_type)
				except:
					print("error updating:",region_id,region_name,region_spss_code)
			else:
				print("link already exists:",region_id,region_name,region_spss_code,region_loc_link_code)
		
		print("-----------BROAD REGIONS-----------")

		broadregions=BroadRegion.objects.all()

		for broad_region in broadregions:
			broad_region_id=broad_region.id
			broad_region_name=broad_region.broad_region
			broad_region_spss_code=broad_region.value
			broad_region_loc_link_code=broad_region.geo_location_id
			if broad_region_loc_link_code==None:
				try:
					kwargs={'value':broad_region_spss_code}
					matching_location=locations.filter(**kwargs)[0]
					matching_location_name=matching_location.name
					matching_location_id=matching_location.id
					matching_location_spss_code=matching_location.value
					matching_location_type=matching_location.location_type
					if matching_location_spss_code==broad_region_spss_code and matching_location_name==broad_region_name:
						broad_region.geo_location_id=matching_location_id
						broad_region.save()
					else:
						print("mismatch with:",broad_region_id,broad_region_name,broad_region_spss_code,broad_region_loc_link_code==None,"-->",matching_location_name,matching_location_id,matching_location_spss_code,matching_location_type)
				except:
					print("error updating:",broad_region_id,broad_region_name,broad_region_spss_code)
			else:
				print("link already exists:",broad_region_id,broad_region_name,broad_region_spss_code,broad_region_loc_link_code)
