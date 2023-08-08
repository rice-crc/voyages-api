from django.db import models
import re

from voyage.models import VoyageSources,Voyage
from past.models import Enslaved,EnslaverIdentity

class SourcePage(models.Model):
	"""
	INDIVIDUAL PAGES
	"""
	page_url=models.URLField(max_length=400,null=True)
	iiif_manifest_url=models.URLField(null=True,blank=True,max_length=400)
	iiif_baseimage_url=models.URLField(null=True,blank=True,max_length=400)
	image_filename=models.CharField(
		max_length=100,
		null=True,
		blank=True
	)
	transcription=models.TextField(null=True,blank=True)
	last_updated=models.DateTimeField(auto_now=True)
	human_reviewed=models.BooleanField(default=False,blank=True,null=True)
		
	def __str__(self):
		nonnulls=[i for i in [
				self.page_url,
				self.iiif_manifest_url,
				self.iiif_baseimage_url
			]
			if i is not None and i != ''
		]
		if len(nonnulls)==0:
			return ''
		else:
			return nonnulls[0]
	@property
	def square_thumbnail(self):
		if self.iiif_baseimage_url not in (None,""):
# 			square_thumbnail=re.sub("/full/max/","/square/200,200/",self.iiif_baseimage_url)
			#michigan's test server can't handle square requests
			iiif_endpoint_patterns="(/full/max/)|(/full/full/)"
			square_thumbnail=re.sub(iiif_endpoint_patterns,"/full/200,/",self.iiif_baseimage_url)
			return square_thumbnail
		else:
			return None
			
class SourcePageConnection(models.Model):
	zotero_source=models.ForeignKey(
		'ZoteroSource',
		related_name='page_connection',
		on_delete=models.CASCADE
	)
	
	source_page=models.ForeignKey(
		'SourcePage',
		related_name='zotero_connection',
		on_delete=models.CASCADE
	)
	
	class Meta:
		unique_together=[
			['zotero_source','source_page']
		]




# >>> from document.models import *
# >>> zoterosources=ZoteroSource.objects.all()
# >>> for zs in zoterosources:
# ...     if zs.voyages.all() is not None:
# ...             for v in zs.voyages.all():
# ...                     zvc,zvc_isnew=ZoteroVoyageConnection.objects.get_or_create(zotero_source=zs,voyage=v)
# ...                     zvc.save()
# ... 


# >>> for zs in zoterosources:
# ...     if zs.enslaved_people.all() is not None:
# ...             for e in zs.enslaved_people.all():
# ...                     zec,zec_isnew=ZoteroEnslavedConnection.objects.get_or_create(zotero_source=zs,enslaved=e)
# ...                     zec.save()

# for zs in zoterosources:
# 	if zs.enslavers.all() is not None:
# 		for e in zs.enslavers.all():
# 			zec,zec_isnew=ZoteroEnslaverConnection.objects.get_or_create(zotero_source=zs,enslaver=e)
# 			zec.save()


class ZoteroVoyageConnection(models.Model):
	zotero_source=models.ForeignKey(
		'ZoteroSource',
		related_name='zotero_voyage_connections',
		on_delete=models.CASCADE
	)
	voyage=models.ForeignKey(
		Voyage,
		related_name='voyage_zotero_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
	class Meta:
		unique_together=[
			['zotero_source','voyage','page_range']
		]

class ZoteroEnslaverConnection(models.Model):
	zotero_source=models.ForeignKey(
		'ZoteroSource',
		related_name='zotero_enslaver_connections',
		on_delete=models.CASCADE
	)
	enslaver=models.ForeignKey(
		EnslaverIdentity,
		related_name='enslaver_zotero_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
	class Meta:
		unique_together=[
			['zotero_source','enslaver','page_range']
		]

class ZoteroEnslavedConnection(models.Model):
	zotero_source=models.ForeignKey(
		'ZoteroSource',
		related_name='zotero_enslaved_connections',
		on_delete=models.CASCADE
	)
	enslaved=models.ForeignKey(
		Enslaved,
		related_name='enslaved_zotero_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
	class Meta:
		unique_together=[
			['zotero_source','enslaved','page_range']
		]


class ZoteroSource(models.Model):
	"""
	Represents the relationship between Voyage and VoyageSources
	source_order determines the order sources appear for each voyage
	related to: :class:`~voyages.apps.voyage.models.VoyageSources`
	related to: :class:`~voyages.apps.voyage.models.Voyage`
	"""
	
	item_url=models.URLField(max_length=400,null=True)
	
	zotero_url=models.URLField(max_length=400)
	
	legacy_source=models.ForeignKey(
		VoyageSources,
		related_name="source_zotero_refs",
		null=True,
		on_delete=models.CASCADE
	)
	
	short_ref=models.CharField(
		max_length=255,
		null=True,
		blank=True,
	)
	
	zotero_title=models.CharField(
		max_length=255,
		null=False,
		blank=False,
	)
	
	zotero_date=models.CharField(
		max_length=60,
		null=False,
		blank=False
	)
	
	is_legacy_source=models.BooleanField(default=False,blank=True,null=True)
	
	last_updated=models.DateTimeField(auto_now=True)
	human_reviewed=models.BooleanField(default=False,blank=True,null=True)
	
	notes=models.TextField(null=True,blank=True)
		
	class Meta:
		unique_together=[
			['zotero_title','zotero_url','legacy_source']
		]
	
	def __str__(self):
		return self.zotero_title + " " + self.zotero_date

	@property
	def zotero_web_page_url(self):
		if self.zotero_url not in (None,""):
			url=re.sub("api\.zotero\.org","www.zotero.org",self.zotero_url)
			return url
		else:
			return None
	
	class Meta:
		ordering=['id']
