from __future__ import absolute_import, unicode_literals

import operator
import threading
from builtins import range, str
from functools import reduce
from django.conf import settings

from django.contrib.auth.models import User
from django.db import models
from django.db.models import (Case, CharField, F, Func, IntegerField, Q, Value, When)
from django.db.models.expressions import Subquery, OuterRef
from django.db.models.fields import TextField
from django.db.models.functions import Coalesce, Concat, Length, Substr
#import Levenshtein_search
import re

from voyage.models import Place, Voyage, VoyageSources
#from common.validators import date_csv_field_validator

# Levenshtein-distance based search with ranked results.
# https://en.wikipedia.org/wiki/Levenshtein_distance

'''
# function obtained from
# https://stackoverflow.com/questions/517923/
# what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = unidecode.unidecode(text)
    return text.replace(',', '').lower()


class NameSearchCache:
    _loaded = False
    _lock = threading.Lock()
    _index = None
    _name_key = {}
    _sound_recordings = {}
    
    @staticmethod
    def get_composite_names(name):
        yield name
        parts = re.split("\\s*,\\s*|\\s+", name)
        if len(parts) == 2:
            yield parts[1] + " " + parts[0]
        for part in parts:
            yield part

    @classmethod
    def get_recordings(cls, names):
        rec = cls._sound_recordings
        return {
            name: rec[name]
            for name in names
            if name is not None and name in rec
        }

    @classmethod
    def search(cls, name, max_cost=3, max_results=100):
        res = cls.search_full(name, max_cost, max_results)
        return [id for x in res for id in x[0]]

    @classmethod
    def search_full(cls, name, max_cost, max_results):
        res = sorted(Levenshtein_search.lookup(0, strip_accents(name),
                                               max_cost),
                     key=lambda x: x[1])
        return [(cls._name_key[x[0]], x[1], x[0]) for x in res[0:max_results]]

    @classmethod
    def load(cls, force_reload=False):
        with cls._lock:
            if not force_reload and cls._loaded:
                return
            Levenshtein_search.clear_wordset(0)
            cls._name_key = {}
            all_names = set()
            q = Enslaved.objects.values_list('enslaved_id', 'documented_name',
                                             'name_first', 'name_second',
                                             'name_third')

            for item in q:
                ns = {
                    strip_accents(part)
                    for i in range(1, len(item)) if item[i] is not None
                    for part in NameSearchCache.get_composite_names(item[i])
                }
                all_names.update(ns)
                item_0 = item[0]
                for name in ns:
                    ids = cls._name_key.setdefault(name, [])
                    ids.append(item_0)
            Levenshtein_search.populate_wordset(0, list(all_names))
            q = EnslavedName.objects.values_list('id', 'name', 'language',
                                                 'recordings_count')
            for item in q:
                current = cls._sound_recordings.setdefault(item[1], {})
                langs = current.setdefault('langs', [])
                lang = {}
                lang['lang'] = item[2]
                lang['id'] = item[0]
                lang['records'] = [
                    f'0{item[0]}.{item[2]}.{index}.mp3'
                    for index in range(1, 1 + item[3])
                ]
                langs.append(lang)
            cls._loaded = True
'''

class EnslaverInfoAbstractBase(models.Model):
    principal_alias = models.CharField(max_length=255)

    # Personal info.
    birth_year = models.IntegerField(null=True)
    birth_month = models.IntegerField(null=True)
    birth_day = models.IntegerField(null=True)
    birth_place = models.CharField(max_length=255, null=True)

    death_year = models.IntegerField(null=True)
    death_month = models.IntegerField(null=True)
    death_day = models.IntegerField(null=True)
    death_place = models.CharField(max_length=255, null=True)

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
    principal_location=models.ForeignKey(Place, null=True,
                                                on_delete=models.CASCADE,
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


class EnslaverMerger(EnslaverInfoAbstractBase):
    """
    Represents a merger of two or more identities.
    We inherit from EnslaverInfoAbstractBase so that all personal fields
    are also contained in the merger.
    """
    comments = models.CharField(max_length=1024)


class EnslaverMergerItem(models.Model):
    """
    Represents a single identity that is part of a merger.
    """
    merger = models.ForeignKey('EnslaverMerger',
                               null=False,
                               on_delete=models.CASCADE)
    # We do not use a foreign key to the identity since if the merger
    # is accepted, some/all of the records may be deleted and the keys
    # would either be invalid or set to null.
    enslaver_identity_id = models.IntegerField(null=False)


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
                                       on_delete=models.CASCADE)
    voyage = models.ForeignKey('voyage.Voyage',
                               null=False,
                               on_delete=models.CASCADE)
    role = models.IntegerField(null=False)
    # There might be multiple persons with the same role for the same voyage
    # and they can be ordered (ranked) using the following field.
    order = models.IntegerField(null=True)
    # NOTE: we will have to substitute VoyageShipOwner and VoyageCaptain
    # models/tables by this entity.


class NamedModelAbstractBase(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return str(self.id) + ", " + self.name

    class Meta:
        abstract = True


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
    pass

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
                                     on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    order = models.IntegerField()
    notes = models.CharField(max_length=255, null=True, blank=True)


class EnslavedContributionLanguageEntry(models.Model):
    contribution = models.ForeignKey(EnslavedContribution,
                                     on_delete=models.CASCADE)
    language_group = models.ForeignKey(LanguageGroup, null=True,
                                       on_delete=models.CASCADE)
    order = models.IntegerField()
    notes = models.CharField(max_length=255, null=True, blank=True)


class EnslavedName(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    language = models.CharField(max_length=3, null=False, blank=False)
    recordings_count = models.IntegerField()

    class Meta:
        unique_together = ('name', 'language')

class EnslavementRelationType(models.Model):
	relation_type=models.CharField(max_length=255, null=False)

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
    transaction = models.ForeignKey(
        EnslavementRelation,
        related_name="enslaved_person",
        null=False,
        on_delete=models.CASCADE)
    enslaved = models.ForeignKey(Enslaved,
        related_name="transactions",
        null=False,
        on_delete=models.CASCADE)

class EnslaverRole(models.Model):
	role=models.CharField(max_length=255, null=True)

class EnslaverInRelation(models.Model):
    """
    Associates an enslaver in a slave relation.
    """

    id = models.IntegerField(primary_key=True)
    transaction = models.ForeignKey(
        EnslavementRelation,
        related_name="enslavers",
        null=False,
        on_delete=models.CASCADE)
    enslaver_alias = models.ForeignKey(
     	EnslaverAlias,
       	related_name="transactions",
    	null=False,
    	on_delete=models.CASCADE)
    role = models.ForeignKey(EnslaverRole,null=True, help_text="The role of the enslaver in this relation",on_delete=models.CASCADE)

