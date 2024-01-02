import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from document.models import *
from voyages3.settings import *
import requests
import json
import os
import re

class Command(BaseCommand):
	help = 'fixes a huntington bug'
	def handle(self, *args, **options):
		
		# apparently when I pushed the huntington sources, i treated the titles as unique
		# they are not!
		# the below walks through the huntington collection
		
		# finds discontinuous page ranges (after the first continuous page range)
		# and captures these as a dictionary
		# {huntington_source_id:[page_source_connection_ids...]}
		
		sources=Source.objects.all()
		huntingtonsources=sources.filter(short_ref__name__icontains="DOCP Huntington")
		sources_to_fix={}
		
		c=0
		for hs in huntingtonsources:
			record=False
			pageconnections=[pc for pc in hs.page_connections.all()]
			prev_pn=None
			prev_pageconnectionid=None
			pageruns=[]
			thispagerun=[]
			for pageconnection in pageconnections:
				imagefilename=pageconnection.page.image_filename
				print(pageconnection.id,imagefilename)
				if imagefilename not in ['',None]:
					pn=int(re.search("[0-9]+(?=\.(jpg|tif))",imagefilename).group(0))
					if prev_pn is not None:
						if pn-prev_pn > 1:
							if thispagerun==[]:
								record=True
								thispagerun.append(pageconnection.id)
							else:
								pageruns.append(thispagerun)
								thispagerun=[pageconnection.id]
								
						elif record:
							thispagerun.append(pageconnection.id)
						else:
							thispagerun=[]
							record=False
					prev_pn = pn
					prev_pageconnectionid=pageconnection.id
			
			if thispagerun!=[]:
				pageruns.append(thispagerun)
			
			if pageruns!=[]:
				print(pageruns)
				sources_to_fix[hs.id]=pageruns
			print("-------")

		
		print(json.dumps(sources_to_fix,indent=2))

		# next -- we run through those sources
		# and create a new zotero source for every sub-array in the dict
		# then point the new source at it
		
		library_id=zotero_credentials['library_id']
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		
		template = zot.item_template('manuscript')
		
# 		for source_id in sources_to_fix:
# 			
# 			
# 			
# 			for pageconnection_id_list in sources_to_fix[source_id]:
				