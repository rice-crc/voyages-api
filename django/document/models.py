from django.db import models
import re

class SourcePage(models.Model):
	"""
	Voyage sources.
	Representing the original variables SOURCEA, SOURCEB, SOURCEC
	and etc to SOURCER
	"""
	
	item_url=models.URLField(null=True,blank=True)
	iiif_manifest_url=models.URLField(null=True,blank=True,max_length=400)
	iiif_baseimage_url=models.URLField(null=True,blank=True,max_length=400)
	
	def __str__(self):
		nonnulls=[i for i in [
				self.item_url,
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
	

class ZoteroSource(models.Model):
	"""
	Represents the relationship between Voyage and VoyageSources
	source_order determines the order sources appear for each voyage
	related to: :class:`~voyages.apps.voyage.models.VoyageSources`
	related to: :class:`~voyages.apps.voyage.models.Voyage`
	"""
	
	zotero_url=models.URLField(unique=True,max_length=400)
	
	zotero_title=models.CharField(
		max_length=255,
		null=False,
		blank=False,
		unique=True
	)
	
	zotero_date=models.CharField(
		max_length=60,
		null=False,
		blank=False
	)
	
	def __str__(self):
		return self.zotero_title + " " + self.zotero_date

	@property
	def zotero_web_page_url(self):
		if self.zotero_url not in (None,""):
			url=re.sub("api\.zotero\.org","www.zotero.org",self.zotero_url)
			return url
		else:
			return None
