import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from voyage.models import *
from voyages3.settings import *
import requests
import json
import time
import os

class Command(BaseCommand):
	'''
		DO NOT RUN THIS. IT IS A ONE-TIME JOB THAT HAS BEEN COMPLETED.
		ALL OUR SOURCES NOW LIVE IN ZOTERO.
		I AM TEMPTED TO DELETE IT!
	'''
	def handle(self, *args, **options):
	
		library_id=zotero_credentials['library_id']
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		#the below is provisional. my best guess...
		legacy_source_zotero_itemtype_map={
			"Documentary source":"document",
			"Newspaper":"newspaperArticle",
			"Published source":"book",
			"Unpublished secondary source":"book",
			"Manuscript":"manuscript",
			"Private note or collection":"manuscript"
		}

		legacysources=VoyageSources.objects.all()
		zoterosources=ZoteroSource.objects.all()		
# 		
# 		#1. sweep through the existing zotero sources
# 		#and see if there are any that
# 		##A. have been linked to legacy sources but
# 		##B. do not have a short ref entry of their own
# 		###--> if so, apply it
# 		# it probably makes sense to apply the other ssc & texas doc import scripts first, then to run this
# 		# and later we can tear down the legacy sources
# 		for zs in zoterosources:
# 			if zs.short_ref in [None,''] and zs.legacy_source is not None:
# 				zs.short_ref=zs.legacy_source.short_ref
# 				zs.save()
# 				print("updated",zs,zs.short_ref)
# 		
# 		#2. apply the legacy sources over to the matching zotero sources
# 		already_migrated_legacy_sources_count=0
# 		for ls in legacysources:
# 			shortref=ls.short_ref
# 			matching_zoterosources = zoterosources.filter(short_ref=shortref)
# 			mzsc=matching_zoterosources.count()
# 			item_type=ls.source_type.group_name
# 			full_ref=ls.full_ref
# 			zotero_title=full_ref[:250]
# 			zotero_template_name=legacy_source_zotero_itemtype_map[item_type]
# 			## if it's one of our new (ssc & texas so far) docs, the legacy source will be split out into its component parts. Log that and move on.
# 			if mzsc > 1:
# 				print("multiple hits --> ",mzsc,"zotero sources matching",ls.short_ref)
# 			elif mzsc==0:
# 				print("---\nlegacy source does not exist in zotero sources. creating",shortref)
# 				template = zot.item_template(zotero_template_name)
# 				template['title']=zotero_title
# 				template['shortTitle']=shortref
# 				template['abstractNote']=full_ref
# # 				print(template)
# 				resp = zot.create_items([template])
# # 				print(resp)
# 				zotero_url=resp['successful']['0']['links']['self']['href']
# 				
# 				newzs=ZoteroSource.objects.create(
# 					short_ref=shortref,
# 					legacy_source=ls,
# 					zotero_url=zotero_url,
# 					zotero_title=zotero_title,
# 					is_legacy_source=True
# 				)
# 				
# 				newzs.save()
# 				print("created",newzs,"\n---")
# 			elif mzsc==1:
# 				already_migrated_legacy_sources_count+=1
# 		
# 		print("already migrated",already_migrated_legacy_sources_count,"legacy sources")
# 		
# 		#now walk through it one more time and map the voyage source connections.
# 		migrated_legacy_sources=ZoteroSource.objects.all().filter(is_legacy_source=True)
# 		
# 		for mls in migrated_legacy_sources:
# 			print(mls)
# 			legacy_voyagesourceconnections=mls.legacy_source.source.all()
# 			for lvsc in legacy_voyagesourceconnections:
# 				voyage=lvsc.group
# 				text_ref=lvsc.text_ref
# 				
# 				zvc,zvc_isnew=ZoteroVoyageConnection.objects.get_or_create(
# 					zotero_source=mls,
# 					voyage=voyage,
# 					page_range=text_ref
# 				)
# 				if zvc_isnew:
# 					print("*",text_ref,"-->",voyage)






# 		THIS WILL TECHNICALLY WORK, BUT IT ABSOLUTELY SLAMS IMNO, FO84, and SLNALAR
		# BECAUSE THOSE HAVEN'T BEEN SEGMENTED
		# SO LET'S SEGMENT THEM!! ----- BUT UNTIL WE DO, I'M NOT GOING TO RUN THIS.
# 		enslavedsourceconnections=EnslavedSourceConnection.objects.all()
# 		for esc in enslavedsourceconnections:
# 			try:
# 				zs=ZoteroSource.objects.get(legacy_source=esc.source)
# 				zsc,zsc_isnew=ZoteroEnslavedConnection.objects.get_or_create(
# 					enslaved=esc.enslaved,
# 					page_range=esc.text_ref,
# 					zotero_source=zs
# 				)
# 				if zsc_isnew:
# 					print("*",esc.text_ref,"-->",esc)
# 			except:
# 				
# 				
# 				time.sleep(1)
# 				print("MULTIPLE HITS-->",ZoteroSource.objects.get(legacy_source=esc.source))
# 		
# 		enslaversourceconnections=EnslaverIdentitySourceConnection.objects.all()
# 		for esc in enslaversourceconnections:
# 			try:
# 				zs=ZoteroSource.objects.get(legacy_source=esc.source)
# 				zsc,zsc_isnew=ZoteroEnslaverConnection.objects.get_or_create(
# 					enslaver=esc.identity,
# 					page_range=esc.text_ref,
# 					zotero_source=zs
# 				)
# 				if zsc_isnew:
# 					print("*",esc.text_ref,"-->",esc)
# 			except:
# 				time.sleep(1)
# 				print("MULTIPLE HITS-->",ZoteroSource.objects.get(legacy_source=esc.source))