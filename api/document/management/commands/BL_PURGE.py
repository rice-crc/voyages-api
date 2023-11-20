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
import os

class Command(BaseCommand):
	help = 'wipes out all bl sources and pages. why? because their data and servers have been a nightmare and this is taking lots of testing, and very very bad code on my end. not fun!'
	def handle(self, *args, **options):

		bl_sources=Source.objects.all().filter(is_british_library=True)
		bl_pages=Page.objects.all().filter(is_british_library=True)
		
		print("PRE-PURGE")
		print('%d sources and %d pages tagged as BL' %(bl_sources.count(),bl_pages.count()))
		
		library_id='5288953'
		grouplibrary_name='sv_british_library'
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)

		
		
		item_ids=[i[0] for i in bl_sources.values_list('zotero_item_id')]
		print(item_ids)
		
		print(item_ids)
		for source in bl_sources:
			zot_item_id=str(source.zotero_item_id)
			try:
				item=zot.item(zot_item_id)
				zot.delete_item(item)
				print("deleted zotero item:",str(zot_item_id))
			except:
				print("item does not exist")
			source.delete()
			
		bl_pages.delete()
		bl_sources.delete()

		bl_sources=Source.objects.all().filter(is_british_library=True)
		bl_pages=Page.objects.all().filter(is_british_library=True)
		
		print("POST-PURGE")
		print('%d sources and %d pages tagged as BL' %(bl_sources.count(),bl_pages.count()))
