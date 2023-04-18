from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import CharField, IntegerField
#import Levenshtein_search
import re
from voyage.models import Place, Voyage, VoyageSources
from common.models import *
#from common.validators import date_csv_field_validator

class EnslaverInfoAbstractBase(models.Model):
	principal_alias = models.CharField(max_length=255)

	# Personal info.
	birth_year = models.IntegerField(null=True)
	birth_month = models.IntegerField(null=True)
	birth_day = models.IntegerField(null=True)
	birth_place = models.ForeignKey(Place,
		on_delete=models.SET_NULL,
		related_name='+',
		null=True,
		db_index=True)

	death_year = models.IntegerField(null=True)
	death_month = models.IntegerField(null=True)
	death_day = models.IntegerField(null=True)
	death_place = models.ForeignKey(Place,
		on_delete=models.SET_NULL,
		related_name='+',
		null=True,
		db_index=True)

	father_name = models.CharField(max_length=255, null=True)
	father_occupation = models.CharField(max_length=255, null=True)
	mother_name = models.CharField(max_length=255, null=True)

	first_spouse_name = models.CharField(max_length=255, null=True)
	first_marriage_date = models.CharField(max_length=12, null=True)
	second_spouse_name = models.CharField(max_length=255, null=True)
	second_marriage_date = models.CharField(max_length=12, null=True)

	probate_date = models.CharField(max_length=12, null=True)
	will_value_pounds = models.CharField(max_length=12, null=True)
	will_value_dollars = models.CharField(max_length=12, null=True)
	will_court = models.CharField(max_length=12, null=True)
	text_id=models.CharField(max_length=50)
	first_active_year=models.IntegerField(null=True)
	last_active_year=models.IntegerField(null=True)
	number_enslaved=models.IntegerField(null=True)
	principal_location=models.ForeignKey(Place,
		on_delete=models.SET_NULL,
		related_name='+',
		null=True,
		db_index=True)
	class Meta:
		abstract = True

class EnslaverIdentity(EnslaverInfoAbstractBase):
	class Meta:
		verbose_name = 'Enslaver unique identity and personal info'

class EnslaverIdentitySourceConnection(models.Model):
	identity = models.ForeignKey(EnslaverIdentity, related_name="enslaver_sources", on_delete=models.CASCADE)
	# Sources are shared with Voyages.
	source = models.ForeignKey(VoyageSources, related_name="enslaver_identity",
							   null=False, on_delete=models.CASCADE)
	source_order = models.IntegerField()
	text_ref = models.CharField(max_length=255, null=False, blank=True)

class EnslaverAlias(models.Model):
	"""
	An alias represents a name appearing in a record that is mapped to
	a consolidated identity. The same individual may appear in multiple
	records under different names (aliases).
	"""
	identity = models.ForeignKey(
			EnslaverIdentity,
			on_delete=models.CASCADE,
			related_name='alias'
			)
	alias = models.CharField(max_length=255)

	class Meta:
		verbose_name = 'Enslaver alias'

class EnslaverVoyageConnection(models.Model):
	"""
	Associates an enslaver with a voyage at some particular role.
	"""

	class Role:
		CAPTAIN = 1
		OWNER = 2
		BUYER = 3
		SELLER = 4

	enslaver_alias = models.ForeignKey('EnslaverAlias',
									   null=False,
									   related_name='enslaver_voyage',
									   on_delete=models.CASCADE)
	voyage = models.ForeignKey('voyage.Voyage',
							   null=False,
							   on_delete=models.CASCADE)
	role = models.IntegerField(null=False)
	# There might be multiple persons with the same role for the same voyage
	# and they can be ordered (ranked) using the following field.
	order = models.IntegerField(null=True)
	# NOTE: we will have to substitute VoyageShipOwner and VoyageCaptain

class LanguageGroup(NamedModelAbstractBase):
	longitude = models.DecimalField("Longitude of point",
									max_digits=10,
									decimal_places=7,
									null=True)
	latitude = models.DecimalField("Latitude of point",
								   max_digits=10,
								   decimal_places=7,
								   null=True)

class ModernCountry(NamedModelAbstractBase):
	longitude = models.DecimalField("Longitude of Country",
									max_digits=10,
									decimal_places=7,
									null=False)
	latitude = models.DecimalField("Latitude of Country",
								   max_digits=10,
								   decimal_places=7,
								   null=False)
	languages = models.ManyToManyField(LanguageGroup)
	
	class Meta:
		verbose_name = "Modern country"
		verbose_name_plural = "Modern countries"

class RegisterCountry(NamedModelAbstractBase):
	pass
	class Meta:
		verbose_name = "Register country"
		verbose_name_plural = "Register countries"

class AltLanguageGroupName(NamedModelAbstractBase):
	language_group = models.ForeignKey(LanguageGroup,
									   null=False,
									   related_name='alt_names',
									   on_delete=models.CASCADE)

class CaptiveFate(NamedModelAbstractBase):
	class Meta:
		verbose_name = "Captive fate"
		verbose_name_plural = "Captive fates"

class CaptiveStatus(NamedModelAbstractBase):
	class Meta:
		verbose_name = "Captive status"
		verbose_name_plural = "Captive statuses"


# TODO: this model will replace resources.AfricanName

class Enslaved(models.Model):
	"""
	Enslaved person.
	"""
	id = models.IntegerField(primary_key=True)

	# For African Origins dataset documented_name is an African Name.
	# For Oceans of Kinfolk, this field is used to store the Western
	# Name of the enslaved.
	documented_name = models.CharField(max_length=100, blank=True)
	name_first = models.CharField(max_length=100, null=True, blank=True)
	name_second = models.CharField(max_length=100, null=True, blank=True)
	name_third = models.CharField(max_length=100, null=True, blank=True)
	modern_name = models.CharField(max_length=100, null=True, blank=True)
	# Certainty is used for African Origins only.
	editor_modern_names_certainty = models.CharField(max_length=255,
													 null=True,
													 blank=True)
	# Personal data
	age = models.IntegerField(null=True, db_index=True)
	gender = models.IntegerField(null=True, db_index=True)
	height = models.DecimalField(null=True, decimal_places=2, max_digits=6, verbose_name="Height in inches", db_index=True)
	skin_color = models.CharField(max_length=100, null=True, db_index=True)
	language_group = models.ForeignKey(LanguageGroup, null=True,
									   on_delete=models.CASCADE,
									   db_index=True)
	register_country = models.ForeignKey(RegisterCountry, null=True,
										 on_delete=models.CASCADE,
										db_index=True)
	# For Kinfolk, this is the Last known location field.
	post_disembark_location = models.ForeignKey(Place, null=True,
												on_delete=models.CASCADE,
												db_index=True)
	last_known_date = models.CharField(
		max_length=10,
			   blank=True,
		null=True,
		help_text="Date in format: MM,DD,YYYY")
	last_known_date_dd= models.IntegerField(null=True)
	last_known_date_mm= models.IntegerField(null=True)
	last_known_year_yyyy= models.IntegerField(null=True)
	captive_fate = models.ForeignKey(CaptiveFate, null=True, on_delete=models.SET_NULL, db_index=True)
	captive_status = models.ForeignKey(CaptiveStatus, null=True, on_delete=models.SET_NULL, db_index=True)
	voyage = models.ForeignKey(Voyage, null=False, on_delete=models.CASCADE, db_index=True)
	dataset = models.IntegerField(null=False, default=0, db_index=True)
	notes = models.CharField(null=True, max_length=8192)
	sources = models.ManyToManyField(VoyageSources,
									 through='EnslavedSourceConnection',
									 related_name='+')
	dataset=models.IntegerField(null=False, default=0, db_index=True)

class EnslavedSourceConnection(models.Model):
	enslaved = models.ForeignKey(Enslaved,
								 on_delete=models.CASCADE,
								 related_name='sources_conn')
	# Sources are shared with Voyages.
	source = models.ForeignKey(VoyageSources,
							   on_delete=models.CASCADE,
							   related_name='+',
							   null=False)
	source_order = models.IntegerField()
	text_ref = models.CharField(max_length=255, null=False, blank=True)

class EnslavedName(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	language = models.CharField(max_length=3, null=False, blank=False)
	recordings_count = models.IntegerField()
	class Meta:
		unique_together = ('name', 'language')
		verbose_name = "Enslaved name"
		verbose_name_plural = "Enslaved names"

class EnslavementRelationType(NamedModelAbstractBase):
	pass
	class Meta:
		verbose_name = "Enslavement relation type"
		verbose_name_plural = "Enslavement Relation Types"

class EnslavementRelation(models.Model):
	"""
	Represents a relation involving enslavers and enslaved individuals.
	"""
	id = models.IntegerField(primary_key=True)
	relation_type = models.ForeignKey(EnslavementRelationType,null=True, on_delete=models.CASCADE)
	place = models.ForeignKey(Place, null=True, on_delete=models.SET_NULL)
	date = models.CharField(max_length=12, null=True,
		help_text="Date in MM,DD,YYYY format with optional fields.")
	date_dd = models.IntegerField(null=True)
	date_mm = models.IntegerField(null=True)
	date_yyyy = models.IntegerField(null=True)
	amount = models.DecimalField(null=True, decimal_places=2, max_digits=6)
	voyage = models.ForeignKey(Voyage, related_name="+",
							   null=True, on_delete=models.CASCADE)
	source = models.ForeignKey(VoyageSources, related_name="+",
							   null=True, on_delete=models.CASCADE)
	text_ref = models.CharField(max_length=255, null=False, blank=True, help_text="Source text reference")

class EnslavedInRelation(models.Model):
	"""
	Associates an enslaved in a slave relation.
	"""
	id = models.IntegerField(primary_key=True)
	enslavement_relation = models.ForeignKey(
		EnslavementRelation,
		related_name="enslaved_relations",
		null=False,
		on_delete=models.CASCADE)
	enslaved = models.ForeignKey(Enslaved,
		related_name="enslaved_people",
		null=False,
		on_delete=models.CASCADE)

class EnslaverRole(NamedModelAbstractBase):
	pass
	class Meta:
		verbose_name = "Enslaver role"
		verbose_name_plural = "Enslaver roles"

class EnslaverInRelation(models.Model):
	"""
	Associates an enslaver in a slave relation.
	"""
	id = models.IntegerField(primary_key=True)
	enslavement_relation = models.ForeignKey(
		EnslavementRelation,
		related_name="enslavers",
		null=False,
		on_delete=models.CASCADE)
	enslaver_alias = models.ForeignKey(
	 	EnslaverAlias,
	   	related_name="enslaver_aliases",
		null=False,
		on_delete=models.CASCADE)
	role = models.ForeignKey(EnslaverRole,null=True, help_text="The role of the enslaver in this relation",on_delete=models.CASCADE)

class ExternalLinkAbstractBase(models.Model):
	url=models.URLField(max_length=500)
	authority=models.CharField(max_length=255, null=False, blank=False, help_text="")
	class Meta:
		abstract = True

class EnslaverLinkedData(ExternalLinkAbstractBase):
	enslaver=models.ForeignKey(
		EnslaverIdentity,
		null=True,
		on_delete=models.DO_NOTHING,
		related_name="enslaver_linked_data")
	class Meta:
		verbose_name = "Enslaver links"
		verbose_name_plural = "Enslaver links"

class EnslavedLink(ExternalLinkAbstractBase):
	enslaved=models.ForeignKey(
		Enslaved,
		null=True,
		on_delete=models.DO_NOTHING,
		related_name="enslaved_linked_data")
	class Meta:
		verbose_name = "Enslaved links"
		verbose_name_plural = "Enslaved links"