from django.db import models
import re
from voyage.models import Voyage
from past.models import Enslaved,EnslaverIdentity,EnslavementRelation
from common.models import NamedModelAbstractBase,SparseDateAbstractBase

class DocSparseDate(SparseDateAbstractBase):
	pass

class Page(models.Model):
	"""
	INDIVIDUAL PAGES
	"""
	page_url=models.URLField(
		max_length=400,null=True,blank=True
	)
	iiif_manifest_url=models.URLField(
		null=True,blank=True,max_length=400
	)
	iiif_baseimage_url=models.URLField(
		null=True,blank=True,max_length=400)
	image_filename=models.CharField(
		max_length=100,
		null=True,
		blank=True
	)
	transcription=models.TextField(null=True,blank=True)
	last_updated=models.DateTimeField(auto_now=True)
	human_reviewed=models.BooleanField(default=False,blank=True,null=True)
	
	is_british_library=models.BooleanField(
		"BL docs have been problematic, need a quick handle for them",
		default=False,blank=True,null=True
	)
	transkribus_pageid=models.IntegerField(null=True,blank=True,unique=True)
	
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
		related_name='page_connections',
		on_delete=models.CASCADE
	)
	
	page=models.ForeignKey(
		'Page',
		related_name='source_connections',
		on_delete=models.CASCADE
	)
	order=models.IntegerField(
		"Document page order",
		null=True,
		blank=True
	)
	
# 	class Meta:
# 		unique_together=[
# 			['source','page'],
# 			['source','order']
# 		]

class SourceVoyageConnection(models.Model):
	source=models.ForeignKey(
		'Source',
		related_name='source_voyage_connections',
		on_delete=models.CASCADE
	)
	voyage=models.ForeignKey(
		Voyage,
		related_name='voyage_source_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
# 	class Meta:
# 		unique_together=[
# 			['source','voyage','page_range']
# 		]

class SourceEnslaverConnection(models.Model):
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
# 	class Meta:
# 		unique_together=[
# 			['source','enslaver','page_range']
# 		]

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

class SourceEnslavementRelationConnection(models.Model):
	source=models.ForeignKey(
		'Source',
		related_name='source_enslavement_relation_connections',
		on_delete=models.CASCADE
	)
	enslavement_relation=models.ForeignKey(
		EnslavementRelation,
		related_name='enslavement_relation_source_connections',
		on_delete=models.CASCADE
	)
	page_range=models.CharField(
		max_length=250,
		null=True,
		blank=True
	)
# 	class Meta:
# 		unique_together=[
# 			['source','enslaved','page_range']
# 		]

class ShortRef(models.Model):
	"""
	Represents a controlling collection. Necessitated by SSC docs.
	
	We have so many titled, individual documents micro-segmented in the IIIF manifests that we have broken the way text_ref used to be used.
	
	For instance, both of the below two sources belong to volume 43 in the Clements collection. Each is a "source" with a "title" that belongs to AP CLEMENTS 43
	
		1. Manuscript document, "An Explanation of Sundry Paper's card: with me to Peru, &amp; of other's acquired there", after 1736 February 6
		2. Manuscript document, "John Browns Demands", after 1736
		
	And we have individual page numbers for both of those.
	"""
	name = models.CharField(max_length=255,unique=True)
	transkribus_docId = models.CharField(
		max_length=10,
		unique=True,
		blank=True,
		null=True
	)
	
	def __str__(self):
		return self.name

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
		null=True,
		blank=True
	)
	
	zotero_item_id=models.CharField(
		"Zotero Alphanumeric Item ID",
		max_length=20,
		unique=True,
		null=True,
		blank=True
	)
	
	zotero_grouplibrary_name=models.CharField(
		max_length=255,
		null=False,
		blank=False,
		default="sv-docs"
	)
	
	short_ref=models.ForeignKey(
		ShortRef,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='short_ref_sources'
	)
	
	title=models.CharField(
		"Title",
		max_length=255,
		null=False,
		blank=False
	)
	
	is_british_library=models.BooleanField(
		"BL docs have been problematic, need a quick handle for them",
		default=False,blank=True,null=True
	)
	
	date = models.OneToOneField(
		DocSparseDate,
		verbose_name="Date of publication or authorship",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+"
	)
	
	last_updated=models.DateTimeField(
		"Last Updated",
		auto_now=True
	)
	
	human_reviewed=models.BooleanField(
		"Review",
		default=False,
		blank=True,
		null=True
	)
	
	has_published_manifest=models.BooleanField(
		"Is there a published manifest on dellamonica's server?",
		default=False,
		blank=False,
		null=False
	)
	
	notes=models.TextField(null=True,blank=True)
	
	order_in_shortref=models.IntegerField(
		"Now that we're splitting shortrefs, sources should be ordered under them",
		null=True,
		blank=True
	)
		
	class Meta:
		unique_together=[
			['title','url','legacy_source']
		]
	
	def __str__(self):
		return self.title + " " + self.short_ref.name

	@property
	def zotero_web_page_url(self):
		if self.zotero_url not in (None,""):
			url="https://www.zotero.org/groups/%s/sv-docs/items/%s/library" %(self.zotero_group_id,self.zotero_item_id)
	
	class Meta:
		ordering=['id']
