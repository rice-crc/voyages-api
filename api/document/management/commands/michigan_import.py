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

class Command(BaseCommand):
	help = 'imports michigan collections -- purpose-built'
	def handle(self, *args, **options):
				
		collection_manifests=michigan_collection_manifests
		
		library_id=zotero_credentials['library_id']
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		#hard-coding the item creation
		michigan_legacy_refs=[
			{
				"short_ref":"AP Clement 43",
				"full_ref":"Asiento Papers, v. 43, Clements"
			},
			{
				"short_ref":"AP Clement 44",
				"full_ref":"Asiento Papers, v. 44, Clements"
			}
		]
		source_type,source_type_isnew=VoyageSourcesType.objects.get_or_create(
			group_name="Manuscript"
		)
		
		for mlr in michigan_legacy_refs:
			try:
				vs=VoyageSources.objects.get(short_ref=mlr['short_ref'])
				vs.full_ref=mlr['full_ref']
				vs.short_ref=mlr['short_ref']
				vs.save()
			except:
				VoyageSources.objects.create(
					short_ref=mlr['short_ref'],
					full_ref=mlr['full_ref'],
					source_type=source_type
				)
		
		for cmu in collection_manifests:
			url=cmu['url']
			short_ref=cmu['short_ref']
			collection_page_req=requests.get(url)
			tree=json.loads(collection_page_req.text)
			
			metadatadict={
				m['label']:m['value'] for m in tree['metadata']
			}
			
			
			
			legacy_source,legacy_source_isnew=VoyageSources.objects.get_or_create(
				short_ref=short_ref,
				source_type=source_type
			)
			print("-------------------------------",legacy_source)
			
			
			for doc in tree['structures']:
				doc_title=doc['label']
				print(doc_title)
				iiif_base_urls=[re.sub("/canvas.*","",u) for u in doc['canvases']]
# 				print(iiif_base_urls)
# 				template = zot.item_template('book')
				template = zot.item_template('manuscript')
# 				print(template)
				template['itemType'] = "Manuscript"
				template['title'] = doc_title
				template['shortTitle']=short_ref
				template['url']=iiif_base_urls[0]+"/info.json"
# 				template["archive"]=cmu['archive']
# 				template["series"]=metadatadict["Series"]
# 				template["libraryCatalog"]=metadatadict["Collection"]



				django_zotero_object,django_zotero_object_isnew=ZoteroSource.objects.get_or_create(
					zotero_title=doc_title[:250],
					legacy_source=legacy_source
				)

				
				dzurl=django_zotero_object.zotero_url




				if dzurl not in ('',None):
					item_id=re.search("(?<=items/)[A-Z|0-9]+",dzurl).group(0)
					try:
						resp=zot.item(item_id)
						zotero_item_exists=True
						print("zotero item exists:",item_id)
					except:
						zotero_item_exists=False
				else:
					zotero_item_exists=False
				
				if not zotero_item_exists:
					resp = zot.create_items([template])
					zotero_url=resp['successful']['0']['links']['self']['href']
					django_zotero_object.zotero_url=zotero_url
					django_zotero_object.save()
					print("created zotero object:",zotero_url)
				
				
				for iu in iiif_base_urls:
					sp,sp_isnew=SourcePage.objects.get_or_create(
						page_url=iu+"/info.json",
						iiif_baseimage_url=iu+"/full/max/0/default.jpg"
					)
					
					print(sp,django_zotero_object)
					print(sp.id,sp)
					print(django_zotero_object.id,django_zotero_object)
					spc,spc_isnew=SourcePageConnection.objects.get_or_create(
						zotero_source=django_zotero_object,
						source_page=sp
					)
# 			
