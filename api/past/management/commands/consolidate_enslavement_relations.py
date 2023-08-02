import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from document.models import *
from voyage.models import *
from voyages3.settings import *
import requests
import json
import os



class Command(BaseCommand):
	help = 'consolidates voyages into enslavement identities and allows enslavers to have\
	multiple roles in them, and these relations to have multiple types -- including \
	voyages. this should eliminate the need for on-the-fly deduping of enslavers & \
	enslaved.\
	THIS SHOULD ONLY BE RUN ONCE\
	and then the scaffolding should be torn down.\
	Alternatively, we do not do this, because the enslaver-enslaved individual relations\
	are not isomorphic to the enslaver-voyage-enslaved grouped relations. \
	Specifically, if we start using this generic relation type to depict for instance\
	ship owners to enslaved people and direct owners to enslaved people then we will lose\
	the direct connections in the aggregations -- or we will disaggregate, in which case,\
	what is the point?\
	The point might be to just have all these relations in one place -- which we can \
	ensure if we disallow multiple roles by the same person, and multiple relation types.\
	Of course then we are enforcing duplication...'
	def handle(self, *args, **options):
		aliases=EnslaverAlias.objects.all()
		relationtypes=EnslavementRelationType.objects.all()
		transportationtype=relationtypes.filter(name='Transportation').first()
		# first, we migrate all the voyages over
		## turning these into enslavement relations that have *one* type of voyage
		## that are connected to enslaver aliases and voyages
		enslaved=Enslaved.objects.all()
		print("enslaved")
		for e in enslaved:
			voyage=e.voyage
			if voyage is not None:
				er,er_isnew=EnslavementRelation.objects.get_or_create(
					voyage=voyage,
					relation_type=transportationtype,
					is_from_voyages=True
				)
				eir,eir_isnew=EnslavedInRelation.objects.get_or_create(
					enslaved=e,
					relation=er
				)
		print("enslavers")
		for a in aliases:
			enslaver_voyages=a.enslaver_voyage_connection.all()
			for evc in enslaver_voyages:
				
				er,er_isnew=EnslavementRelation.objects.get_or_create(
					voyage=evc.voyage,
					relation_type=transportationtype,
					is_from_voyages=True
				)
				
				eir,eir_isnew=EnslaverInRelation.objects.get_or_create(
					relation=er,
					role=evc.role,
					enslaver_alias=a
				)
			
		
		
		#we can't transfer sources over because for some reason (???) there are no
		#enslaver-to-enslavementrelation sources. only enslaver-to-source and voyage-to source