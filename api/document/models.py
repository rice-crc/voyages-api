from django.db import models
import re
from voyage.models import Voyage
from past.models import Enslaved,EnslaverIdentity

class SourcePage(models.Model):
	"""
	INDIVIDUAL PAGES
	"""
	page_url=models.URLField(
		max_length=400,null=True
	)
	iiif_manifest_url=models.URLField(
		null=True,blank=True,max_length=400
	)
	iiif_baseimage_url=models.URLField(
		null=True,blank=True,max_length=400
	)
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
	source=models.ForeignKey(
		'Source',
		related_name='page_connection',
		on_delete=models.CASCADE
	)
	
	source_page=models.ForeignKey(
		'SourcePage',
		related_name='source_connection',
		on_delete=models.CASCADE
	)
	
	class Meta:
		unique_together=[
			['source','source_page']
		]

class VoyageConnection(models.Model):
	source=models.ForeignKey(
		'Source',
		related_name='source_voyage_connections',
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
			['source','voyage','page_range']
		]

class EnslaverConnection(models.Model):
	source=models.ForeignKey(
		'Source',
		related_name='source_enslaver_connections',
		on_delete=models.CASCADE
	)
	enslaver=models.ForeignKey(
		EnslaverIdentity,
		related_name='enslaver_source_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
	class Meta:
		unique_together=[
			['source','enslaver','page_range']
		]

class SourceEnslavedConnection(models.Model):
	source=models.ForeignKey(
		'Source',
		related_name='source_enslaved_connections',
		on_delete=models.CASCADE
	)
	enslaved=models.ForeignKey(
		Enslaved,
		related_name='enslaved_source_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
	class Meta:
		unique_together=[
			['source','enslaved','page_range']
		]


class Source(models.Model):
	"""
	Represents the relationship between Voyage and VoyageSources
	source_order determines the order sources appear for each voyage
	related to: :class:`~voyages.apps.voyage.models.VoyageSources`
	related to: :class:`~voyages.apps.voyage.models.Voyage`
	"""
	
	item_url=models.URLField(
		max_length=400,
		null=True
	)
	
	zotero_group_id=models.IntegerField(
		"Zotero Integer Group ID",
		null=False,
		blank=False
	)
	
	zotero_item_id=models.CharField(
		"Zotero Alphanumeric Item ID",
		unique=True,
		null=False,
		blank=False
	)
	
	short_ref=models.CharField(
		"Canonical, Unique Short Ref",
		max_length=25,
		null=True,
		blank=True,
		unique=True,
	)
	
	title=models.CharField(
		"Title",
		max_length=255,
		null=False,
		blank=False,
	)
	
	date=models.CharField(
		"Date of Publication or Authorship",
		max_length=60,
		null=False,
		blank=False
	)
	
	last_updated=models.DateTimeField(
		"Last Updated",
		auto_now=True
	)
	
	human_reviewed=models.BooleanField(
		"Review ",
		default=False,
		blank=True,
		null=True
	)
	
	notes=models.TextField(null=True,blank=True)
		
	class Meta:
		unique_together=[
			['title','url','legacy_source']
		]
	
	def __str__(self):
		return self.title + " " + self.date

	@property
	def zotero_web_page_url(self):
		if self.zotero_url not in (None,""):
			url="https://www.zotero.org/groups/%s/sv-docs/items/%s/library" %(self.zotero_group_id,self.zotero_item_id)
	
	class Meta:
		ordering=['id']
