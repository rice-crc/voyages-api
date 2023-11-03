import re
from django.core.management.base import BaseCommand, CommandError
from document.models import *
import json
import os

class Command(BaseCommand):
	help = 'imports michigan collections -- purpose-built'
	def handle(self, *args, **options):

		basepath="document/management/commands/"
		tsvs=[i for i in os.listdir(basepath) if "mssST" in i]
		
		
		d=open("document/management/commands/sourcepages.json","r")
		t=d.read()
		d.close()
		sourcepages=json.loads(t)
		print("source page",sourcepages[0])
		
		
		d=open("document/management/commands/spcs.json","r")
		t=d.read()
		d.close()
		sourcepageconnections=json.loads(t)
		print("spc",sourcepageconnections[0])
		
		d=open("document/management/commands/zoterosources.json","r")
		t=d.read()
		d.close()
		zoterosources=json.loads(t)
		
		zoterosources=[zs for zs in zoterosources if zs['zotero_url'] not in [None,'']]
		
		print("zoterosource",zoterosources[0])
		
		sources=Source.objects.all()
		print("source",sources[0].__dict__)
		
		broken_out_shortrefs=[
			'OMNO',
			'RLMS',
			'DOCP Huntington 57 24',
			'DOCP Huntington 57 17',
			'DOCP Huntington 57 18',
			'DOCP Huntington 57 19',
			'DOCP Huntington 57 21',
			'AP Clement 43',
			'AP Clement 44'
		]
		
		for zs in zoterosources:
			z_id=zs['id']
			zurl=zs['zotero_url']
			zotero_group_id=re.search('(?<=groups/)[0-9]+',zurl).group(0)
			zotero_item_id=re.search('(?<=items/)[0-9|A-Z]+',zurl).group(0)
			item_url=zs['item_url']
			shortref=zs['short_ref']
			if shortref not in broken_out_shortrefs:
				corresponding_source=sources.filter(short_ref__name=shortref)
				short_ref_obj=ShortRef.objects.create(name=shortref)
				if len(corresponding_source)==0:
					source=Source.objects.create(
						item_url=zs['item_url'],
						zotero_group_id=zotero_group_id,
						zotero_item_id=zotero_item_id,
						short_ref=short_ref_obj,
						title=zs['zotero_title']
					)
				elif len(corresponding_source)==1:
					s=corresponding_source[0]
					source=Source.objects.update(
						item_url=zs['item_url'],
						zotero_group_id=zotero_group_id,
						zotero_item_id=zotero_item_id,
						short_ref=short_ref_obj
					).save()
				else:
					print("too many sources, we thought we had this covered?",shortref)
			else:
				short_ref_obj,short_ref_obj_isnew=ShortRef.objects.get_or_create(
					name=shortref
				)
				source=Source.objects.create(
					item_url=zs['item_url'],
					zotero_group_id=zotero_group_id,
					zotero_item_id=zotero_item_id,
					short_ref=short_ref_obj,
					title=zs['zotero_title']
				)
				
			source_id=source.id
			
			these_spcs = [spc for spc in sourcepageconnections if z_id==zs['id']]
			for spc in these_spcs:
				page_id=spc['source_page_id']
				id=spc['id']
				source_page=[sp for sp in sourcepages if sp['id']==page_id][0]
				page=Page.objects.create(
					page_url=source_page['page_url'],
					iiif_manifest_url=source_page['iiif_manifest_url'],
					iiif_baseimage_url=source_page['iiif_baseimage_url'],
					image_filename=source_page['image_filename'],
					transcription=source_page['transcription']
				)
				page_id=page.id
				SourcePageConnection.objects.create(
					source_id=source_id,
					page_id=page_id
				)

	
