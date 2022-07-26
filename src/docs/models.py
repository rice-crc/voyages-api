from django.db import models

# Create your models here.

class Doc(models.Model):

	url = models.URLField(max_length=500)