import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from voyage.models import *
from SSC.settings import *
import requests
import json

class Command(BaseCommand):
	help = 'imports michigan collections -- purpose-built'
	def handle(self, *args, **options):
		
		THIS WAS WRITTEN FOR A DIFFERENT, STANDALONE VERSION OF THE DOCS APP. UPDATE IT BEFORE RUNNING.
		
# 
# 		
# 		
# 		collection_manifests=michigan_collection_manifests
# 		
# 		library_id=zotero_credentials['library_id']
# 		library_type=zotero_credentials['library_type']
# 		api_key=zotero_credentials['api_key']
# 		zot = zotero.Zotero(library_id, library_type, api_key)
# 		
# 		for cmu in collection_manifests:
# 			url=cmu['url']
# 			short_ref=cmu['short_ref']
# 			collection_page_req=requests.get(url)
# 			tree=json.loads(collection_page_req.text)
# 			
# 			metadatadict={
# 				m['label']:m['value'] for m in tree['metadata']
# 			}
# 			
# 			legacy_source=LegacySource.objects.get(short_ref=short_ref)
# 			print(legacy_source)
# 			
# 			
# 			for doc in tree['structures']:
# 				doc_title=doc['label']
# 				print(doc_title)
# 				iiif_base_urls=[re.sub("/canvas.*","",u) for u in doc['canvases']]
# # 				print(iiif_base_urls)
# # 				template = zot.item_template('book')
# 				template={
# 					'itemType': 'book',
# 					'title': '',
# 					'creators': [
# 						{
# 							'creatorType': 'author',
# 							'firstName': '',
# 							'lastName': ''
# 						}
# 					],
# 					'abstractNote': '',
# 					'series': '',
# 					'seriesNumber': '',
# 					'volume': '',
# 					'numberOfVolumes': '',
# 					'edition': '',
# 					'place': '',
# 					'publisher': '',
# 					'date': '',
# 					'numPages': '',
# 					'language': '',
# 					'ISBN': '',
# 					'shortTitle': '',
# 					'url': '',
# 					'accessDate': '',
# 					'archive': '',
# 					'archiveLocation': '',
# 					'libraryCatalog': '',
# 					'callNumber': '',
# 					'rights': '',
# 					'extra': '',
# 					'tags': [],
# 					'collections': [],
# 					'relations': {}
# 				}
# # 				print(template)
# 				template['itemType'] = "Manuscript"
# 				template['title'] = doc_title
# 				template['shortTitle']=short_ref
# 				template['url']=iiif_base_urls[0]+"/info.json"
# # 				template["archive"]=cmu['archive']
# # 				template["series"]=metadatadict["Series"]
# # 				template["libraryCatalog"]=metadatadict["Collection"]
# # 				print(template)
# 				django_zotero_object,django_zotero_object_isnew=ZoteroSource.objects.get_or_create(
# 					legacy_source=legacy_source,
# # 					zotero_date=parseddate,
# 					zotero_title=doc_title
# 				)
# 				resp = zot.create_items([template])
# 				zotero_url=resp['successful']['0']['links']['self']['href']
# 				print("--->",zotero_url)
# 				django_zotero_object.zotero_url=zotero_url
# 				django_zotero_object.save()
# 				print(django_zotero_object)
# 				
# 				for iu in iiif_base_urls:
# 					sp,sp_isnew=SourcePage.objects.get_or_create(
# 						item_url=iu+"/info.json",
# 						iiif_baseimage_url=iu+"/full/max/0/default.jpg"
# 					)
# 					
# 					print(sp,django_zotero_object)
# 					print(sp.id,sp)
# 					print(django_zotero_object.id,django_zotero_object)
# 					spc,spc_isnew=SourcePageConnection.objects.get_or_create(
# 						zotero_source=django_zotero_object,
# 						source_page=sp
# 					)
# 			
