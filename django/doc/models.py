from django.db import models

class NamedModelAbstractBase(models.Model):
	name = models.CharField(max_length=255,blank=False,null=False)
	def __str__(self):
		return self.name
	class Meta:
		abstract = True

class DocTag(NamedModelAbstractBase):
	tag=models.CharField(max_length=20,null=False,blank=False,unique=True)
	class Meta:
		verbose_name = "Document Tag"
		verbose_name_plural = "Document Tags"
	def __str__(self):
		return self.tag

#UIDs in the doc app should come from zotero I think
class Doc(NamedModelAbstractBase):
	doc_title=models.CharField(max_length=150,null=True,blank=True)
	pub_year=models.IntegerField(null=True,blank=True)
	tags=models.ManyToManyField(DocTag)
	zotero_uri=models.URLField(max_length=500,null=False,blank=False)
	full_ref = models.CharField(max_length=1000, null=False, blank=False)
	uid = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		verbose_name = "Source Authority"
		verbose_name_plural = "Source Authorities"
	def __str__(self):
		return self.doc_title

class Reference(NamedModelAbstractBase):
	doc = models.ForeignKey(Doc,
		on_delete=models.CASCADE,
		related_name='source_refs',
		null=False,
		blank=False)
	iiif_manifest_uri=models.URLField(max_length=500,null=True,blank=True)
	zotero_uri=models.URLField(max_length=500,null=False,blank=False)
	text_ref = models.CharField(max_length=255, null=False, blank=True)
	uid = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		verbose_name = "Reference"
		verbose_name_plural = "References"
	def __str__(self):
		return self.text_ref