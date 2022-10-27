from django.db import models
# Create your models here.

class DocTag(models.Model):
	tag=models.CharField(max_length=20,null=False,blank=False)
	
	def __str__(self):
		return self.url.__unicode__()

	def __unicode__(self):
		return str(self.url)

class Doc(models.Model):

	url = models.URLField(max_length=500)
	citation = models.CharField(max_length=500,null=True,blank=True)
	title=models.CharField(max_length=150,null=True,blank=True)
	pub_year=models.IntegerField(null=True,blank=True)
	tag=models.ManyToManyField(DocTag)
	def __str__(self):
		return self.url.__unicode__()

	def __unicode__(self):
		return str(self.url)
