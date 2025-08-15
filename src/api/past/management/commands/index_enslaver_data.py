import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from voyage.models import *
import requests
import json
import os



class Command(BaseCommand):
	help = 'connects enslavers directly to voyages and roles for faster searching'
	def handle(self, *args, **options):
		enslaverIdentities=EnslaverIdentity.objects.all()
		
		enslaverIdentities=enslaverIdentities.prefetch_related(
			'aliases__enslaver_relations__relation__voyage',
			'aliases__enslaver_relations__roles'
		)
		
		enslaver_voyage_values_list=enslaverIdentities.values_list(
			'id',
			'aliases__enslaver_relations__relation__voyage__id'
		)
		
		voyages_dict={
			o.id:o for o in Voyage.objects.all()
		}
		c=0
		print('voyages')
		for evv in enslaver_voyage_values_list:
			id,v_id=evv
			if v_id is not None:
				enslaver_identity=EnslaverIdentity.objects.get(id=id)
				voyage=voyages_dict[v_id]
				enslaver_identity.voyages.add(voyage)
			c+=1
			if c%1000==0:
				print(c)
		
		enslaver_roles_values_list=enslaverIdentities.values_list('id','aliases__enslaver_relations__roles__id')
		
		roles_dict={
			o.id:o for o in EnslaverRole.objects.all()
		}
		
		c=0
		print('roles')
		for erv in enslaver_roles_values_list:
			id,role_id=erv
			if role_id is not None:
				enslaver_identity=EnslaverIdentity.objects.get(id=id)
				role=roles_dict[role_id]
				enslaver_identity.roles.add(role)
			c+=1
			if c%1000==0:
				print(c)
			