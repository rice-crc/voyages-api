import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import *
from common.models import SparseDate

class Command(BaseCommand):
	help = 'Maps all comma-spliced voyage fields to their new counterparts'
	def handle(self, *args, **options):
		voyages=Voyage.objects.all()
		
		for v in voyages:
			print(v)
			vd=v.voyage_dates
			vdfields=[i for i in list(vd.__dict__.keys()) if i not in ('_state','id') and not i.endswith('_id')]
			
			for vdfield in vdfields:
				vdval=eval('vd.'+vdfield)
				if "," in str(vdval):
					m,d,y=[int(i) if i!='' else None for i in vdval.split(',')]
# 					print(vdfield,[m,d,y])
					sd=SparseDate.objects.create(
						day=d,
						month=m,
						year=y
					)
# 					print(sd)
					exec('vd.'+vdfield+'_sparsedate=sd')
			vd.save()
# 			print(vd)
