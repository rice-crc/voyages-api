from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from document.models import *
from xml.etree import ElementTree
import json
import re
import requests
#adding in authorization and urls from localsettings
from voyages3.localsettings import zotero_credentials
from voyages3.settings import STATIC_ROOT
from pyzotero import zotero
import time
from voyage.models import *

class Command(BaseCommand):
	help = """\
		The ROAD team's document pairing app, which allows users to quickly run through \
		IIIF manifests and segment them while tagging existing voyages, is yielding its \
		first results. The outputs are json files that link image urls with voyage id's. \
		This walks those pairings and creates the connections to the existing voyages, \
		then identifies whether those voyage also connect to enslaved people and \
		enslavers, and establishes those connections as well. You must target a shortref \
		in order that voyages with multiple sources have a better chance of this indexed \
		source being lined up properly with the source being specified in the pairs.json \
		file. The script will not treat voyages that do not have a pre-existing source \
		that meets the match conditions.\
	"""
	
	def add_arguments(self, parser):
		parser.add_argument("--shortref", default=None)

	def handle(self, *args, **options):
		shortref=options['shortref']
		if not shortref:
			print("you must specify a shortref.")
			exit()
		shortref_obj=ShortRef.objects.get(name=shortref)
		
		library_id=5290782
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		template = zot.item_template('manuscript')
		source_type=SourceType.objects.get(name="Manuscript")
		
		d=open("document/management/commands/data/pairs.json","r")
		t=d.read()
		d.close()
		raw_pairings=json.loads(t)
		voyage_image_pairings={}
		img_count=0
		catalogue_ids=[]
		#roll up the pairings into a voyage-keyed dictionary
		for rp in raw_pairings:
			voyage_id=rp['voyage_id']
			image_url=rp['image_url']
			#quite often the images indexed are not the full-size ones. fix that.
			clean_image_url=re.sub("/[^/]+?/[^/]+?/[^/]+?/[^/]+?$","/full/max/0/default.jpg",image_url)
			#let's validate that all these voyages exist before we go any further.
# 			voyage=Voyage.objects.get(voyage_id=voyage_id)
			catalogue=rp['catalog_name']
			
			if catalogue not in catalogue_ids:
				catalogue_ids.append(catalogue)
			
			if voyage_id not in voyage_image_pairings:
				voyage_image_pairings[voyage_id]={catalogue:[clean_image_url]}
			else:
				if catalogue in voyage_image_pairings[voyage_id]:
					voyage_image_pairings[voyage_id][catalogue].append(clean_image_url)
				else:
					voyage_image_pairings[voyage_id][catalogue]=[clean_image_url]
			if voyage_id not in voyage_image_pairings:
				voyage_image_pairings[voyage_id]=[clean_image_url]
			else:
				voyage_image_pairings[voyage_id][catalogue].append(clean_image_url)
			img_count+=1
		
		print(f"This json file pairs {img_count} images to {len(voyage_image_pairings)} voyages across {len(catalogue_ids)} catalogues.")
		print(f"catalogues: {catalogue_ids}")
		
		c=0
		for voyage_id in voyage_image_pairings:
			voyage=Voyage.objects.get(voyage_id=voyage_id)
			source_connections=voyage.voyage_source_connections.all()
			source_connections=source_connections.filter(source__short_ref__name__exact=shortref)
			sources=[sc.source for sc in source_connections]
			
			print(voyage,f'has {len(sources)} sources')
			
			for catalogue in voyage_image_pairings[voyage_id]:
				
				if len(sources)==0:
					print("-->creating source")
					d=open("document/management/commands/data/catalogue_names.json","r")
					t=d.read()
					d.close()
					catalogues_index=json.loads(t)
					catalogue_data=catalogues_index[catalogue]
					
					template['archive']=catalogue_data['Archive']
					template['archiveLocation']=catalogue_data['Loc. in Archive']
					template['shortTitle']=catalogue_data['Short Title']
					template['url']=catalogue_data['Collection URL']
					
					ship_name=voyage.voyage_ship.ship_name
					if ship_name in ['',None]:
						ship_name="[vessel name unspecified]"
					
					voyage_dates=voyage.voyage_dates
					vd=voyage_dates.first_dis_of_slaves_sparsedate
					if vd is None:
						vd=voyage_dates.slave_purchase_began_sparsedate
					if vd is None:
						vd=voyage_dates.vessel_left_port_sparsedate
						
					y=vd.year
					ystr=y or ''
					m=vd.month
					mstr=m or ''
					d=vd.day
					dstr=d or ''
					
					titledatestr=f'{mstr}-{dstr}-{ystr}'
					
					zoterodatestr=f'{ystr}-{mstr}-{dstr}'
					
					title=f'Manifest of the {ship_name}, {zoterodatestr}'
					
					template['title']=title
					
					template['date']=zoterodatestr
					
					while True:
						resp = zot.create_items([template])
						if resp['successful']:
							break
						else:
							print("FAILED")
							time.sleep(5)
					
					zotero_item=resp['successful']['0']
					zotero_item_id=zotero_item['key']
					zotero_url=zotero_item['links']['alternate']['href']
					
					#get bib entry
					errors=0
					cutoff=5
					while True:
						res = requests.get( \
						f"https://api.zotero.org/groups/{library_id}/items/{zotero_item_id}?format=json&include=bib&style=chicago-fullnote-bibliography", \
						headers={ 'Authorization': f"Bearer {api_key}" }, \
						timeout=60)
						
						if res.status_code==200:
							break
						else:
							print("Error")
							errors+=1
							time.sleep(5)
							if errors>cutoff:
								failure=True
								print("SKIPPING",source.title)
					
					item = res.json()
					bib=item['bib']
					
					source_date=DocSparseDate.objects.create(
						year=y,
						month=m,
						day=d
					)
					
					source=Source.objects.create(
						title=title,
						zotero_group_id=library_id,
						zotero_item_id=zotero_item_id,
						short_ref=shortref_obj,
						zotero_grouplibrary_name=shortref,
						zotero_url=zotero_url,
						date=source_date,
						source_type=source_type,
						bib=bib
					)
				
				else:
					source=sources[0]
					
				SourceVoyageConnection.objects.create(
					source=source,
					voyage=voyage
				)
				
				enslavementrelations=voyage.voyage_enslavement_relations.all()
				
				enslaved_ids=[i[0] for i in list(set(enslavementrelations.values_list('enslaved_in_relation__enslaved__id'))) if i[0] is not None]
				
				enslaver_ids=[i[0] for i in list(set(enslavementrelations.values_list('relation_enslavers__enslaver_alias__identity__id'))) if i[0] is not None]
				
# 				print(enslaved_ids)
# 				print(enslaver_ids)
				
				for enslaved_id in enslaved_ids:
					enslaved=Enslaved.objects.get(id=enslaved_id)
					SourceEnslavedConnection.objects.create(
						source=source,
						enslaved=enslaved
					)
					
				
				for enslaver_id in enslaver_ids:
					enslaver=EnslaverIdentity.objects.get(id=enslaver_id)
					SourceEnslaverConnection.objects.create(
						source=source,
						enslaver=enslaver
					)
				
				for page_image_url in voyage_image_pairings[voyage_id][catalogue]:
					
					page=Page.objects.create(
						iiif_baseimage_url=page_image_url
					)
					
					SourcePageConnection.objects.create(
						page=page,
						source=source
					)
				
				
					
					
					
# 					
						
					
					## if it's one of our new (ssc & texas so far) docs, the legacy source will be split out into its component parts. Log that and move on.
# 					if mzsc > 1:
# 						print("multiple hits --> ",mzsc,"zotero sources matching",ls.short_ref)
# 					elif mzsc==0:
# 						print("---\nlegacy source does not exist in zotero sources. creating",shortref)
# 						template = zot.item_template(zotero_template_name)
# 						template['title']=zotero_title
# 						template['shortTitle']=shortref
# 						template['abstractNote']=full_ref
# 		# 				print(template)
# 						resp = zot.create_items([template])
# 		# 				print(resp)
# 						zotero_url=resp['successful']['0']['links']['self']['href']
# 						
# 						newzs=ZoteroSource.objects.create(
# 							short_ref=shortref,
# 							legacy_source=ls,
# 							zotero_url=zotero_url,
# 							zotero_title=zotero_title,
# 							is_legacy_source=True
# 						)
					
					
# 					print(catalogue_data)
						
# 						
# 						voyage_image_pairings={}
# 
# 				
# 					c+=1	
# 					try:
# 						print(vd.year,vd.month,vd.day)
# 					except:
# 						print(voyage_dates.__dict__)
# 						exit()
		print(c)

				
		
		
		
		
		
		
# 		
# 		
# 		
# 		
# 		
# 		
# 		
# 		
# 		
# 		library_id=zotero_credentials['library_id']
# 		library_type=zotero_credentials['library_type']
# 		api_key=zotero_credentials['api_key']
# 		zot = zotero.Zotero(library_id, library_type, api_key)
# 		
# 		shortref=options['shortref']
# 		
# 		sources=Source.objects.all()
# 		if shortref is not None:
# 			sources=sources.filter(short_ref__name__icontains=shortref)
# 			c=1
# 			errors=0
# 			cutoff=5
# 			for source in sources:
# 				zotero_item_id=source.zotero_item_id
# 				failure=False
# 				while True:
# 					res = requests.get( \
# 					f"https://api.zotero.org/groups/{library_id}/items/{zotero_item_id}?format=json&include=bib&style=chicago-fullnote-bibliography", \
# 					headers={ 'Authorization': f"Bearer {api_key}" }, \
# 					timeout=60)
# 					
# 					if res.status_code==200:
# 						break
# 					else:
# 						print("Error")
# 						errors+=1
# 						if errors>cutoff:
# 							failure=True
# 							print("SKIPPING",source.title)
# 			
# 				if not failure:
# 					item = res.json()
# 					
# 					bib=item['bib']
# 					
# 					source.bib=bib
# 					source.save()