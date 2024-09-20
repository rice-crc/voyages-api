import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import *
from document.models import *
from past.models import *
from voyage.models import *
from voyages3.settings import *
import requests
import json
import os
import time

class Command(BaseCommand):
	help = 'IMNO sources -- purpose-built'
	def handle(self, *args, **options):
		
		library_id='5290782'
		grouplibrary_name='IMNO_split'
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)
		omno_sources=Source.objects.all().filter(short_ref__name='OMNO')
		csvfilepath="document/management/commands/ok_data_minimal.csv"
		
		imnoshortref=ShortRef.objects.get(name="IMNO")
		opnashortref=ShortRef.objects.get(name="OPNA")
		
		with open(csvfilepath,'r') as csvfile:
			reader=csv.DictReader(csvfile)
			
			for row in reader:
				Uniqueid=int(row['\ufeffUniqueid'].strip())
				SourceA=row['SourceA'].strip()
				ShortrefA=row['ShortrefA'].strip()
				SourceB=row['SourceB'].strip()
				ShortrefB=row['ShortrefB'].strip()
				NameOwnerEmployer=row['NameOwnerEmployer'].strip()
				ShipperName=row['ShipperName'].strip()
				ConsignorName=row['ConsignorName'].strip()
				SellerName=row['SellerName'].strip()
				BuyerName=row['BuyerName'].strip()
				VoyageID=int(row['VoyageID'])
				
				skipthis=False
				try:
					enslavedperson=Enslaved.objects.get(enslaved_id=Uniqueid)
				except ObjectDoesNotExist:
					skipthis=True
					print("skipping. could not find enslaved id",Uniqueid)
				
				try:
					voyage=Voyage.objects.get(voyage_id=VoyageID)
				except ObjectDoesNotExist:
					skipthis=True
					print("skipping. could not find voyage_id",VoyageID)
				if not skipthis:
					if ShortrefA=="IMNO":
				
						pre_existing_source_connections=SourceVoyageConnection.objects.filter(
							source__short_ref__name='IMNO',
							voyage_id=VoyageID
						)
						pre_existing_source_connections.delete()
					
						try:
							date=re.search("[0-9]*\-[0-9]*\-[0-9]*",SourceA).group(0)
						except:
# 							print(SourceA)
							date='--'
						
						title=re.sub("IMNO,* *","Manifest of the ",SourceA)
						
						
						SourceA_obj,sourcea_isnew=Source.objects.get_or_create(
							title=title,
							short_ref=imnoshortref
						)
					

						if sourcea_isnew:
						
							mm,dd,yyyy=[int(i.strip()) if i.strip() not in [None,''] else None for i in date.split('-')]
						
							mm_str,dd_str,yyyy_str=[i.strip() if i.strip() not in [None,''] else '' for i in date.split('-')]
						
							datestr="%s-%s-%s" %(yyyy_str,mm_str,dd_str)
					
							template = zot.item_template('manuscript')
							template['itemType'] = "Manuscript"
							template['title'] = title
							template['language']='en-US'
							template['date'] = datestr
							template['shortTitle']="IMNO"
							template["archive"]="National Archives and Records Administration (Washington DC, USA)"
							template["archiveLocation"]="Records of the United States Customs Service (Record Group 36), Slave Manifests of Coastwise Vessels Filed at New Orleans, Louisiana, 1807-1860, Inward Series, v. Microfilm Serial M1895, RG 36"
					
							while True:
								try:
									resp = zot.create_items([template])
									break
								except:
									time.sleep(10)
					
							try:
								zotero_url=resp['successful']['0']['links']['self']['href']
								print(zotero_url)
							except:
								print("error with zotero call")
								print(resp)
								exit()
					
							group_id=int(re.search("(?<=groups/)[0-9]+",zotero_url).group(0))
							item_id=re.search("(?<=items/)[A-Z|0-9]+",zotero_url).group(0)


							if not (mm is None and yyyy is None and dd is None):
								docsparsedate=DocSparseDate.objects.create(
									month=mm,
									day=dd,
									year=yyyy
								)
							else:
								docsparsedate=None
							
							
							SourceA_obj.zotero_group_id=group_id
							SourceA_obj.zotero_item_id=item_id
							SourceA_obj.date=docsparsedate
							SourceA_obj.save()
					
						SourceVoyageConnection.objects.get_or_create(
							source=SourceA_obj,
							voyage_id=VoyageID
						)
					
					#enslavement relation connections
					
					if ShipperName not in [None,'']:
						
						existing_transportation_relations=EnslavementRelation.objects.filter(
							enslaved_in_relation__enslaved__enslaved_id=Uniqueid,
							relation_enslavers__enslaver_alias__alias=ShipperName,
							relation_enslavers__roles__name='Shipper'
						)
						
						if existing_transportation_relations.count()==0:
							print("SHIPPER --- bad relation on row ",row)
							exit()
						elif existing_transportation_relations.count()>1:
							print("-------\nSHIPPER --- multiple relations",row)
							for tr in existing_transportation_relations:
								print(tr.__dict__)
							print("-------")
						else:
							SourceEnslavementRelationConnection.objects.get_or_create(
								source=SourceA_obj,
								enslavement_relation=existing_transportation_relations[0]
							)
							enslaver_identity=EnslaverIdentity.objects.filter(
								aliases__enslaver_relations__roles__name='Shipper',
								aliases__enslaver_relations__relation=existing_transportation_relations[0]
							)
							if len(enslaver_identity)==1:
								SourceEnslaverConnection.objects.get_or_create(
									source=SourceA_obj,
									enslaver=enslaver_identity[0]
								)

					if ConsignorName not in [None,'']:
						
						existing_transportation_relations=EnslavementRelation.objects.filter(
							enslaved_in_relation__enslaved__enslaved_id=Uniqueid,
							relation_enslavers__enslaver_alias__alias=ConsignorName,
							relation_enslavers__roles__name='Consignor'
						)
						
						if existing_transportation_relations.count()==0:
							print("CONSIGNOR --- bad relation on row ",row)
							exit()
						elif existing_transportation_relations.count()>1:
							print("-------\nCONSIGNOR --- multiple relations",row)
							for tr in existing_transportation_relations:
								print(tr.__dict__)
							print("-------")
						else:
							SourceEnslavementRelationConnection.objects.get_or_create(
								source=SourceA_obj,
								enslavement_relation=existing_transportation_relations[0]
							)

							enslaver_identity=EnslaverIdentity.objects.filter(
								aliases__enslaver_relations__roles__name='Consignor',
								aliases__enslaver_relations__relation=existing_transportation_relations[0]
							)
							if len(enslaver_identity)==1:
								SourceEnslaverConnection.objects.get_or_create(
									source=SourceA_obj,
									enslaver=enslaver_identity[0]
								)
							
					if NameOwnerEmployer not in [None,'']:
						
						existing_ownership_relations=EnslavementRelation.objects.filter(
							enslaved_in_relation__enslaved__enslaved_id=Uniqueid,
							relation_enslavers__enslaver_alias__alias=NameOwnerEmployer,
							relation_enslavers__roles__name='Owner'
						)
					
						if existing_ownership_relations.count()==0:
							print("OWNER --- bad relation on row ",row)
						elif existing_ownership_relations.count()>1:
							print("-------\nmultiple relations",NameOwnerEmployer,row)
							for ownership_relation in existing_ownership_relations:
								print(ownership_relation.__dict__)
							print("-------")
						else:
							SourceEnslavementRelationConnection.objects.get_or_create(
								source=SourceA_obj,
								enslavement_relation=existing_transportation_relations[0]
							)
							print(existing_transportation_relations[0].relation_enslavers.all()[0].enslaver_alias.identity)
							enslaver_identity=EnslaverIdentity.objects.filter(
								aliases__enslaver_relations__roles__name='Owner',
								aliases__enslaver_relations__relation=existing_transportation_relations[0]
							)
							if len(enslaver_identity)==1:
								SourceEnslaverConnection.objects.get_or_create(
									source=SourceA_obj,
									enslaver=enslaver_identity[0]
								)
							
					
						SourceEnslavedConnection.objects.get_or_create(
							enslaved=enslavedperson,
							source=SourceA_obj
						)
					
					
					elif ShortrefB=="OPNA":
				
						pre_existing_source_connections=SourceVoyageConnection.objects.filter(
							source__short_ref__name='OPNA',
							voyage_id=VoyageID
						)
# 						pre_existing_source_connections.delete()
					
						try:
							date=re.search("[0-9]{4}",SourceB).group(0)
						except:
# 							print(SourceB)
							date=None
						
						title=re.sub("OPNA,* *","",SourceB)
						
						SourceB_obj,sourceb_isnew=Source.objects.get_or_create(
							title=title,
							short_ref=opnashortref
						)
					
						if sourceb_isnew:

							template = zot.item_template('manuscript')
							template['itemType'] = "Manuscript"
							template['title'] = title
							if date is not None:
								template['date'] = date
							template['language']='en-US'
							template['shortTitle']="OPNA"
							template["archive"]="Orleans Parish Notarial Archive (New Orleans, US)"
					
							while True:
								try:
									resp = zot.create_items([template])
									break
								except:
									time.sleep(10)
					
							try:
								zotero_url=resp['successful']['0']['links']['self']['href']
								print(zotero_url)
							except:
								print("error with zotero call")
								print(resp)
								exit()
					
							group_id=int(re.search("(?<=groups/)[0-9]+",zotero_url).group(0))
							item_id=re.search("(?<=items/)[A-Z|0-9]+",zotero_url).group(0)
							
							if date is not None:
								docsparsedate=DocSparseDate.objects.create(
									year=int(yyyy)
								)
							else:
								docsparsedate=None
						
							SourceB_obj.zotero_group_id=group_id
							SourceB_obj.zotero_item_id=item_id
							SourceB_obj.date=docsparsedate
							SourceB_obj.save()
					
						SourceVoyageConnection.objects.get_or_create(
							source=SourceB_obj,
							voyage_id=VoyageID
						)
					
						#enslavement relation connections
										
						if SellerName not in [None,'']:
						
							existing_ownership_relations=EnslavementRelation.objects.filter(
								enslaved_in_relation__enslaved__enslaved_id=Uniqueid,
								relation_enslavers__enslaver_alias__alias=SellerName,
								relation_enslavers__roles__name='Seller'
							)
					
							if existing_ownership_relations.count()==0:
								print("SELLER --- bad relation on row ",row)
							elif existing_ownership_relations.count()>1:
								print("-------\nmultiple relations",SellerName,row)
								for ownership_relation in existing_ownership_relations:
									print(ownership_relation.__dict__)
								print("-------")
							else:
								SourceEnslavementRelationConnection.objects.get_or_create(
									source=SourceB_obj,
									enslavement_relation=existing_transportation_relations[0]
								)
								enslaver_identity=EnslaverIdentity.objects.filter(
									aliases__enslaver_relations__roles__name='Seller',
									aliases__enslaver_relations__relation=existing_transportation_relations[0]
								)
								if len(enslaver_identity)==1:
									SourceEnslaverConnection.objects.get_or_create(
										source=SourceB_obj,
										enslaver=enslaver_identity[0]
									)

						if BuyerName not in [None,'']:
							existing_ownership_relations=EnslavementRelation.objects.filter(
								enslaved_in_relation__enslaved__enslaved_id=Uniqueid,
								relation_enslavers__enslaver_alias__alias=BuyerName,
								relation_enslavers__roles__name='Buyer'
							)
					
							if existing_ownership_relations.count()==0:
								print("SELLER --- bad relation on row ",row)
							elif existing_ownership_relations.count()>1:
								print("-------\nmultiple relations",BuyerName,row)
								for ownership_relation in existing_ownership_relations:
									print(ownership_relation.__dict__)
								print("-------")
							else:
								SourceEnslavementRelationConnection.objects.get_or_create(
									source=SourceB_obj,
									enslavement_relation=existing_transportation_relations[0]
								)
								enslaver_identity=EnslaverIdentity.objects.filter(
									aliases__enslaver_relations__roles__name='Buyer',
									aliases__enslaver_relations__relation=existing_transportation_relations[0]
								)
								if len(enslaver_identity)==1:
									SourceEnslaverConnection.objects.get_or_create(
										source=SourceB_obj,
										enslaver=enslaver_identity[0]
									)


					
					
						print(enslavedperson,SourceB_obj)
						SourceEnslavedConnection.objects.get_or_create(
							enslaved=enslavedperson,
							source=SourceB_obj
						)
