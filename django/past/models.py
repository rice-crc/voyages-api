from __future__ import absolute_import, unicode_literals

import operator
from builtins import range, str
from functools import reduce
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import (connection, models, transaction)
from django.db.models import (Aggregate, Case, CharField, Count, F, Func, IntegerField, Max, Min, Q, Sum, Value, When)
from django.db.models.expressions import Subquery, OuterRef
from django.db.models.fields import TextField
from django.db.models.functions import Coalesce, Concat, Length, Substr
from django.db.models.sql import RawQuery
from voyage.models import Place, Voyage, VoyageDataset, VoyageSources
import re
from common.models import NamedModelAbstractBase,SparseDate

class SourceConnectionAbstractBase(models.Model):
	# Sources are shared with Voyages.
	source = models.ForeignKey(VoyageSources, related_name="+",
							   null=False, on_delete=models.CASCADE)
	source_order = models.IntegerField()
	text_ref = models.CharField(max_length=255, null=False, blank=True)

	class Meta:
		abstract = True

class EnslaverInfoAbstractBase(models.Model):
	principal_alias = models.CharField(max_length=255)

	# Personal info.
	birth_year = models.IntegerField(null=True,blank=True)
	birth_month = models.IntegerField(null=True,blank=True)
	birth_day = models.IntegerField(null=True,blank=True)
	birth_place = models.ForeignKey(Place, null=True,blank=True, on_delete=models.SET_NULL, related_name='+')

	death_year = models.IntegerField(null=True,blank=True)
	death_month = models.IntegerField(null=True,blank=True)
	death_day = models.IntegerField(null=True,blank=True)
	death_place = models.ForeignKey(Place, null=True,blank=True, on_delete=models.SET_NULL, related_name='+')

	father_name = models.CharField(max_length=255, null=True,blank=True)
	father_occupation = models.CharField(max_length=255, null=True,blank=True)
	mother_name = models.CharField(max_length=255, null=True,blank=True)

	# We will include the spouses in the Enslaver table and use
	# EnslavementRelation to join the individuals by a marriage
	# relationship.
	# first_spouse_name = models.CharField(max_length=255, null=True)
	# first_marriage_date = models.CharField(max_length=12, null=True)
	# second_spouse_name = models.CharField(max_length=255, null=True)
	# second_marriage_date = models.CharField(max_length=12, null=True)
	
	probate_date = models.CharField(max_length=12, null=True,blank=True)
	will_value_pounds = models.CharField(max_length=12, null=True,blank=True)
	will_value_dollars = models.CharField(max_length=12, null=True,blank=True)
	will_court = models.CharField(max_length=12, null=True,blank=True)
	principal_location = models.ForeignKey(Place, null=True,
												on_delete=models.CASCADE,
												db_index=True,blank=True)
	notes = models.CharField(null=True,blank=True, max_length=8192)
	
	enslaved_count = models.IntegerField(db_index=True,blank=True,null=True)
	transactions_amount = models.DecimalField(db_index=True,blank=True, null=False, default=0, decimal_places=2, max_digits=6)
	first_year = models.IntegerField(db_index=True,blank=True, null=True)
	last_year = models.IntegerField(db_index=True,blank=True, null=True)

	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		return "Enslaver info: " + self.principal_alias
	 
	class Meta:
		abstract = True

class EnslaverIdentity(EnslaverInfoAbstractBase):

	class Meta:
		verbose_name = "Enslaver unique identity and personal info"
		verbose_name_plural = "Enslaver unique identity and personal info"

class EnslaverIdentitySourceConnection(models.Model):
	identity = models.ForeignKey(EnslaverIdentity, on_delete=models.CASCADE)
	# Sources are shared with Voyages.
	source = models.ForeignKey(VoyageSources, related_name="+",
							   null=False, on_delete=models.CASCADE)
	source_order = models.IntegerField()
	text_ref = models.CharField(max_length=255, null=False, blank=True)

class EnslaverAlias(models.Model):
	"""
	An alias represents a name appearing in a record that is mapped to
	a consolidated identity. The same individual may appear in multiple
	records under different names (aliases).
	"""
	identity = models.ForeignKey(EnslaverIdentity, on_delete=models.CASCADE, related_name='aliases')
	alias = models.CharField(max_length=255)
	
	# The manual id can be used to track the original entries in sheets produced
	# by the researchers.
	manual_id = models.CharField(max_length=30, null=True,blank=True)

	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		return "EnslaverAlias: " + self.alias

	class Meta:
		verbose_name = 'Enslaver alias'
		verbose_name_plural = 'Enslaver aliases'

class EnslaverRole(NamedModelAbstractBase):
	class Meta:
		verbose_name = "Enslaver role"
		verbose_name_plural = "Enslaver roles"
		

class EnslaverVoyageConnection(models.Model):
	"""
	Associates an enslaver with a voyage at some particular role.
	"""

	enslaver_alias = models.ForeignKey(
		EnslaverAlias,
		null=False,
		on_delete=models.CASCADE,
		related_name='enslaver_voyages'
	)
	voyage = models.ForeignKey(
		'voyage.Voyage',
		null=False,
		on_delete=models.CASCADE,
		related_name='voyage_enslavers'
	)
	role = models.ForeignKey(EnslaverRole, null=False, on_delete=models.CASCADE)
	# There might be multiple persons with the same role for the same voyage
	# and they can be ordered (ranked) using the following field.
	order = models.IntegerField(null=True)
	# NOTE: we will have to substitute VoyageShipOwner and VoyageCaptain
	# models/tables by this entity.
	# leaving this line below for later cleanup when the migration is finished.
	# settings.VOYAGE_ENSLAVERS_MIGRATION_STAGE

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
	
	class Meta:
		verbose_name = "Register country"
		verbose_name_plural = "Register countries"

class AltLanguageGroupName(NamedModelAbstractBase):
	language_group = models.ForeignKey(LanguageGroup,
									   null=False,
									   related_name='alt_names',
									   on_delete=models.CASCADE)

class EnslavedDataset:
	AFRICAN_ORIGINS = 0
	OCEANS_OF_KINFOLK = 1


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
	enslaved_id = models.IntegerField(primary_key=True)

	# For African Origins dataset documented_name is an African Name.
	# For Oceans of Kinfolk, this field is used to store the Western
	# Name of the enslaved.
	documented_name = models.CharField(
		max_length=100,
		blank=True
	)
	name_first = models.CharField(
		max_length=100,
		null=True,
		blank=True
	)
	name_second = models.CharField(
		max_length=100,
		null=True,
		blank=True
	)
	name_third = models.CharField(
		max_length=100,
		null=True,
		blank=True
	)
	modern_name = models.CharField(
		max_length=100,
		null=True,
		blank=True
	)
	# Certainty is used for African Origins only.
	editor_modern_names_certainty = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)
	# Personal data
	age = models.IntegerField(
		null=True,
		blank=True,
		db_index=True
	)
	gender = models.IntegerField(
		null=True,
		blank=True,
		db_index=True
	)
	height = models.DecimalField(
		null=True,
		blank=True,
		decimal_places=2,
		max_digits=6,
		verbose_name="Height in inches",
		db_index=True
	)
	skin_color = models.CharField(
		max_length=100,
		null=True,
		blank=True,
		db_index=True
	)
	language_group = models.ForeignKey(
		LanguageGroup,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		db_index=True
	)
	register_country = models.ForeignKey(
		RegisterCountry,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
	)
	# For Kinfolk, this is the Last known location field.
	post_disembark_location = models.ForeignKey(
		Place,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		db_index=True,
		related_name='+'
	)
	last_known_date = models.ForeignKey(
		SparseDate,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		verbose_name="Last known date",
		related_name="+"
	)
	
	captive_fate = models.ForeignKey(CaptiveFate, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
	captive_status = models.ForeignKey(CaptiveStatus, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
	voyage = models.ForeignKey(Voyage, null=False, on_delete=models.CASCADE, db_index=True)
	dataset = models.IntegerField(null=False, default=0, db_index=True)
	notes = models.CharField(null=True,blank=True, max_length=8192)
	sources = models.ManyToManyField(VoyageSources,
									 through='EnslavedSourceConnection',
									 related_name='+')
	def __str__(self):
		return " : ".join([str(self.enslaved_id),self.documented_name])

	class Meta:
		verbose_name="Enslaved Person"
		verbose_name_plural="Enslaved People"


class EnslavedSourceConnection(SourceConnectionAbstractBase):
	enslaved = models.ForeignKey(Enslaved,
								 on_delete=models.CASCADE,
								 related_name='sources_conn')


class EnslavedContributionStatus:
	PENDING = 0
	ACCEPTED = 1
	REJECTED = 2


class EnslavedContribution(models.Model):
	enslaved = models.ForeignKey(Enslaved, on_delete=models.CASCADE)
	contributor = models.ForeignKey(User, null=True, related_name='+',
									on_delete=models.CASCADE)
	date = models.DateField(auto_now_add=True)
	notes = models.CharField(max_length=255, null=True, blank=True)
	is_multilingual = models.BooleanField(default=False)
	status = models.IntegerField()
	token = models.CharField(max_length=40, null=True, blank=True)


class EnslavedContributionNameEntry(models.Model):
	contribution = models.ForeignKey(EnslavedContribution,
									 on_delete=models.CASCADE,
									 related_name='contributed_names')
	name = models.CharField(max_length=255, null=False, blank=False)
	order = models.IntegerField()
	notes = models.CharField(max_length=255, null=True, blank=True)


class EnslavedContributionLanguageEntry(models.Model):
	contribution = models.ForeignKey(EnslavedContribution,
									 on_delete=models.CASCADE,
									 related_name='contributed_language_groups')
	language_group = models.ForeignKey(LanguageGroup, null=True,
									   on_delete=models.CASCADE)
	order = models.IntegerField()


class EnslavedName(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	language = models.CharField(max_length=3, null=False, blank=False)
	recordings_count = models.IntegerField()

	class Meta:
		unique_together = ('name', 'language')


class EnslavementRelationType(NamedModelAbstractBase):
	pass


class EnslavementRelation(models.Model):
	"""
	Represents a relation involving any number of enslavers and enslaved
	individuals.
	"""
	
	relation_type = models.ForeignKey(EnslavementRelationType, null=False, on_delete=models.CASCADE)
	place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
	date = models.ForeignKey(
		SparseDate,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		verbose_name="Enslavement relation date",
		related_name="+"
	)
	
	amount = models.DecimalField(null=True,blank=True, decimal_places=2, max_digits=6)
	unnamed_enslaved_count = models.IntegerField(null=True,blank=True)
	voyage = models.ForeignKey(Voyage, related_name="+",
							   null=True,blank=True, on_delete=models.CASCADE)
	source = models.ForeignKey(VoyageSources, related_name="+",
							   null=True,blank=True, on_delete=models.CASCADE)
	text_ref = models.CharField(max_length=255, null=True, blank=True, help_text="Source text reference")
	def __str__(self):
		return str(self.id)

class EnslavedInRelation(models.Model):
	"""
	Associates an enslaved in a slave relation.
	"""

	relation = models.ForeignKey(
		EnslavementRelation,
		related_name="enslaved",
		null=False,
		on_delete=models.CASCADE)
	enslaved = models.ForeignKey(Enslaved,
		related_name="relations",
		null=False,
		on_delete=models.CASCADE)
	def __str__(self):
		return self.enslaved.documented_name


class EnslaverInRelation(models.Model):
	"""
	Associates an enslaver in a slave relation.
	"""

	relation = models.ForeignKey(
		EnslavementRelation,
		related_name="enslavers",
		null=False,
		on_delete=models.CASCADE)
	enslaver_alias = models.ForeignKey(EnslaverAlias, null=False, on_delete=models.CASCADE)
	role = models.ForeignKey(EnslaverRole, null=False, on_delete=models.CASCADE, help_text="The role of the enslaver in this relation")
	def __str__(self):
		return self.enslaver_alias.alias

def single_val(source):
	try:
		if isinstance(source, list):
			source = source[0]
	except:
		pass
	return source


class EnslaverContribution(models.Model):
	# We allow NULLs because the enslaver may be deleted and we still want to
	# keep the contribution (it might even be the reason the identity was
	# deleted, say in the case of a merge).
	enslaver = models.ForeignKey(EnslaverIdentity, null=True, on_delete=models.SET_NULL)
	contributor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	created = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(null=False)
	data = models.TextField(null=False)
