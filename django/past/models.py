from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.db.models import CharField, IntegerField, ManyToManyField
import re
from geo.models import Place
from doc.models import Reference
from event.models import Event,Date

class NamedModelAbstractBase(models.Model):
	name = models.CharField(max_length=255,blank=False,null=False)
	def __str__(self):
		return self.name
	class Meta:
		abstract = True

class Role(NamedModelAbstractBase):
	pass
	class Meta:
		verbose_name = "Enslaver role"
		verbose_name_plural = "Enslaver roles"

class PersonEventConnection(models.Model):
	event=models.ForeignKey(
		Event,
		on_delete=models.CASCADE,
		related_name='event_person_connection'
	)
	role=models.ForeignKey(
		Role,
		on_delete=models.CASCADE,
		related_name='people_with_role'
	)
	class Meta:
		verbose_name = "Person in event"
		verbose_name_plural = "People in events"

class EnslaverInfoAbstractBase(models.Model):
	principal_alias = models.CharField(max_length=255)
	birth=models.ForeignKey(
		PersonEventConnection,
		on_delete=models.CASCADE,
		related_name='enslavers_born_now'
	)

	death=models.ForeignKey(
		PersonEventConnection,
		on_delete=models.CASCADE,
		related_name='enslavers_died_now'
	)

	father_name = models.CharField(max_length=255, null=True)
	father_occupation = models.CharField(max_length=255, null=True)
	mother_name = models.CharField(max_length=255, null=True)
	marriages = ManyToManyField(PersonEventConnection)
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
		related_name='enslaver_principal_location',
		null=True,
		db_index=True)
	references=ManyToManyField(Reference)
	class Meta:
		abstract = True

class EnslaverIdentity(EnslaverInfoAbstractBase):
	class Meta:
		verbose_name = 'Enslaver Identity'
		verbose_name_plural = 'Enslaver Identities'

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
	enslavement_events=models.ManyToManyField(PersonEventConnection)
	uid = models.IntegerField(null=False,blank=False,unique=True)
	class Meta:
		verbose_name = 'Enslaver alias'
		verbose_name_plural = 'Enslaver aliases'

class LanguageGroup(Place):
	class Meta:
		verbose_name = "Geo-Coded Language Group"
		verbose_name_plural = "Geo-Coded Language Groups"

class ModernCountry(Place):
	class Meta:
		verbose_name = "Modern Country"
		verbose_name_plural = "Modern Countries"

class RegisterCountry(Place):
	pass
	class Meta:
		verbose_name = "Register country"
		verbose_name_plural = "Register countries"

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
	language_group = models.ForeignKey(
		LanguageGroup,
		null=True,
		on_delete=models.CASCADE,
		db_index=True,
		related_name='enslaved_people_with_language_group_here'
	)
	register_country = models.ForeignKey(
		RegisterCountry,
		null=True,
		on_delete=models.CASCADE,
		db_index=True,
		related_name='enslaved_people_registered_with_this_country'
		)
	# For Kinfolk, this is the Last known location field.
	post_disembark_location = models.ForeignKey(
		Place,
		null=True,
		on_delete=models.CASCADE,
		db_index=True,
		related_name='enslaved_people_who_ended_up_here'
	)
	last_known_date = models.ForeignKey(
		Date,
		null=True,
		on_delete=models.CASCADE,
		db_index=True
	)
	enslavement_events=models.ManyToManyField(PersonEventConnection)
	captive_fate = models.ForeignKey(CaptiveFate, null=True, on_delete=models.SET_NULL, db_index=True)
	captive_status = models.ForeignKey(CaptiveStatus, null=True, on_delete=models.SET_NULL, db_index=True)
	dataset = models.IntegerField(null=False, default=0, db_index=True)
	notes = models.CharField(null=True, max_length=8192)
	references = models.ManyToManyField(Reference)
	dataset=models.IntegerField(null=False, default=0, db_index=True)

class EnslavedName(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	language = models.CharField(max_length=3, null=False, blank=False)
	recordings_count = models.IntegerField()
	class Meta:
		unique_together = ('name', 'language')
		verbose_name = "Enslaved name"
		verbose_name_plural = "Enslaved names"

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