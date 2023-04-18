from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from geo.models import Place
from doc.models import Reference

class NamedModelAbstractBase(models.Model):
	name = models.CharField(max_length=255,blank=False,null=False)
	def __str__(self):
		return self.name
	class Meta:
		abstract = True


# Create your models here.
class Date(models.Model):
	"""
	Nullable dates
	"""
	d = models.IntegerField(
		blank=True,
		validators=[
			MaxValueValidator(1),
			MinValueValidator(31)
		]
	)
	m = models.IntegerField(
		blank=True,
		validators=[
			MaxValueValidator(1),
			MinValueValidator(12)
		]
	)
	y = models.IntegerField(
		blank=True,
		validators=[
			MaxValueValidator(1),
			MinValueValidator(3000)
		]
	)
	h = models.IntegerField(
		blank=True,
		validators=[
			MaxValueValidator(1),
			MinValueValidator(24)
		]
	)
	imputed = models.BooleanField(default=False)
	def __str__(self):
		return " ".join([
			"/".join([str(i) if i is not None else '' for i in [m,d,y]]),
			[str(h)+":00" if h is not None else ""],
			['**' if self.imputed else ""]
		])

class EventType(NamedModelAbstractBase):
	pass

class Event(models.Model):
	"""
	Nullable dates
	"""
	start_date=models.ForeignKey(
		Date,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='events_begun_on_this_date'
	)
	finish_date=models.ForeignKey(
		Date,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='events_ended_on_this_date'
	)
	place=models.ForeignKey(
		Place,
		null=False,
		blank=False,
		on_delete=models.CASCADE
	)
	event_type = models.ForeignKey(
		EventType,
		null=False,
		blank=False,
		on_delete=models.CASCADE
	)
	references = models.ManyToManyField(Reference)
	def __str__(self):
		return " | ".join([self.place.__str__,self.date.__str__,self.event_type.__str__])