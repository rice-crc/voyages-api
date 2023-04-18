from django.db import models

class NamedModelAbstractBase(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.id) + ", " + self.name

    class Meta:
        abstract = True
