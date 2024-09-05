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
		
		csvpath='document/management/commands/Texas_CST_2023.csv'
		formattedrows=[]
		
		library_id=zotero_credentials['library_id']
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		
		with open(csvpath,'r',encoding='utf-8-sig') as csvfile:
			reader=csv.DictReader(csvfile)
			headers={
				'VOYAGEID':'int',
				'ENSLAVEDID':'int',
				'SOURCEA':'str',
				'SOURCEB':'str',
				'URL 1':'str',
				'URL 2':'str',
				'URL 3':'str',
				'URL 4':'str',
				'URL 5':'str'
			}
			for row in reader:
				formattedrow={}
				for h in headers:
					v=row[h]
					if headers[h]=="int":
						formattedrow[h]=int(v)
					else:
						if v=='':
							formattedrow[h]=None
						else:
							formattedrow[h]=str(v)
				sourcea_shortref=re.search("[A-Z]{4}(?=,)",formattedrow["SOURCEA"]).group(0)
				#the dchr sources don't seem to be any good?
				if sourcea_shortref in ['RLMS', 'OMNO']:
					formattedrows.append(formattedrow)
		
		print(zotero_credentials)
		
		for row in formattedrows:
			voyage=Voyage.objects.get(voyage_id=row['VOYAGEID'])
			enslaved=Enslaved.objects.get(id=row['ENSLAVEDID'])
			sourcea_full_str=row['SOURCEA']
			
# 			#FORMAT NOTE: standard format is OMNO, Brazos, 3/12/1846
# 			#but for some, dd41 included the ms number like
# 			#RLMS, MS26-0367, Galveston, 10/27/1849
			try:
				sourcea_shortref,shipname_str,date_str=[i.strip() for i in sourcea_full_str.split(',')]
				ms_str=''
			except:
				sourcea_shortref,ms_str,shipname_str,date_str=[i.strip() for i in sourcea_full_str.split(',')]
			legacy_source=VoyageSources.objects.get(short_ref=sourcea_shortref)

			mm,dd,yyyy=date_str.split("/")
			zotero_title="Manifest of the %s" %shipname_str
			zotero_title=zotero_title[:240] + " " + date_str
			parseddate="-".join([str(i) for i in [yyyy,mm,dd]])


			dupcount=1
			while True:
				try:
					django_zotero_object,django_zotero_object_isnew=ZoteroSource.objects.get_or_create(
						zotero_title=zotero_title,
						legacy_source=legacy_source
					)
					break
				except:
					zotero_title += " (duplicate %d)" %dupcount
					
					dupcount+=1
			
			django_zotero_object.zotero_date=parseddate
			django_zotero_object.save()
			
			#create the zotero --> enslaved connection
			#(i'm not capturing page numbers)
			zoteroenslavedconnection,zoteroenslavedconnection_isnew=ZoteroEnslavedConnection.objects.get_or_create(
				zotero_source=django_zotero_object,
				enslaved=enslaved
			)
			
			#create the zotero --> voyage connection
			#(i'm not capturing page numbers...)
			zoterovoyageconnection,zoterovoyageconnection_isnew=ZoteroVoyageConnection.objects.get_or_create(
				zotero_source=django_zotero_object,
				voyage=voyage
			)
			
			page_url_fields=['SOURCEB','URL 1','URL 2','URL 3','URL 4','URL 5']

			page_urls=[row[i].strip() for i in page_url_fields if row[i] not in ('',None)]
			
			collectionmap={
				173891269:{'page_offset':0,'collectionstring':'lz%2Fpartnerships-0003%2F16-0922_US-NE_0001%2F0001%2F12-0888_US-MD_207%2F12-0888_US-MD_Slave-Ma-Roll-20-%28Old-Roll-3B%29-Outward-30-Oct-1828-1833%2F12-0888_US-MD_Slave-Ma-Roll-20-%28Old-Roll-3B%29-Outward-30-Oct-1828-1833_'},
				173907432:{'page_offset':0,'collectionstring':'lz%2Fpartnerships-0003%2F16-0922_US-NE_0001%2F0001%2F12-0888_US-MD_207%2F12-0888_US-MD_Slave-Manifests-Roll-21-%28Old-Roll-4A%29-Outward-1834-1837%2F12-0888_US-MD_Slave-Manifests-Roll-21-%28Old-Roll-4A%29-Outward-1834-1837_'},
				173908198:{'page_offset':0,'collectionstring':'lz%2Fpartnerships-0003%2F16-0922_US-NE_0001%2F0001%2F12-0888_US-MD_207%2F12-0888_US-MD_Slave-Manifests-Roll-22-%28Old-Roll-4B%29-Outward-1838-1840%2F12-0888_US-MD_Slave-Manifests-Roll-22-%28Old-Roll-4B%29-Outward-1838-1840_'},
				119905391:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_620303988_0004%2F32847_620303988_0004-'},
				119906086:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_620303988_0005%2F32847_620303988_0005-'},
				119899145:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0015%2F32847_1020705388_0015-'},
				119901810:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0019%2F32847_1020705388_0019-'},
				119898651:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0014%2F32847_1020705388_0014-'},
				119898146:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0013%2F32847_1020705388_0013-'},
				119899758:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0016%2F32847_1020705388_0016-'},
				119896530:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0010%2F32847_1020705388_0010-'},
				119897633:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0012%2F32847_1020705388_0012-'},
				119902449:{'page_offset':-1,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0020%2F32847_1020705388_0020-'},
				119901173:{'page_offset':-2,'collectionstring':'lz%2Fpartnerships%2F32847%2F0001%2FDD01562%2F32847_1020705388_0018%2F32847_1020705388_0018-'},
				173903848:{'page_offset':0,'collectionstring':'lz%2Fpartnerships-0003%2F16-0922_US-NE_0001%2F0001%2F12-0888_US-MD_207%2F12-0888_US-MD_Slave-Manifests--Roll-18-%28Old-Roll-2%29-Outward-1824-1827%2F12-0888_US-MD_Slave-Manifests--Roll-18-%28Old-Roll-2%29-Outward-1824-1827_'}
			}
# 
			for p in page_urls:
				is_nara='catalog.archives.gov' in p
				if is_nara:
					collection_id=int(re.search("(?<=gov/id/)[0-9]+",p).group(0))
					objectpage=int(re.search("(?<=objectPage=)[0-9]+",p).group(0))
					page_offset=collectionmap[collection_id]['page_offset']
					collectionstring=collectionmap[collection_id]['collectionstring']
					page_number_str=str(objectpage+page_offset)
					while len(page_number_str)<5:
						page_number_str="0"+page_number_str
					iiif_baseimage_url="https://catalog.archives.gov/iiif/3/%s%s.jpg/full/max/0/default.jpg" %(
						collectionstring,
						page_number_str
					)
				else:
					iiif_baseimage_url=None
	
				print(row)
				sp,sp_isnew=SourcePage.objects.get_or_create(
					page_url=p,
					iiif_baseimage_url=iiif_baseimage_url
				)
				print(sp,django_zotero_object)
				print(sp.id,sp)
				print(django_zotero_object.id,django_zotero_object)
				spc,spc_isnew=SourcePageConnection.objects.get_or_create(
					zotero_source=django_zotero_object,
					source_page=sp
				)

				print(spc.id,spc)
				if len(page_urls)>0:
					first_page_url=page_urls[0]
				else:
					first_page_url=""

				if django_zotero_object.zotero_url in ("",None):
					template = zot.item_template('manuscript')
					template['itemType'] = "Manuscript"
					template['title'] = zotero_title
					template['date'] = parseddate
					template['shortTitle']=sourcea_shortref
					template['url']=first_page_url
					if sourcea_shortref=="OMNO":
						template["archive"]="National Archives and Records Administration, (Washington DC, USA)"
						template["archiveLocation"]="Records of the United States Customs Service (Record Group 36)"
						template["libraryCatalog"]="Slave Manifests of Coastwise Vessels Filed at New Orleans, Louisiana, 1807-1860, Outward Series"
						template["callNumber"]="Microform M1895, RG 36"
					if sourcea_shortref=="RLMS":
						template["archive"]="Rosenberg Library (Galveston, TX, USA)"
						template["archiveLocation"]="Galveston & Texas History Center"
						template["libraryCatalog"]="Manifests of Slaves"
						template["callNumber"]=ms_str
					resp = zot.create_items([template])
					zotero_url=resp['successful']['0']['links']['self']['href']
					print(zotero_url)
					django_zotero_object.zotero_url=zotero_url
					django_zotero_object.save()
					print(resp)