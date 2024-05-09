import requests
import json
from django.core.management.base import BaseCommand, CommandError
from common.reqs import  getJSONschema


class Command(BaseCommand):
	help = 'publishes the schema as flat json and python files, \
	which are used to populate the options avaiable in the model serializers. \
	this should be run any time you alter the serializers or models. \
	outputs go to api/common/static and are included in the git repo.'
	def handle(self, *args, **options):
		
# 		base_obj_names=[
# 			"Author",
# 			"Enslaved",
# 			"EnslaverIdentity",
# 			"Institution",
# 			"Post",
# 			"Voyage",
# 			"Source",
# 			"Estimate",
# 			"EnslavementRelation"
# 		]
# 		
# 		for base_obj_name in base_obj_names:
# 			getJSONschema(base_obj_name,hierarchical=False,rebuild=True)