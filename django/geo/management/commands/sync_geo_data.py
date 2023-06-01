import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import *
from geo.models import *

class Command(BaseCommand):
	help = 'maps all voyage geo data to their new counterparts'
	def handle(self, *args, **options):
		places=Place.objects.all()
		regions=Region.objects.all()
		broadregions=BroadRegion.objects.all()
		geolocations=Location.objects.all()
		
		print(places)
		print(regions)
		print(broadregions)
		print(geolocations)
		
		regionvals=[]
		
		for p in [regions,broadregions]:
			regionvals+=[l[0] for l in p.values_list('value')]
			
		placevals=[l[0] for l in places.values_list('value')]
		
		for br in broadregions:
			
			LT,LT_isnew=LocationType.objects.get_or_create(
				name="Broad Region"
			)
			
			thislocation=Location.objects.get_or_create(
				longitude=br.longitude,
				latitude=br.latitude,
				name=br.broad_region,
				location_type=LT,
				value=br.value
			)
		
		for r in regions:
			
			LT,LT_isnew=LocationType.objects.get_or_create(
				name="Region"
			)
			
			parent=Location.objects.get(value=r.broad_region.value)
			
			thislocation=Location.objects.get_or_create(
				longitude=r.longitude,
				latitude=r.latitude,
				name=r.region,
				location_type=LT,
				value=r.value,
				child_of=parent
			)
			
		for p in places:
			
			LT,LT_isnew=LocationType.objects.get_or_create(
				name="Place"
			)
			
			parent=Location.objects.get(value=p.region.value)
			
			if p.value in regionvals:
				sv=p.value
				placevals.remove(sv)
				while sv in regionvals+placevals:
					sv+=1
				placevals.append(sv)
				pvalue=sv
				print("CONFLICT:",p.value,p.place,"renamed to",sv)
			else:
				pvalue=p.value
			
			thislocation=Location.objects.get_or_create(
				longitude=p.longitude,
				latitude=p.latitude,
				name=p.place,
				location_type=LT,
				value=pvalue,
				child_of=parent
			)
