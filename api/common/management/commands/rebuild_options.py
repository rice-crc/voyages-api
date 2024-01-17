import requests
import json
from django.core.management.base import BaseCommand, CommandError
from common.reqs import  getJSONschema


class Command(BaseCommand):
	help = 'rebuilds the solr indices'
	def handle(self, *args, **options):
		
		base_obj_names=[
			"Author",
			"Enslaved",
			"Enslaver",
			"Institution",
			"Post",
			"Voyage",
			"Source",
			"Estimate"
		]
		
		for base_obj_name in base_obj_names:
			getJSONschema(base_obj_name,hierarchical=False,rebuild=True)