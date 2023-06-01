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
from voyage.models import Voyage, VoyageDataset, VoyageSources,Place
import re
from common.models import NamedModelAbstractBase
# from geo.models import Location

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
    birth_year = models.IntegerField(null=True)
    birth_month = models.IntegerField(null=True)
    birth_day = models.IntegerField(null=True)
    birth_place = models.ForeignKey(Place, null=True, on_delete=models.SET_NULL, related_name='+')

    death_year = models.IntegerField(null=True)
    death_month = models.IntegerField(null=True)
    death_day = models.IntegerField(null=True)
    death_place = models.ForeignKey(Place, null=True, on_delete=models.SET_NULL, related_name='+')

    father_name = models.CharField(max_length=255, null=True)
    father_occupation = models.CharField(max_length=255, null=True)
    mother_name = models.CharField(max_length=255, null=True)

    # We will include the spouses in the Enslaver table and use
    # EnslavementRelation to join the individuals by a marriage
    # relationship.
    # first_spouse_name = models.CharField(max_length=255, null=True)
    # first_marriage_date = models.CharField(max_length=12, null=True)
    # second_spouse_name = models.CharField(max_length=255, null=True)
    # second_marriage_date = models.CharField(max_length=12, null=True)
	
    probate_date = models.CharField(max_length=12, null=True)
    will_value_pounds = models.CharField(max_length=12, null=True)
    will_value_dollars = models.CharField(max_length=12, null=True)
    will_court = models.CharField(max_length=12, null=True)
    principal_location = models.ForeignKey(Place, null=True,
                                                on_delete=models.CASCADE,
                                                db_index=True)
    notes = models.CharField(null=True, max_length=8192)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "Enslaver info: " + self.principal_alias
	 
    class Meta:
        abstract = True


class EnslaverIdentity(EnslaverInfoAbstractBase):

    class Meta:
        verbose_name = 'Enslaver unique identity and personal info'


class PropHelper:
    """
    A helper structure to index property values by id and key.
    """

    def __init__(self):
        self.data = {}

    def add_num(self, id, key, num):
        if num is None:
            return
        self.set_or_replace(id, key, lambda prev: num + (prev or 0))

    def add_to_set(self, id, key, val):
        if val is None:
            return
        self.set_or_replace(id, key, lambda prev: {val}.union(prev or set()))

    def set(self, id, key, val):
        if val is None:
            return
        self.set_or_replace(id, key, lambda _: val)

    def set_or_replace(self, id, key, update_fn):
        item = self.data.setdefault(id, {})
        item[key] = update_fn(item.get(key, None))

class BitOrAgg(Aggregate):
    function = 'BIT_OR'
    name = 'BitOr'


class BitsAndFunc(Func):
    """
    This custom func applies the binary AND to the two expressions and checks
    for a positive value (indicating bit intersection).
    """
    arity = 2
    arg_joiner = ' & '
    template = '(%(expressions)s)'


class Lower(Func):
    function = 'LOWER'


class PowerFunc(Func):
    arity = 2
    function = 'POWER'
    arg_joiner = ','
    template = 'POWER(%(expressions)s)'


class RemoveNonAlphaChars(Func):
    arity = 1
    function = 'REGEXP_REPLACE'
    arg_joiner = ','
    template = r"""REGEXP_REPLACE(%(expressions)s, '[^[[:alpha:]]]', '')"""


class EnslaverCachedProperties(models.Model):
    identity = models.OneToOneField(EnslaverIdentity, related_name='cached_properties',
                                on_delete=models.CASCADE, primary_key=True)
    enslaved_count = models.IntegerField(db_index=True)
    transactions_amount = models.DecimalField(db_index=True, null=False, default=0, decimal_places=2, max_digits=6)
    # Enumerate all the distinct roles for an enslaver, using the PKs of the
    # Role enumeration separated by comma.
    roles = models.CharField(max_length=255, null=False, blank=True)
    first_year = models.IntegerField(db_index=True, null=True)
    last_year = models.IntegerField(db_index=True, null=True)
    # The voyage datasets that contain voyages associated with the enslavers. We
    # encode the aggregation as a bitwise OR of the powers of two of dataset values.
    voyage_datasets = models.IntegerField(db_index=True, null=True)
    # Store lexicographically smallest and largest aliases for each Enslaver.
    # This can then be used to sort
    min_alias = models.CharField(blank=True, db_index=True, max_length=255)
    max_alias = models.CharField(blank=True, db_index=True, max_length=255)

    @staticmethod
    def compute(identities=None):
        """
        Compute cached properties for the Enslaver. This method seeds the
        EnslaverCachedProperties table which can be used to search and sort
        enslavers based on aggregated values.
        """
        identity_field = 'enslaver_alias__identity__id'

        def apply_filter(q, matching_field=None):
            return q.filter(**{f"{matching_field or identity_field}__in": identities}) if identities is not None else q

        helper = PropHelper()
        voyage_year_field = 'voyage__voyage_dates__imp_arrival_at_port_of_dis'
        q_years = EnslaverVoyageConnection.objects \
            .select_related(voyage_year_field) \
            .values(identity_field) \
            .annotate(min_year=Min(voyage_year_field)) \
            .annotate(max_year=Max(voyage_year_field)) \
            .values_list(identity_field, 'min_year', 'max_year')
        q_years = apply_filter(q_years)

        def get_year(s):
            if s is None or len(s) < 4:
                return None
            try:
                return int(s[-4:])
            except:
                return None

        for row in q_years:
            helper.set(int(row[0]), 'min_year', get_year(row[1]))
            helper.set(int(row[0]), 'max_year', get_year(row[2]))

        # Process the alias field so that sorting behaves decently even with
        # some badly formatted entries we currently have (e.g. with question
        # marks, commas, digits etc)
        alias_field = RemoveNonAlphaChars(Lower(F('alias')))
        q_aliases = EnslaverAlias.objects \
            .values('identity_id') \
            .annotate(min_alias=Min(alias_field)) \
            .annotate(max_alias=Max(alias_field)) \
            .values_list('identity_id', 'min_alias', 'max_alias')
        q_aliases = apply_filter(q_aliases, 'identity_id')
        for row in q_aliases:
            helper.set(int(row[0]), 'min_alias', row[1])
            helper.set(int(row[0]), 'max_alias', row[2])

        q_datasets = EnslaverVoyageConnection.objects \
            .select_related('voyage__dataset') \
            .values(identity_field) \
            .annotate(datasets=BitOrAgg(PowerFunc(Value(2), F('voyage__dataset')))) \
            .values_list(identity_field, 'datasets')
        q_datasets = apply_filter(q_datasets)
        for row in q_datasets:
            helper.set(int(row[0]), 'datasets', int(row[1]))

        enslaved_count_field = 'voyage__voyage_slaves_numbers__imp_total_num_slaves_embarked'
        voyage_conn_fields = [identity_field, enslaved_count_field]
        # The number of captives associated with an Enslaver is obtained from
        # two sources: (1) the number of enslaved embarked in all voyages
        # associated with the enslaver; (2) enslaved people in a relationship
        # with the enslaver through the EnslavementRelation table.
        q_captive_count_voyageconn = EnslaverVoyageConnection.objects \
            .select_related(*voyage_conn_fields) \
            .values(identity_field) \
            .annotate(enslaved_count=Sum(enslaved_count_field)) \
            .values_list(identity_field, 'enslaved_count')
        q_captive_count_voyageconn = apply_filter(q_captive_count_voyageconn)
        related_enslaved_field = 'relation__enslaved__enslaved_id'
        relation_fields = [identity_field, related_enslaved_field]
        q_captive_count_relations = EnslaverInRelation.objects \
            .select_related(*relation_fields) \
            .values(identity_field) \
            .annotate(enslaved_count=Count(related_enslaved_field, distinct=True)) \
            .values_list(identity_field, 'enslaved_count')
        q_captive_count_relations = apply_filter(q_captive_count_relations)
        unnamed_count_field = 'relation__unnamed_enslaved_count'
        q_unnamed = EnslaverInRelation.objects \
            .select_related(identity_field, unnamed_count_field) \
            .annotate(enslaved_count=Sum(unnamed_count_field)) \
            .values_list(identity_field, 'enslaved_count')
        q_unnamed = apply_filter(q_unnamed)
        for row in q_captive_count_voyageconn:
            helper.add_num(int(row[0]), 'enslaved_count', row[1])
        for row in q_captive_count_relations:
            helper.add_num(int(row[0]), 'enslaved_count', row[1])
        for row in q_unnamed:
            helper.add_num(int(row[0]), 'enslaved_count', row[1])
        amount_fields = [identity_field, 'relation__amount']
        q_transaction_amount = EnslaverInRelation.objects \
            .select_related(*amount_fields) \
            .values(identity_field) \
            .annotate(amount_sum=Sum(amount_fields[1])) \
            .values_list(identity_field, 'amount_sum')
        q_transaction_amount = apply_filter(q_transaction_amount)
        for row in q_transaction_amount:
            helper.add_num(int(row[0]), 'tot_amount', row[1])
        q_roles = EnslaverInRelation.objects.values_list(identity_field, 'role')
        q_roles = apply_filter(q_roles)
        for row in q_roles:
            helper.add_to_set(int(row[0]), 'roles', row[1])
        q_roles = EnslaverVoyageConnection.objects.values_list(identity_field, 'role')
        q_roles = apply_filter(q_roles)
        for row in q_roles:
            helper.add_to_set(int(row[0]), 'roles', row[1])
        for id, item in helper.data.items():
            props = EnslaverCachedProperties()
            props.identity_id = id
            props.enslaved_count = item.get('enslaved_count', 0)
            # Note: we leave a comma after each number *on purpose*. This is so
            # we can search for roles by querying for contains "{role_id},".
            # Without the comma in the end, we could get false positives for ids
            # with multiple digits.
            props.roles = ''.join(sorted(f"{role}," for role in item.get('roles', [])))
            props.transactions_amount = item.get('tot_amount', 0)
            props.first_year = item.get('min_year', None)
            props.last_year = item.get('max_year', None)
            props.min_alias = item.get('min_alias', '')
            props.max_alias = item.get('max_alias', '')
            # Avoid blank entries messing up alias sorting with some hardcoded
            # balues that should place these last in their respective sorts.
            if props.min_alias == '':
                props.min_alias = 'zzzzzzzzzz'
            if props.max_alias == '':
                props.max_alias = 'aaaaaaaaaa'
            props.voyage_datasets = item.get('datasets', 0)
            yield props

    @staticmethod
    def update():
        with transaction.atomic():
            # Delete all cached entries first to avoid duplicate primary key
            # errors (note that this model's PK is also a FK).
            EnslaverCachedProperties.objects.all().delete()
            EnslaverCachedProperties.objects.bulk_create(__class__.compute())


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
    manual_id = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "EnslaverAlias: " + self.alias

    class Meta:
        verbose_name = 'Enslaver alias'


class EnslaverRole(NamedModelAbstractBase):
    pass


class EnslaverVoyageConnection(models.Model):
    """
    Associates an enslaver with a voyage at some particular role.
    """

    enslaver_alias = models.ForeignKey(EnslaverAlias,
                                       null=False,
                                       on_delete=models.CASCADE)
    voyage = models.ForeignKey('voyage.Voyage',
                               null=False,
                               on_delete=models.CASCADE)
    role = models.ForeignKey(EnslaverRole, null=False, on_delete=models.CASCADE)
    # There might be multiple persons with the same role for the same voyage
    # and they can be ordered (ranked) using the following field.
    order = models.IntegerField(null=True)
    # NOTE: we will have to substitute VoyageShipOwner and VoyageCaptain
    # models/tables by this entity.
    # leaving this line below for later cleanup when the migration is finished.
    # settings.VOYAGE_ENSLAVERS_MIGRATION_STAGE


# class VoyageCaptainOwnerHelper:
#     """
#     A simple helper class to fetch enslavers associated with a voyage based on
#     their role.
#     """
# 
#     _captain_through_table = Voyage.voyage_captain.through._meta.db_table
#     _owner_through_table = Voyage.voyage_ship_owner.through._meta.db_table
# 
#     def __init__(self):
#         self.owner_role_ids = list( \
#             EnslaverRole.objects.filter(name__icontains='owner').values_list('pk', flat=True))
#         self.captain_role_ids = list( \
#             EnslaverRole.objects.filter(name__icontains='captain').values_list('pk', flat=True))
# 
# 
#     class UniqueHelper:
#         """
#         A little helper that allows appending to a list only if the items
#         (names) are unique while maintaining the insertion order.
#         """
# 
#         def __init__(self):
#             self.all = []
#             self.unique = set()
#         
#         def append(self, iterable):
#             for x in iterable:
#                 if x not in self.unique:
#                     self.unique.add(x)
#                     self.all.append(x)
#     
#             
#     def get_captains(self, voyage):
#         h = self.UniqueHelper()
#         if settings.VOYAGE_ENSLAVERS_MIGRATION_STAGE <= 2:
#             # Fetch from the LEGACY table.
#             h.append(c.name for c in \
#                 voyage.voyage_captain.order_by(f"{self.__class__._captain_through_table}.captain_order"))
#         if settings.VOYAGE_ENSLAVERS_MIGRATION_STAGE >= 2:
#             # Fetch from EnslaversVoyageConnection.
#             h.append(self.__class__.get_all_with_roles(voyage, self.captain_role_ids))
#         # Dedupe names.
#         return h.all
# 
#     def get_owners(self, voyage):
#         h = self.UniqueHelper()
#         if settings.VOYAGE_ENSLAVERS_MIGRATION_STAGE <= 2:
#             # Fetch from the LEGACY table.
#             h.append(c.name for c in \
#                 voyage.voyage_ship_owner.order_by(f"{self.__class__._owner_through_table}.owner_order"))
#         if settings.VOYAGE_ENSLAVERS_MIGRATION_STAGE >= 2:
#             # Fetch from EnslaversVoyageConnection.
#             h.append(self.__class__.get_all_with_roles(voyage, self.owner_role_ids))
#         # Dedupe names.
#         return h.all
# 
#     @staticmethod
#     def get_all_with_roles(voyage, roles):
#         for ens in voyage.enslavers:
#             if ens.role_id in roles:
#                 yield ens.enslaver_alias.alias


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
    enslaved_id = models.IntegerField(primary_key=True)

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
                                                db_index=True,
                                                related_name='+')
    last_known_date = models.CharField(
        max_length=10,

        blank=True,
        null=True,
        help_text="Date in format: MM,DD,YYYY")
    captive_fate = models.ForeignKey(CaptiveFate, null=True, on_delete=models.SET_NULL, db_index=True)
    captive_status = models.ForeignKey(CaptiveStatus, null=True, on_delete=models.SET_NULL, db_index=True)
    voyage = models.ForeignKey(Voyage, null=False, on_delete=models.CASCADE, db_index=True)
    dataset = models.IntegerField(null=False, default=0, db_index=True)
    notes = models.CharField(null=True, max_length=8192)
    sources = models.ManyToManyField(VoyageSources,
                                     through='EnslavedSourceConnection',
                                     related_name='+')


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

#this was causing a conflict in the migration to the new db
#i think a unicode issue
#     class Meta:
#         unique_together = ('name', 'language')


class EnslavementRelationType(NamedModelAbstractBase):
    pass


class EnslavementRelation(models.Model):
    """
    Represents a relation involving any number of enslavers and enslaved
    individuals.
    """
    
    id = models.IntegerField(primary_key=True)
    relation_type = models.ForeignKey(EnslavementRelationType, null=False, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, null=True, on_delete=models.SET_NULL, related_name='+')
    date = models.CharField(max_length=12, null=True,
        help_text="Date in MM,DD,YYYY format with optional fields.")
    amount = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    unnamed_enslaved_count = models.IntegerField(null=True)
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
    relation = models.ForeignKey(
        EnslavementRelation,
        related_name="enslaved",
        null=False,
        on_delete=models.CASCADE)
    enslaved = models.ForeignKey(Enslaved,
        related_name="relations",
        null=False,
        on_delete=models.CASCADE)


class EnslaverInRelation(models.Model):
    """
    Associates an enslaver in a slave relation.
    """

    id = models.IntegerField(primary_key=True)
    relation = models.ForeignKey(
        EnslavementRelation,
        related_name="enslavers",
        null=False,
        on_delete=models.CASCADE)
    enslaver_alias = models.ForeignKey(EnslaverAlias, null=False, on_delete=models.CASCADE)
    role = models.ForeignKey(EnslaverRole, null=False, on_delete=models.CASCADE, help_text="The role of the enslaver in this relation")

# 
# class EnslavementBipartiteGraph:
#     """
#     A cache of the bipartite graph connecting enslaved to its enslavers.
#     """
#     _enslaved_to_enslavers: "dict[int, set[int]]" = dict()
#     _enslavers_principal_alias: "dict[int, str]" = dict()
#     _lock = threading.Lock()
#     _init = False
# 
#     @classmethod
#     def load(cls, force_reload=False):
#         with cls._lock:
#             if force_reload or not cls._init:
#                 enslaved_to_rel = {}
#                 relation_ids = set()
#                 q_enslaved = EnslavedInRelation.objects.values_list('relation_id', 'enslaved_id')
#                 for rel_id, enslaved_id in q_enslaved:
#                     relation_ids.add(rel_id) ; enslaved_to_rel.setdefault(enslaved_id, set()).add(rel_id)
# 
#                 enslavers_by_rel = {}
#                 q_enslavers = EnslaverInRelation.objects.select_related('enslaver_alias__identity_id').values_list('relation_id', 'enslaver_alias__identity_id')
#                 for rel_id, enslaver_id in q_enslavers:
#                     if rel_id in relation_ids: enslavers_by_rel.setdefault(rel_id, set()).add(enslaver_id)
# 
#                 bipartite = {}
#                 for enslaved_id, relations in enslaved_to_rel.items():
#                     bipartite[enslaved_id] = set(enslaver_id for rel_id in relations for enslaver_id in enslavers_by_rel.get(rel_id, []))
#                 cls._enslaved_to_enslavers = bipartite
#                 cls._enslavers_principal_alias = {int(x[0]): x[1] for x in EnslaverIdentity.objects.values_list('id', 'principal_alias')}
#                 cls._init = True
#                 return bipartite
# 
#     @clssmethod
#     def get_top_enslavers(cls, enslaved_ids: "Iterable[int]", n = 5):
#         counts : "dict[int, int]" = {}
#         for enslaved_id in enslaved_ids:
#             for enslaver_id in cls._enslaved_to_enslavers.get(enslaved_id, []):
#                 counts[enslaver_id] = counts.get(enslaver_id, 0) + 1
#         return [(item[0], cls._enslavers_principal_alias.get(item[0]), item[1]) 
#                 for item in sorted(counts.items(), key=lambda x: -x[1])[:n]]


_special_empty_string_fields = {
    'voyage__voyage_ship__ship_name': 1,
    'voyage__voyage_dates__first_dis_of_slaves': '2',
    'notes': 1
}

_name_fields = ['documented_name', 'name_first', 'name_second', 'name_third']
# Note: we started with three modern name fields, but it
# was decided (2021-10-05) to drop all but one.
_modern_name_fields = ['modern_name']


class MultiValueHelper:
    """
    This helper uses the GROUP_CONCAT function to fetch multiple values as a
    single string value for the query and supports mapping this single string
    back to a structure (list of dicts, or list of flat values if only one field
    mapping is used).
    """

    _FIELD_SEP = "#@@@#"
    _GROUP_SEP = "@###@"
    _FIELD_SEP_VALUE = Value(_FIELD_SEP)

    def __init__(self, projected_name, m2m_connection_model, fk_name, data_adapter = None, group_adapter = None, **field_mappings):
        self.field_mappings = field_mappings
        self.projected_name = projected_name
        self.model = m2m_connection_model
        self.fk_name = fk_name
        self.data_adapter = data_adapter
        self.group_adapter = group_adapter

    def adapt_query(self, q):
        """
        This method adapts the query by including a computed field aliased "projected_name".
        The computed field groups multiple related rows and field by concatenating them into
        a single string. The parse_group method can be used to parse this concatenated
        string and obtain a list of dictionaries, where each entry corresponds to the fields
        in a related row.
        """
        fields_concatenated = []
        for field_map in self.field_mappings.values():
            fields_concatenated.append(F(field_map) if isinstance(field_map, str) else field_map)
            fields_concatenated.append(self._FIELD_SEP_VALUE)
        # Drop the last entry which is a field separator.
        fields_concatenated.pop()
        group_concat_field = Func(
            Concat(*fields_concatenated, output_field=TextField()) if len(fields_concatenated) > 1 else fields_concatenated[0],
            # This value and the arg_joiner is needed so that the ORM produces the right syntax
            # for GROUP_CONCAT(CONCAT(<FieldsToConcatenate>) SEPARATOR <quoted _GROUP_SEP>).
            Value(self._GROUP_SEP),
            template = "%(function)s(DISTINCT %(expressions)s)",
            arg_joiner=" SEPARATOR ",
            function='GROUP_CONCAT')
        sub_query = self.model.objects.filter(**{ self.fk_name: OuterRef('pk') }) \
            .annotate(group_concat_field=group_concat_field) \
            .values('group_concat_field')
        return q.annotate(**{ self.projected_name: Subquery(sub_query) })

    def parse_grouped(self, value):
        """
        Produce an iterable of dicts by parsing the field produced by this helper.
        """
        flen = len(self.field_mappings)
        if value is None or flen == 0:
            return []
        res = []
        for item in value.split(self._GROUP_SEP):
            values = item.split(self._FIELD_SEP)
            if len(values) == flen:
                if self.data_adapter:
                    values = self.data_adapter(values)
                if values is None:
                    continue
                # Return a dict when multiple values are mapped otherwise return just the value.
                res.append({ name: values[index] for (index, name) in enumerate(self.field_mappings.keys()) } if flen > 1 else values[0])
        if self.group_adapter:
            res = self.group_adapter(res)
        return res if res is not None else []

    def patch_row(self, row):
        """
        For a dict row that is obtained by executing the query with the GROUP_CONCAT in this
        helper, patch the projected name to contain a list of entries, each being a dict
        corresponding to an associated entry.
        """
        if self.projected_name in row:
            row[self.projected_name] = self.parse_grouped(row[self.projected_name])
        else:
            row[self.projected_name] = []
        return row

    @staticmethod
    def set_group_concat_limit(limit=1000000):
        """
        MySQL has a parameter that controls how much data can be produced by a
        GROUP_CONCAT statement. Since GROUP_CONCAT is the main mechanism we use
        in this helper to produce complex nested data in the query output
        without requiring multiple roundtrips to the database, a low limit for
        this parameter could mean that the number of nested entries returned is
        truncated.
        """
        with connection.cursor() as cursor:
            cursor.execute(f'SET SESSION group_concat_max_len = {int(limit)};')


class NullIf(Func):
    # TODO (Django update): this is implemented in latest version of Django...
    function = 'NULLIF'
    arity = 2


def _auto_select_related_fields(q, fields):
    """
    For performance reasons it is better if we detect all the fields that are
    related to the main model and force the ORM to select them in the query
    (otherwise, they would need to be fetched by separate queries). We use the
    convention of double underscores in related field names to detect those
    fields and extract only the part that needs to be passed to
    select_related().
    """
    related = list({f[:i] for (f, i) in [(f, f.rfind('__')) for f in fields] if i > 0})
    return q.select_related(*related)


def _year_range_conv(range):
    """
    When searching by year on CSV date-value fields, apply this conversion.
    """
    return [',,' + str(y) for y in range]

def single_val(source):
    try:
        if isinstance(source, list):
            source = source[0]
    except:
        pass
    return source


class PivotTableDefinition:
    AGG_COUNT = 'COUNT'
    AGG_SUM = 'SUM'

    def __init__(self, row_fields, agg_field, agg_mode=AGG_COUNT):
        self.row_fields = row_fields
        self.agg_field = F(agg_field) if isinstance(agg_field, str) else agg_field
        self.agg_mode = agg_mode

    def adapt_query(self, model, query):
        # The query is  used to select the results from which a pivot table will
        # be built. We use it as an inner query and let the db do the
        # aggregation over it.
        ptq = model.objects.filter(pk__in=Subquery(query.values('pk')))
        ptq = ptq.values(**{k: F(v) if isinstance(v, str) else v for k, v in self.row_fields.items()})
        aggregator = self.agg_field
        if self.agg_mode == PivotTableDefinition.AGG_COUNT:
            aggregator = Count(aggregator, distinct=True)
        if self.agg_mode == PivotTableDefinition.AGG_SUM:
            aggregator = Sum(aggregator)
        ptq = ptq.annotate(cell=aggregator)
        return ptq


class EnslavedSearch:
    """
    Search parameters for enslaved persons.
    """

    SOURCES_LIST = "sources_list"
    ENSLAVERS_LIST = "enslavers_list"

    sources_helper = MultiValueHelper(
        SOURCES_LIST,
        EnslavedSourceConnection,
        'enslaved_id',
        text_ref="text_ref",
        full_ref="source__full_ref")
    enslavers_helper = MultiValueHelper(
        ENSLAVERS_LIST,
        EnslavedInRelation,
        'enslaved_id',
        enslaver_name="relation__enslavers__enslaver_alias__alias",
        relation_date="relation__date",
        enslaver_role="relation__enslavers__role__name")

    all_helpers = [sources_helper, enslavers_helper]

    def __init__(self,
                 enslaved_dataset=None,
                 searched_name=None,
                 exact_name_search=False,
                 gender=None,
                 age_range=None,
                 height_range=None,
                 year_range=None,
                 embarkation_ports=None,
                 disembarkation_ports=None,
                 post_disembark_location=None,
                 language_groups=None,
                 ship_name=None,
                 voyage_id=None,
                 enslaved_id=None,
                 source=None,
                 order_by=None,
                 voyage_dataset=None,
                 skin_color=None,
                 vessel_fate=None,
                 pivot_table=None):
        """
        Search the Enslaved database. If a parameter is set to None, it will not
        be included in the search. @param: enslaved_dataset The enslaved dataset
        to be searched
                (either None to search all or an integer code).
        @param: searched_name A name string to be searched @param:
        exact_name_search Boolean indicating whether the search is
                exact or fuzzy
        @param: gender The gender ('male' or 'female'). @param: age_range A pair
        (a, b) where a is the min and b is maximum age @param: height_range A
        pair (a, b) where a is the min and b is maximum
                height
        @param: year_range A pair (a, b) where a is the min voyage year and b
                the max
        @param: embarkation_ports A list of port ids where the enslaved
                embarked
        @param: disembarkation_ports A list of port ids where the enslaved
                disembarked
        @param: post_disembark_location A list of place ids where the enslaved
                was located after disembarkation
        @param: language_groups A list of language groups ids for the enslaved
        @param: ship_name The ship name that the enslaved embarked @param:
        voyage_id A pair (a, b) where the a <= voyage_id <= b @param:
        enslaved_id A pair (a, b) where the a <= enslaved_id <= b @param: source
        A text fragment that should match Source's text_ref or
                full_ref
        @param: order_by An array of dicts {
                'columnName': 'NAME', 'direction': 'ASC or DESC' }. Note that if
                the search is fuzzy, then the fallback value of order_by is the
                ranking of the fuzzy search.
        @param: voyage_dataset A list of voyage datasets that restrict the
        search. @param: skin_color a textual description for skin color (Racial
        Descriptor) @param: vessel_fate a list of fates for the associated
        voyage vessel.
        @param: pivot_table is the specification for the aggregation of data in
        a pivot table. The search filters will be applied to the Enslaved and
        then the aggregation will only take place over matches.
        """
        self.enslaved_dataset = single_val(enslaved_dataset)
        self.searched_name = single_val(searched_name)
        self.exact_name_search = single_val(exact_name_search)
        self.gender = single_val(gender)
        self.age_range = age_range
        self.height_range = height_range
        self.year_range = year_range
        self.embarkation_ports = embarkation_ports
        self.disembarkation_ports = disembarkation_ports
        self.post_disembark_location = post_disembark_location
        self.language_groups = language_groups
        self.ship_name = single_val(ship_name)
        self.voyage_id = voyage_id
        self.enslaved_id = enslaved_id
        self.source = single_val(source)
        self.order_by = order_by or [{'columnName': 'pk', 'direction': 'asc'}]
        self.voyage_dataset = voyage_dataset
        self.skin_color = single_val(skin_color)
        self.vessel_fate = vessel_fate
        self.pivot_table = pivot_table


    def get_order_for_field(self, field):
        if isinstance(self.order_by, list):
            for x in self.order_by:
                if x['columnName'] == field:
                    return x['direction']
        return None

    def execute(self, fields):
        """
        Execute the search and output an enumerable of dictionaries, each
        representing an Enslaved record.
        @param: fields A list of fields that are fetched.
        """
        q = Enslaved.objects

        ranking = None
        is_fuzzy = False
        if self.searched_name and len(self.searched_name):
            if self.exact_name_search:
                qmask = Q(documented_name__icontains=self.searched_name)
                qmask |= Q(name_first__icontains=self.searched_name)
                qmask |= Q(name_second__icontains=self.searched_name)
                qmask |= Q(name_third__icontains=self.searched_name)
                q = q.filter(qmask)
            else:
                # Perform a fuzzy search on our cached names.
                EnslavedNameSearchCache.load()
                fuzzy_ids = EnslavedNameSearchCache.search(self.searched_name)
                if len(fuzzy_ids) == 0:
                    return []
                ranking = {x[1]: x[0] for x in enumerate(fuzzy_ids)}
                q = q.filter(pk__in=fuzzy_ids)
                is_fuzzy = True
                if 'enslaved_id' not in fields:
                    fields.append('enslaved_id')
        if self.gender:
            gender_val = 1 if self.gender == 'male' else 2
            q = q.filter(gender=gender_val)
        if self.voyage_dataset:
            conditions = [Q(voyage__dataset=VoyageDataset.parse(x)) for x in self.voyage_dataset]
            q = q.filter(reduce(operator.or_, conditions))
        if self.enslaved_dataset is not None:
            q = q.filter(dataset=self.enslaved_dataset)
        if self.age_range:
            q = q.filter(age__range=self.age_range)
        if self.height_range:
            q = q.filter(height__range=self.height_range)
        if self.post_disembark_location:
            q = q.filter(
                post_disembark_location__pk__in=self.post_disembark_location)
        if self.source:
            qmask = Q(sources_conn__text_ref__icontains=self.source)
            qmask |= Q(sources__full_ref__icontains=self.source)
            q = q.filter(qmask)
        if self.voyage_id:
            q = q.filter(voyage__pk__range=self.voyage_id)
        if self.enslaved_id:
            q = q.filter(pk__range=self.enslaved_id)
        if self.year_range:
            # Search on YEARAM field. Note that we have a 'MM,DD,YYYY' format
            # even though the only year should be present.
            q = q.filter(
                voyage__voyage_dates__imp_arrival_at_port_of_dis__range=_year_range_conv(self.year_range))
        if self.embarkation_ports:
            # Search on MJBYPTIMP field.
            q = q.filter(
                voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__pk__in=self.embarkation_ports)
        if self.disembarkation_ports:
            # Search on MJSLPTIMP field.
            q = q.filter(
                voyage__voyage_itinerary__imp_principal_port_slave_dis__pk__in=self.disembarkation_ports)
        if self.language_groups:
            q = q.filter(language_group__pk__in=self.language_groups)
        if self.ship_name:
            q = q.filter(
                voyage__voyage_ship__ship_name__icontains=self.ship_name)
        if self.vessel_fate:
            q = q.filter(
                voyage__voyage_name_outcome__vessel_captured_outcome__value__in=self.vessel_fate)
        if self.skin_color:
            q = q.filter(skin_color__icontains=self.skin_color)

        order_by_ranking = 'asc'
        if isinstance(self.order_by, list):
            order_by_ranking = None
            for x in self.order_by:
                if is_fuzzy and x['columnName'] == 'ranking':
                    order_by_ranking = x['direction']
                    break
            orm_orderby = []
            for x in self.order_by:
                col_name = x['columnName']
                if col_name == 'ranking':
                    continue
                is_desc = x['direction'].lower() == 'desc'
                nulls_last = True
                order_field = F(col_name)
                empty_string_field_min_char_len = _special_empty_string_fields.get(col_name)
                if empty_string_field_min_char_len:
                    nulls_last = True
                    # Add a "length > min_char_len_for_field" field and sort it
                    # first. Note that we use a non-zero value for
                    # min_char_len_for_field because some fields uses a string
                    # ' ' to represent blank entries while some date fields use
                    # ',,' to represent a blank date.
                    count_field = 'count_' + col_name
                    isempty_field = 'isempty_' + col_name
                    q = q.annotate(**{count_field: Length(order_field)})
                    q = q.annotate(**{
                        isempty_field:
                            Case(
                                When(**{
                                    'then': Value(1),
                                    count_field + '__gt':
                                        empty_string_field_min_char_len
                                }),
                                default=Value(0),
                                output_field=IntegerField())})
                    orm_orderby.append('-' + isempty_field)
                    if 'date' in col_name:
                        # The date formats MM,DD,YYYY with possible blank
                        # values are very messy to sort. Here we add sorting by
                        # the last 4 characters to first sort by year (which is
                        # always present for non blank dates).
                        year_field = 'yearof_' + col_name
                        q = q.annotate(
                            **{
                                year_field:
                                Substr(order_field, 4 * Value(-1), 4)})
                        orm_orderby.append((
                            '-' if is_desc else '') + year_field)

                def add_names_sorting(sorted_name_fields, col_name, q,
                                      is_desc=is_desc):
                    # The next lines create a list made of the name fields with
                    # a separator constant value between each consecutive pair.
                    names_sep = Value(';')
                    names_concat = [names_sep] * \
                        (2 * len(sorted_name_fields) - 1)
                    names_concat[0::2] = sorted_name_fields
                    # We now properly handle empty/null values in sorting.
                    fallback_name_val = Value('AAAAA' if is_desc else 'ZZZZZ')
                    expressions = [
                        Coalesce(NullIf(NullIf(F(name_field), Value('')), Value('?')),
                                 fallback_name_val,
                                 output_field=CharField())
                        for name_field in sorted_name_fields
                    ]
                    q = q.annotate(**{
                        col_name:
                            Func(*expressions,
                                function='GREATEST' if is_desc else 'LEAST'
                                ) if len(expressions) > 1 else expressions[0]
                    })
                    order_field = F(col_name)
                    order_field = order_field.desc(
                    ) if is_desc else order_field.asc()
                    return q, order_field

                if col_name == 'names':
                    col_name = '_names_sort'
                    (q, order_field) = add_names_sorting(
                        _name_fields, col_name, q)
                elif col_name == 'modern_names':
                    col_name = '_modern_names_sort'
                    (q,
                     order_field) = add_names_sorting(_modern_name_fields,
                                                      col_name, q)
                elif is_desc:
                    order_field = order_field.desc(nulls_last=nulls_last)
                else:
                    order_field = order_field.asc(nulls_last=nulls_last)
                if order_field:
                    orm_orderby.append(order_field)
            if orm_orderby:
                q = q.order_by(*orm_orderby)
            else:
                q = q.order_by('enslaved_id')

        if self.pivot_table:
            return self.pivot_table.adapt_query(Enslaved, q)

        # Save annotations to circumvent Django bug 28811 (see below).
        # https://code.djangoproject.com/ticket/28811
        aux_annotations = q.query.annotation_select.copy()
        MultiValueHelper.set_group_concat_limit()
        if is_fuzzy:
            main_query = _auto_select_related_fields(q, fields)
        else:
            q = q.annotate(pk=F('enslaved_id'))
            q = q.values('pk')
            main_query = _auto_select_related_fields(Enslaved.objects, fields)
        for helper in self.all_helpers:
            main_query = helper.adapt_query(main_query)
        main_query = main_query.values(*fields)
            # The next line is again due to Django bug 28811.
        main_query.query.annotation_select.update(aux_annotations)
        if is_fuzzy:
            # Convert the QuerySet to a concrete list and include the ranking
            # as a member of each object in that list.
            q = list(main_query)
            for x in q:
                x['ranking'] = ranking[x['enslaved_id']]
            if order_by_ranking:
                q = sorted(q,
                           key=lambda x: x['ranking'],
                           reverse=(order_by_ranking == 'desc'))
        else:
            (count_query_str, count_params) = q.order_by().distinct().query.sql_with_params()
            q = q.distinct()
            # The next line is again due to Django bug 28811.
            q.query.annotation_select.update(aux_annotations)
            (match_query_str, match_params) = q.query.sql_with_params()
            (main_query_str, main_params) = main_query.query.sql_with_params()
            full_query_str = f"{main_query_str} INNER JOIN ({match_query_str} LIMIT 0,0) AS matches ON matches.pk=past_enslaved.enslaved_id"
            data_query = Enslaved.objects.raw(full_query_str, main_params + match_params)
            q = RawQueryWrapper(data_query.query, EnslaverIdentity.objects.raw(count_query_str, count_params).query, fields)
        return q

    @classmethod
    def patch_row(cls, row):
        for helper in cls.all_helpers:
            row = helper.patch_row(row)
        return row


def _voyages_data_adapter(values):
    values[0] = int(values[0])
    try:
        values[5] = int(values[5])
    except:
        values[5] = None
    return values

def _split_id_and_name(s, name_field):
    match = re.match('([0-9]+)\|(.*)', s)
    return {'id': int(match[1]), name_field: match[2]} if match else None

def _relations_group_adapter(rel_group):
    relations = {}
    for r in rel_group:
        rid = int(r['relation_id'])
        current = relations.get(rid)
        if current is None:
            current = { 'relation_id': rid }
            relations[rid] = current
        current['role'] = r['role']
        current['date'] = r['relation_date']
        cur_enslavers = current.setdefault('enslavers', {})
        enslaver = _split_id_and_name(r['relation_enslaver'], 'alias')
        if enslaver:
            cur_enslavers[enslaver['id']] = enslaver
        cur_enslaved = current.setdefault('enslaved', {})
        enslaved = _split_id_and_name(r['relation_enslaved'], 'alias')
        if enslaved:
            cur_enslaved[enslaved['id']] = enslaved
    return [{k: list(v.values()) if type(v) is dict else v for k, v in r.items()} for r in relations.values()]


class EnslaverSearch:
    ALIASES_LIST = "alias_list"
    VOYAGES_LIST = "voyages_list"
    SOURCES_LIST = "sources_list"
    RELATIONS_LIST = "relations_list"

    aliases_helper = MultiValueHelper(
        ALIASES_LIST,
        EnslaverAlias,
        'identity_id',
        alias='alias')

    voyages_helper = MultiValueHelper(
        VOYAGES_LIST,
        EnslaverVoyageConnection,
        'enslaver_alias__identity_id',
        _voyages_data_adapter,
        voyage_id='voyage_id',
        role='role__name',
        ship_name='voyage__voyage_ship__ship_name',
        embarkation_port='voyage__voyage_itinerary__imp_principal_place_of_slave_purchase__place',
        disembarkation_port='voyage__voyage_itinerary__imp_principal_port_slave_dis__place',
        slaves_embarked='voyage__voyage_slaves_numbers__imp_total_num_slaves_embarked',
        voyage_year='voyage__voyage_dates__imp_arrival_at_port_of_dis',
        alias='enslaver_alias__alias')

    sources_helper = MultiValueHelper(
        SOURCES_LIST,
        EnslaverIdentitySourceConnection,
        'identity_id',
        text_ref="text_ref",
        full_ref="source__full_ref")

    relations_helper = MultiValueHelper(
        RELATIONS_LIST,
        EnslaverInRelation,
        'enslaver_alias__identity_id',
        None,
        _relations_group_adapter,
        relation_id='relation_id',
        relation_date='relation__date',
        role='role__name',
        relation_enslaver=Concat(
            'relation__enslavers__enslaver_alias__identity_id',
            Value('|'),
            'relation__enslavers__enslaver_alias__alias',
            output_field='relation_enslaver_info'),
        relation_enslaved=Concat(
            'relation__enslaved__enslaved__enslaved_id',
            Value('|'),
            'relation__enslaved__enslaved__documented_name',
            output_field='relation_enslaved_info'))

    all_helpers = [aliases_helper, voyages_helper, sources_helper, relations_helper]

    def __init__(self,
                 searched_name=None,
                 exact_name_search=False,
                 year_range=None,
                 embarkation_ports=None,
                 disembarkation_ports=None,
                 departure_ports=None,
                 ship_name=None,
                 voyage_id=None,
                 source=None,
                 enslaved_count=None,
                 roles=None,
                 voyage_datasets=None,
                 order_by=None):
        """
        Search the Enslaver database. If a parameter is set to None, it will
        not be included in the search.
        @param: searched_name A name string to be searched
        @param: exact_name_search Boolean indicating whether the search is
                exact or fuzzy
        @param: voyage_dataset A list of voyage datasets that restrict the search.
        @param: year_range A pair (a, b) where a is the min voyage year and b
                the max
        @param: embarkation_ports A list of port ids where the enslaved
                embarked
        @param: disembarkation_ports A list of port ids where the enslaved
                disembarked
        @param: departure_ports A list of port ids where the voyage
                begin
        @param: ship_name The ship name that the enslaved embarked
        @param: voyage_id A pair (a, b) where the a <= voyage_id <= b
        @param: source A text fragment that should match Source's text_ref or
                full_ref
        @param: enslaved_count A pair (a, b) such that the enslaver has an
                associated enslaved count between a and b.
        @param: roles a list of role pks that should be matched (an enslaver may
                appear in multiple roles).
        @param: a list of Voyage datasets that should be used to match voyages 
                connected to the enslaver.
        @param: order_by An array of dicts {
                'columnName': 'NAME', 'direction': 'ASC or DESC' }.
                Note that if the search is fuzzy, then the fallback value of
                order_by is the ranking of the fuzzy search.
        """
        self.searched_name = single_val(searched_name)
        self.exact_name_search = single_val(exact_name_search)
        self.year_range = year_range
        self.embarkation_ports = embarkation_ports
        self.disembarkation_ports = disembarkation_ports
        self.departure_ports = departure_ports
        self.ship_name = single_val(ship_name)
        self.voyage_id = voyage_id
        self.source = single_val(source)
        self.enslaved_count = enslaved_count
        self.roles = roles
        self.voyage_datasets = voyage_datasets
        self.order_by = order_by or [{'columnName': 'pk', 'direction': 'asc'}]

    def execute(self, fields):
        """
        Execute the search and output an enumerable of dictionaries, each
        representing an Enslaved record.
        @param: fields A list of fields that are fetched.
        """
        q = EnslaverIdentity.objects

        ranking = None
        is_fuzzy = False
        if self.searched_name and len(self.searched_name):
            if self.exact_name_search:
                q = q.filter(aliases__alias__icontains=self.searched_name)
            else:
                # Perform a fuzzy search on our cached names.
                EnslaverNameSearchCache.load()
                fuzzy_ids = EnslaverNameSearchCache.search(self.searched_name)
                if len(fuzzy_ids) == 0:
                    return []
                ranking = {x[1]: x[0] for x in enumerate(fuzzy_ids)}
                q = q.filter(pk__in=fuzzy_ids)
                is_fuzzy = True
                if 'id' not in fields:
                    fields.append('id')

        if self.source:
            qmask = Q(enslaveridentitysourceconnection__text_ref__icontains=self.source)
            qmask |= Q(enslaveridentitysourceconnection__source__full_ref__icontains=self.source)
            q = q.filter(qmask)
        
        # Voyage related search fields: since an enslaver can be associated with
        # multiple voyages, it is enough to match any of them.
        voyage_search_prefix = 'aliases__enslavervoyageconnection__voyage__'

        def add_voyage_field(q, field, op, val):
            return q.filter(**{voyage_search_prefix + field + '__' + op: val })

        if self.voyage_id:
            q = add_voyage_field(q, 'pk', 'range', self.voyage_id)
        if self.ship_name:
            q = add_voyage_field(q, 'voyage_ship__ship_name', 'icontains', self.ship_name)
        if self.embarkation_ports:
            # Search on MJBYPTIMP field.
            q = add_voyage_field(q, 'voyage_itinerary__imp_principal_place_of_slave_purchase__pk', 'in', self.embarkation_ports)
        if self.disembarkation_ports:
            # Search on MJSLPTIMP field.
            q = add_voyage_field(q, 'voyage_itinerary__imp_principal_port_slave_dis__pk', 'in', self.disembarkation_ports)
        if self.departure_ports:
            # Search on PORTDEP field.
            q = add_voyage_field(q, 'voyage_itinerary__imp_port_voyage_begin__pk', 'in', self.departure_ports)
        if self.year_range:
            # Search on YEARAM field. Note that we have a 'MM,DD,YYYY' format
            # even though the only year should be present.
            q = add_voyage_field(q, 'voyage_dates__imp_arrival_at_port_of_dis', 'range', _year_range_conv(self.year_range))
        if self.enslaved_count:
            q = q.filter(cached_properties__enslaved_count__range=self.enslaved_count)
        if self.roles:
            terms = None
            for pk in self.roles:
                term = Q(cached_properties__roles__contains=f"{pk},")
                terms = (term | terms) if terms else term
            q = q.filter(terms)
        if self.voyage_datasets is not None:
            bitvec = 0
            for x in self.voyage_datasets:
                idx_dataset = VoyageDataset.parse(x)
                if idx_dataset < 0:
                    bitvec = 0
                    break
                bitvec |= 2 ** idx_dataset
            if bitvec > 0:
                q = q.annotate(voyage_datasets=BitsAndFunc('cached_properties__voyage_datasets', Value(bitvec)))
                q = q.filter(voyage_datasets__gt=0)
            else:
                q = q.filter(cached_properties__voyage_datasets=0)

        order_by_ranking = None
        orm_orderby = None
        if isinstance(self.order_by, list):
            order_by_ranking = None
            orm_orderby = []
            for x in self.order_by:
                col_name = x['columnName']
                if col_name == 'ranking':
                    if not is_fuzzy:
                        # The ranking column only exists for fuzzy searches.
                        continue
                    order_by_ranking = x['direction']
                    orm_orderby = []
                    break
                is_desc = x['direction'].lower() == 'desc'
                if col_name == 'alias_list':
                    orm_orderby.append(f"{'-' if is_desc else ''}cached_properties__{'max' if is_desc else 'min'}_alias")
                    continue
                order_field = F(col_name)
                if is_desc:
                    order_field = order_field.desc(nulls_last=True)
                else:
                    order_field = order_field.asc(nulls_last=True)
                orm_orderby.append(order_field)

        if not order_by_ranking:
            if orm_orderby:
                q = q.order_by(*orm_orderby)
            else:
                q = q.order_by('-cached_properties__enslaved_count')

        MultiValueHelper.set_group_concat_limit()
        if is_fuzzy:
            main_query = _auto_select_related_fields(q, fields)
        else:
            q = q.annotate(pk=F('id'))
            q = q.values('pk')
            main_query = _auto_select_related_fields(EnslaverIdentity.objects, fields)
        for helper in self.all_helpers:
            main_query = helper.adapt_query(main_query)
        main_query = main_query.values(*fields)

        if is_fuzzy:
            # Convert the QuerySet to a concrete list and include the ranking
            # as a member of each object in that list.
            q = list(main_query)
            for x in q:
                x['ranking'] = ranking[x['id']]
            if order_by_ranking:
                q = sorted(q,
                           key=lambda x: x['ranking'],
                           reverse=(order_by_ranking == 'desc'))
        else:
            (count_query_str, count_params) = q.order_by().distinct().query.sql_with_params()
            (match_query_str, match_params) = q.distinct().query.sql_with_params()
            (main_query_str, main_params) = main_query.query.sql_with_params()
            full_query_str = f"{main_query_str} INNER JOIN ({match_query_str} LIMIT 0,0) AS matches ON matches.pk=past_enslaveridentity.id"
            data_query = EnslaverIdentity.objects.raw(full_query_str, main_params + match_params)
            q = RawQueryWrapper(data_query.query, EnslaverIdentity.objects.raw(count_query_str, count_params).query, fields)
        return q

    @classmethod
    def patch_row(cls, row):
        for helper in cls.all_helpers:
            row = helper.patch_row(row)
        return row


class EnslaverContribution(models.Model):
    # We allow NULLs because the enslaver may be deleted and we still want to
    # keep the contribution (it might even be the reason the identity was
    # deleted, say in the case of a merge).
    enslaver = models.ForeignKey(EnslaverIdentity, null=True, on_delete=models.SET_NULL)
    contributor = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=False)
    data = models.TextField(null=False)
