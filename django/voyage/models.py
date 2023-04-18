from __future__ import unicode_literals

from builtins import str
from django.db import models
from django.db.models import Prefetch
from geo.models import Place
from doc.models import *
from event.models import Event
from past.models import PersonEventConnection

class NamedModelAbstractBase(models.Model):
	name = models.CharField(max_length=255,blank=False,null=False)
	def __str__(self):
		return self.name
	class Meta:
		abstract = True
		
class AfricanInfo(NamedModelAbstractBase):
	"""
	Used to capture information about the ethnicity or background of the
	captives on a ship if found in merchants records or newspaper ads
	"""
	pass
	possibly_offensive = models.BooleanField(
		default=False,
		help_text="Indicates that the wording used in this label might be offensive to readers")

class CargoType(NamedModelAbstractBase):
	"""
	Types of cargo that were shipped on the voyage along with captives.
	"""
	pass
	
class CargoUnit(NamedModelAbstractBase):
	"""
	A unit of measure associated with cargo (weight/volume etc).
	"""
	pass

# Voyage Groupings
# check for mismatch in VoyageGroupings class
class VoyageGroupings(models.Model):
	"""
	Labels for groupings names.
	"""
	name = models.CharField(max_length=30)
	value = models.IntegerField()
	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Grouping for estimating imputed slaves"
		verbose_name_plural = "Groupings for estimating imputed slaves"

class TonType(NamedModelAbstractBase):
	"""
	Types of tonnage.
	"""
	uid = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		verbose_name = "Type of tons"
		verbose_name_plural = "Types of tons"


class Rig(NamedModelAbstractBase):
	"""
	Rig of Vessel.
	"""
	uid = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		verbose_name = "Rig of vessel"
		verbose_name_plural = "Rigs of vessel"

class Vessel(NamedModelAbstractBase):
	"""
	Information about voyage ship.
	related to: :class:`~voyages.apps.voyage.models.Voyage`
	related to: :class:`~voyages.apps.geo.models.Place`
	related to: :class:`~voyages.apps.voyage.models.TonType`
	related to: :class:`~voyages.apps.voyage.models.Rig`
	"""

	# Data variables
	uid = models.CharField(max_length=100, null=False, blank=False, unique=True)
	nationality = models.ForeignKey(
		Place,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		verbose_name="Ship Nationality",
		related_name="ships_of_this_nationality"
	)
	tonnage = models.IntegerField(
		"Tonnage of vessel",
		null=True,
		blank=True
	)
	ton_type = models.ForeignKey(
		'TonType',
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		verbose_name="Type of Tonnage",
		related_name="ton_type_ships"
	)
	rig = models.ForeignKey(
		'Rig',
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		verbose_name="Rig of Vessel",
		related_name="rig_vessels"
	)
	guns_mounted = models.IntegerField(
		"Guns mounted",
		null=True,
		blank=True
	)
	year_of_construction = models.IntegerField(
		"Year of vessel's construction",
		null=True,
		blank=True
	)
	vessel_construction_place = models.ForeignKey(
		Place,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		related_name="vessels_constructed_here",
		verbose_name="Place of vessel construction"
	)
	registered_year = models.IntegerField(
		"Year of vessel's registration",
		null=True,
		blank=True
	)
	registered_place = models.ForeignKey(
		Place,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		related_name="vessels_registered_here",
		verbose_name="Place where vessel registered"
	)
	tonnage_mod = models.FloatField(
		"Tonnage standardized on British"
		"measured tons 1773-1870",
		null=True,
		blank=True
	)
	
	class Meta:
		verbose_name = "Ship"
		verbose_name_plural = "Ships"

class VoyageCargoConnection(models.Model):
	"""
	Specifies cargo that was shipped together with captives.
	"""
	cargo = models.ForeignKey(CargoType, related_name="cargo_voyage_connection",
							  on_delete=models.CASCADE)
	voyage = models.ForeignKey('Voyage', related_name="voyage_cargo_connection",
							   on_delete=models.CASCADE)
	unit = models.ForeignKey(CargoUnit, related_name="unit_cargo_connection", null=True,on_delete=models.CASCADE)
	amount = models.FloatField("The amount of cargo according to the unit", null=True)

	class Meta:
		unique_together = ['voyage', 'cargo']

class LinkedVoyages(models.Model):
	"""
	Allow pairs of voyages to be linked.
	"""
	first = models.ForeignKey(
		'Voyage',
		related_name="links_to_other_voyages",
		on_delete=models.CASCADE
	)
	second = models.ForeignKey(
		'Voyage',
		related_name="+",
		on_delete=models.CASCADE
	)

class CrewStats(models.Model):
	
	crew=models.IntegerField(null=True,blank=True)
	
class EnslavedStats(models.Model):
	
	men=models.IntegerField(null=True,blank=True)
	women=models.IntegerField(null=True,blank=True)
	boys=models.IntegerField(null=True,blank=True)
	girls=models.IntegerField(null=True,blank=True)
	infant=models.IntegerField(null=True,blank=True)
	total=models.IntegerField(null=True,blank=True)
	male_ratio=models.FloatField(null=True,blank=True)
	female_ratio=models.FloatField(null=True,blank=True)
	child_ratio=models.FloatField(null=True,blank=True)
	total_ratio=models.FloatField(null=True,blank=True)
	
	men_imp=models.IntegerField(null=True,blank=True)
	women_imp=models.IntegerField(null=True,blank=True)
	boys_imp=models.IntegerField(null=True,blank=True)
	girls_imp=models.IntegerField(null=True,blank=True)
	infant_imp=models.IntegerField(null=True,blank=True)
	total_imp=models.IntegerField(null=True,blank=True)
	male_ratio_imp=models.FloatField(null=True,blank=True)
	female_ratio_imp=models.FloatField(null=True,blank=True)
	child_ratio_imp=models.FloatField(null=True,blank=True)
	total_ratio_imp=models.FloatField(null=True,blank=True)


class ItineraryEventStats(models.Model):
	
	enslaved_living_stats=models.OneToOneField(
		EnslavedStats,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='+'
	)
	
	enslaved_died_stats=models.OneToOneField(
		EnslavedStats,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='+'
	)
	
	crew_living_stats=models.OneToOneField(
		CrewStats,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='+'
	)
	
	crew_died_stats=models.OneToOneField(
		CrewStats,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='+'
	)


class ItineraryEventConnection(models.Model):
	event=models.OneToOneField(
		Event,
		on_delete=models.CASCADE,	
	)
	
	event_stats=models.OneToOneField(
		ItineraryEventStats,
		on_delete=models.CASCADE,
		null=True,
		blank=True	
	)
	
	itinerary=models.ForeignKey(
		'Itinerary',
		null=False,
		blank=False,
		on_delete=models.CASCADE
	)
	
	order=models.IntegerField(null=False,blank=False)
	
	class Meta:
		unique_together=['order','itinerary']

class Itinerary(models.Model):
	voyage=models.OneToOneField(
		'Voyage',
		null=False,
		blank=False,
		on_delete=models.CASCADE
	)
	
class Voyage(models.Model):
	"""
	Information about voyages.
	"""

	voyage_id = models.IntegerField("Voyage ID", unique=True)

	voyage_in_cd_rom = models.BooleanField(
		"Voyage in 1999 CD-ROM?",
		max_length=1,
		default=False,
		blank=True
	)

	# Technical variables
	voyage_groupings = models.ForeignKey(
		'VoyageGroupings',
		verbose_name="Voyage Groupings",
		related_name='groupings_voyage',
		blank=True,
		null=True,
		on_delete=models.CASCADE
	)

	# Data and imputed variables
	voyage_vessel = models.ForeignKey(
		'Vessel',
		verbose_name="Vessel",
		related_name='vessel_voyage',
		blank=True,
		null=True,
		on_delete=models.CASCADE
	)
	
	voyage_itinerary = models.ForeignKey(
		'Itinerary',
		verbose_name="Itinerary",
		related_name='itinerary_voyage',
		blank=True,
		null=True,
		on_delete=models.CASCADE
	)
	
	references=models.ManyToManyField(Reference)
	
	enslavement_relations=models.ManyToManyField(PersonEventConnection)
		
	last_update = models.DateTimeField(auto_now=True)
	
	african_info = models.ManyToManyField(AfricanInfo)
	
	cargo = models.ManyToManyField(
		CargoType,
		through='VoyageCargoConnection',
		blank=True
	)
	
	dataset = models.IntegerField(null=False)
	
	# generate natural key
	def natural_key(self):
		return (self.voyage_id,)
		
	def __str__(self):
		return "Voyage #%s" % str(self.voyage_id)


