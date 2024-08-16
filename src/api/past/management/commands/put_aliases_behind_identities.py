import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from doc.models import *
from voyage.models import *
from voyages3.settings import *
import requests
import json
import os

# the current past organization is just awful to deal with. we need to
## 1) put aliases behind identities
## 2) attach voyages, relations, and sources directly to identities instead of aliases
## 3) route voyages through relations as a transportation relation w/ captain or shipowner role

## down the line we need to allow for multiple roles in a single relation
#### and then merge the duplicates (where the same enslaver & enslaved are connected but under different roles)

class Command(BaseCommand):
	help = 'puts aliases behind identities'
	def handle(self, *args, **options):
		aliases=EnslaverAlias.objects.all()
		for a in aliases:
			a2,a2_isnew=EnslaverAlias.objects.get_or_create(
				manual_id=a.manual_id,
				last_updated=a.last_updated,
				human_revieweda.human_reviewed,
				identity=a.identity,
				alias=a.alias
			)
		
		enslaverinrelations=EnslaverInRelation.objects.all()
		for eir in enslaverinrelations:
			eir.enslaver_identity2=eir.enslaver_alias.identity
			eir.save()
		

		

# 
# 	identity = models.ForeignKey(EnslaverIdentity, on_delete=models.CASCADE, related_name='aliases')
# 	alias = models.CharField(max_length=255)
# 
# 
# 	enslaver_alias = models.ForeignKey(
# 		EnslaverAlias,
# 		related_name="enslaver_relations",
# 		null=True,
# 		on_delete=models.CASCADE
# 	)
# 	enslaver_identity2 = models.ForeignKey(
# 		EnslaverIdentity,
# 		related_name="enslaver_relations2",
# 		null=True,
# 		on_delete=models.CASCADE
# 	)
# 
# 		
		
		
		
		# 	"""
# 	identity = models.ForeignKey(EnslaverIdentity, on_delete=models.CASCADE, related_name='aliases2')
# 	
# 	# The manual id can be used to track the original entries in sheets produced
# 	# by the researchers.
# 	manual_id = models.CharField(max_length=30, null=True)
# 	last_updated=models.DateTimeField(auto_now=True)
# 	human_reviewed=models.BooleanField(default=False,blank=True,null=True)
# 
		
		
	
	
	
		#first, enslaver aliases
		
# 		
# class EnslaverInRelation(models.Model):
# 	"""
# 	Associates an enslaver in a slave relation.
# 	"""
# 
# 	id = models.IntegerField(primary_key=True)
# 	relation = models.ForeignKey(
# 		EnslavementRelation,
# 		related_name="relation_enslavers",
# 		null=False,
# 		on_delete=models.CASCADE)
# 	enslaver_alias = models.ForeignKey(
# 		EnslaverAlias,
# 		related_name="enslaver_relations",
# 		null=True,
# 		on_delete=models.CASCADE
# 	)
# 	enslaver_identity2 = models.ForeignKey(
# 		EnslaverIdentity,
# 		related_name="enslaver_relations2",
# 		null=True,
# 		on_delete=models.CASCADE
# 	)
# 	role = models.ForeignKey(EnslaverRole, null=False, on_delete=models.CASCADE, help_text="The role of the enslaver in this relation")








# class EnslaverAlias(models.Model):
# 	"""
# 	An alias represents a name appearing in a record that is mapped to
# 	a consolidated identity. The same individual may appear in multiple
# 	records under different names (aliases).
# 	"""
# 	identity = models.ForeignKey(EnslaverIdentity, on_delete=models.CASCADE, related_name='aliases')
# 	alias = models.CharField(max_length=255)
# 	
# 	# The manual id can be used to track the original entries in sheets produced
# 	# by the researchers.
# 	manual_id = models.CharField(max_length=30, null=True)
# 	last_updated=models.DateTimeField(auto_now=True)
# 	human_reviewed=models.BooleanField(default=False,blank=True,null=True)
# 
# 	def __str__(self):
# 		return self.__unicode__()
# 
# 	def __unicode__(self):
# 		return "EnslaverAlias: " + self.alias
# 
# 	class Meta:
# 		verbose_name = 'Enslaver alias'
# 	
# ## Going to flip this relation so aliases live "behind" identities
# ## And going to scaffold all the other relations to point directly at identity
# class EnslaverAlias2(models.Model):
# 	"""
# 	An alias represents a name appearing in a record that is mapped to
# 	a consolidated identity. The same individual may appear in multiple
# 	records under different names (aliases).
# 	"""
# 	identity = models.ForeignKey(EnslaverIdentity, on_delete=models.CASCADE, related_name='aliases2')
# 	
# 	# The manual id can be used to track the original entries in sheets produced
# 	# by the researchers.
# 	manual_id = models.CharField(max_length=30, null=True)
# 	last_updated=models.DateTimeField(auto_now=True)
# 	human_reviewed=models.BooleanField(default=False,blank=True,null=True)
# 
# 	def __str__(self):
# 		return self.__unicode__()
# 
# 	def __unicode__(self):
# 		return "EnslaverAlias: " + self.alias
# 
# 	class Meta:
# 		verbose_name = 'Enslaver alias'
# 
	
		# 
# 
# 
# 
# 
# 		basepath="document/management/commands/"
# 		tsvs=[i for i in os.listdir(basepath) if "mssST" in i]
# 		
# 		library_id=zotero_credentials['library_id']
# 		library_type=zotero_credentials['library_type']
# 		api_key=zotero_credentials['api_key']
# 		zot = zotero.Zotero(library_id, library_type, api_key)
# 		
# 		template = zot.item_template('manuscript')
# 		
# 		for tsv in tsvs:
# 			fpath=os.path.join(basepath,tsv)
# 			print(fpath)
# 			with open(fpath,'r') as tsvfile:
# 				reader=csv.DictReader(tsvfile,delimiter='\t')
# # 				frontmatter=True
# # 				firstrow=True
# 				doc_title=None
# 				for row in reader:
# 					
# 					call_no=row["Call Number"]
# 					physical_collection=row["Physical Collection"]
# 					rights=row["Rights"]
# 					digital_collection=row["Digital Collection"]
# 					object_file_name=row["Object File Name"]
# 					iiif_manifest_url=row["IIIF Page Manifest Link"]
# 					iiif_page_url=row["IIIF Page Image Manifest Link"]
# 					part_of_object=row["Part of Object"]
# 					reference_url=row["Reference URL"]
# 					
# 					
# 					collection_number=re.search("(?<=mssST)\s+[0-9]+",call_no).group(0).strip()
# 					collection_volume=re.search("(?<=v\.)\s+[0-9]+",call_no).group(0).strip()
# 					
# 					if row["Description"]!="":
# 						doc_title=row["Description"]
# 						doc_date=row["Date"]
# 					
# 					full_ref=" ".join(
# 						[
# 							"Duke of Chandos Papers, msST",
# 							collection_number,
# 							collection_volume,
# 							"Huntington"
# 						]
# 					)
# 					
# 					short_ref=" ".join(
# 						[
# 							"DOCP Huntington",
# 							collection_number,
# 							collection_volume
# 						]
# 					)
# 					
# # 					doc_title=" ".join([doc_title,doc_date])
# 					
# 					template["callNumber"]=call_no
# 					template["title"]=doc_title
# 					template["libraryCatalog"]=digital_collection
# 					template["rights"]=rights
# 					template["archive"]=physical_collection
# 					template["archiveLocation"]=part_of_object
# 					template["shortTitle"]=short_ref
# 					template["url"]=reference_url
# 					template["date"]=doc_date
# 					
# 					source_type,source_type_isnew=VoyageSourcesType.objects.get_or_create(
# 						group_name="Manuscript"
# 					)
# 					
# 					legacy_source,lc_isnew=VoyageSources.objects.get_or_create(
# 						full_ref=full_ref,
# 						short_ref=short_ref,
# 						source_type=source_type
# 					)
# 					
# 					dupcount=1
# 					while True:
# 						try:
# 							django_zotero_object,django_zotero_object_isnew=ZoteroSource.objects.get_or_create(
# 								zotero_title=doc_title,
# 								legacy_source=legacy_source
# 							)
# 							break
# 						except:
# 							doc_title += " (duplicate %d)" %dupcount
# 							
# 							dupcount+=1
# 					
# 					django_zotero_object.item_url=reference_url
# 					django_zotero_object.zotero_date=doc_date
# 					django_zotero_object.save()
# 					
# 					dzurl=django_zotero_object.zotero_url
# 				
# 					if dzurl not in ('',None):
# 						item_id=re.search("(?<=items/)[A-Z|0-9]+",dzurl).group(0)
# 						try:
# 							resp=zot.item(item_id)
# 							zotero_item_exists=True
# 							print("zotero item exists:",item_id)
# 						except:
# 							zotero_item_exists=False
# 					else:
# 						zotero_item_exists=False
# 					
# 					if not zotero_item_exists:
# 						resp = zot.create_items([template])
# 						zotero_url=resp['successful']['0']['links']['self']['href']
# 						django_zotero_object.zotero_url=zotero_url
# 						django_zotero_object.save()
# 						print("created zotero object:",zotero_url)
# 					
# 					
# 					sp,sp_isnew=SourcePage.objects.get_or_create(
# 						page_url=iiif_manifest_url,
# 						iiif_baseimage_url=iiif_page_url,
# 						image_filename=object_file_name
# 					)
# 					
# 					print(sp,django_zotero_object)
# # 					print(sp.id,sp)
# # 					print(django_zotero_object.id,django_zotero_object)
# 					spc,spc_isnew=SourcePageConnection.objects.get_or_create(
# 						zotero_source=django_zotero_object,
# 						source_page=sp
# 					)