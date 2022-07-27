from django.db import models
# Create your models here.

class Doc(models.Model):

	url = models.URLField(max_length=500)
	citation = models.CharField(max_length=500,null=True,blank=True)
	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		return str(self.citation)