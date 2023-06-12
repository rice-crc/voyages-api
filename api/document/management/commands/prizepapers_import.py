import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from voyage.models import *
from voyages3.settings import *

class Command(BaseCommand):
	help = 'imports dd41 csv -- purpose-built'
	def handle(self, *args, **options):
		
		csvpath='document/management/commands/prize_papers.csv'
		formattedrows=[]
		
		library_id=zotero_credentials['library_id']
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		
		with open(csvpath,'r',encoding='utf-8-sig') as csvfile:
			reader=csv.DictReader(csvfile)
			
			headers={
				'ship names':'str',
				'ship url':'str',
				'journey id':'str',
				'captains':'str',
				'place start':'str',
				'place end':'str',
				'intended ending place':'str',
				'journey type':'str',
				'sources':'list'
			}
			
			short_ref="HCA"
			
			for row in reader:
				formattedrow={}
				for h in headers:
					v=row[h]
					if headers[h]=="int":
						formattedrow[h]=int(v)
					elif headers[h]=='list':
						listitems=re.findall("(?<=\[)[^\]]+",v[1:-1])
						output=[]
						for li in listitems:
							matcher=[i.strip() for i in  re.findall("(?<=\')[^']+",li) if i.strip()!=',']
							output.append(matcher)
						formattedrow[h]=output
					else:
						if v=='':
							formattedrow[h]=None
						else:
							formattedrow[h]=str(v)
				
				formattedrows.append(formattedrow)
		print(zotero_credentials)
		
		c=0
		base_id=500000
		
		er,er_isnew=EnslaverRole.objects.get_or_create(
			name="Captain"
		)
		
		for row in formattedrows:
		
			#all their voyages (except for one) appear to be new. I will assign them ID's starting at 105000 to keep them in transatlantic.
			
			voyage,voyage_isnew=Voyage.objects.get_or_create(
				voyage_id=base_id+c,
				dataset=0,
			)
			c+=1
			
			if row['captains'] is not None:
				captain_name=re.sub(", (master|Master|Captain|captain) of.*","",row['captains'])
			else:
				captain_name=None
			
					
			try:
				date_attempt=re.search("[0-9|\-]+$",row['captains']).group(0)
			except:
				date_attempt=None
			
			if captain_name not in ('',None):
# 				captain,captain_isnew=VoyageCaptain.objects.get_or_create(name=captain_name)
				print(voyage,captain_name)
				ei,ei_isnew=EnslaverIdentity.objects.get_or_create(
					principal_alias=captain_name
				)
				
				ea,ea_isnew=EnslaverAlias.objects.get_or_create(
					identity=ei,
					alias=captain_name
				)
				
				
				evc,evc_isnew=EnslaverVoyageConnection.objects.get_or_create(
					voyage=voyage,
					enslaver_alias=ea,
					role=er
				)
				
				
				
				print(ei,ea,evc)
			
			ship_name=row['ship names']
			
			ship,ship_isnew=VoyageShip.objects.get_or_create(
				ship_name=ship_name,
				voyage=voyage
			)
			
			legacy_source=VoyageSources.objects.get(short_ref=short_ref)
			
			source=row['sources']
			
			if source!=[]:
				source=source[0]
				url,hca=source
			else:
				url=None
				hca=None
			
# 			print("------>",row['sources'],url)
			
			zotero_title="Voyage of the %s" %ship_name
		
			if date_attempt is not None:
				zotero_title+=" %s" %date_attempt
			
			if hca is not None:
				zotero_title+= " %s" %hca
			
			django_zotero_object,django_zotero_object_isnew=ZoteroSource.objects.get_or_create(
				zotero_title=zotero_title,
				legacy_source=legacy_source
			)
			
			
			django_zotero_object.item_url=url
			if date_attempt is not None:
				django_zotero_object.zotero_date=date_attempt
			
			django_zotero_object.voyages.add(voyage)
			django_zotero_object.enslavers.add(ei)
			django_zotero_object.save()
			
			
		
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
			
			
		
			if django_zotero_object.zotero_url in ("",None):
				template = zot.item_template('book')
				template['itemType'] = "Manuscript"
				template['title'] = zotero_title
				template['date'] = date_attempt
				template['shortTitle']=short_ref
				template['url']=url
				template["archive"]="British National Archives (Kew)"
				template["archiveLocation"]="London"
				resp = zot.create_items([template])
				zotero_url=resp['successful']['0']['links']['self']['href']
				print(zotero_url)
				django_zotero_object.zotero_url=zotero_url
				django_zotero_object.save()
				print(resp)
		