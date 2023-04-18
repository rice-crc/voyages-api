from django.db import models
from common.models import *

class DocUid(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.CharField(max_length=1000, null=False, blank=False, unique=True)

class DocTag(NamedModelAbstractBase):
	tag=models.CharField(max_length=20,null=False,blank=False)
	def __str__(self):
		return self.url.__unicode__()
	def __unicode__(self):
		return str(self.url)

class Doc(models.Model):
	doc_title=models.CharField(max_length=150,null=True,blank=True)
	pub_year=models.IntegerField(null=True,blank=True)
	tag=models.ManyToManyField(DocTag)
	zotero_uri=models.URLField(max_length=500,null=False,blank=False)
	full_ref = models.CharField(max_length=1000, null=False, blank=False)
	doc_uid = models.OneToOneField(
		DocUid,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='uid_doc'
	)
	class Meta:
		verbose_name = "Source Authority"
		verbose_name_plural = "Source Authorities"
	def __str__(self):
		return self.url.__unicode__()
	def __unicode__(self):
		return str(self.url)

class Reference(NamedModelAbstractBase):
	doc = models.ForeignKey(Doc,
		on_delete=models.CASCADE,
		related_name='source_refs',
		null=False,
		blank=False)
	iiif_manifest_uri=models.URLField(max_length=500,null=True,blank=True)
	text_ref = models.CharField(max_length=255, null=False, blank=True)
	class Meta:
		verbose_name = "Reference"
		verbose_name_plural = "References"