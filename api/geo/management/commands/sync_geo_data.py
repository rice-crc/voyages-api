import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import *
from geo.models import *
import uuid

class Command(BaseCommand):
	help = '\
	--maps all classic spss voyage geo data to their new "geolocation" counterparts. \
	1. Used to blow away all the new geolocation entities \
	2. Now it just checks against the spss vals ("Value"), and either updates or creates\
	3. So if you change or add a legacy Region, Place, or BroadRegion entry...\
	--> this will update your geo_location entity data accordingly\
	** Eventually we want to fully deprecate the legacy Region Place & BroadRegion Types\
	** In favor of the unified GeoLocation type\
	'
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
			
			thislocation,thislocation_isnew=Location.objects.get_or_create(
				value=br.value
			)
			
			thislocation.longitude=br.longitude
			thislocation.latitude=br.latitude
			thislocation.name=br.broad_region
			thislocation.location_type=LT
			thislocation.uuid=uuid.uuid4()
			thislocation.save()
			
			br.geo_location=thislocation
			br.save()
		
		for r in regions:
			
			LT,LT_isnew=LocationType.objects.get_or_create(
				name="Region"
			)
			
			parent=Location.objects.get(value=r.broad_region.value)
			
			thislocation,thislocation_isnew=Location.objects.get_or_create(
				value=r.value
			)

			thislocation.longitude=r.longitude
			thislocation.latitude=r.latitude
			thislocation.name=r.region
			thislocation.location_type=LT
			thislocation.child_of=parent
			thislocation.uuid=uuid.uuid4()
			thislocation.save()

			r.geo_location=thislocation
			r.save()
			
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
			
			thislocation,thislocation_isnew=Location.objects.get_or_create(
				value=pvalue
			)
			thislocation.longitude=p.longitude
			thislocation.latitude=p.latitude
			thislocation.name=p.place
			thislocation.location_type=LT
			thislocation.child_of=parent
			thislocation.uuid=uuid.uuid4()
			thislocation.save()
			p.geo_location=thislocation
			p.save()
