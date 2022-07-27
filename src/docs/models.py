from django.db import models
from voyage.models import VoyageSources
# Create your models here.

class Doc(models.Model):

	url = models.URLField(max_length=500)
	source = models.ForeignKey(
		VoyageSources,
		on_delete=models.CASCADE,
		related_name="doc",
		verbose_name="Source",
		null=True
	)
	
	