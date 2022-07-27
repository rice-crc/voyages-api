from docs.models import *
from django.db.models import Avg,Sum,Min,Max,Count,Q
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os
import re
import requests

class Command(BaseCommand):
	help = 'there ain\'t no balm in gilead'
	def handle(self, *args, **options):
		
		print('deleting all docs')
		docs=Doc.objects.all()
		for doc in docs:
			doc.delete()
		
		
		base_path='docs/management/commands/'
		
		d=open(os.path.join(base_path,'manifests.txt'))
		t=d.read()
		d.close()
		urls=[l for l in t.split('\n') if l!='']
		
		for u in urls:
			r=requests.get(u)
			if r.status_code==200:
				j=json.loads(r.text)
				try:
					citation=[i['value']['none'][0] for i in j['metadata'] if i['label']['none'][0]=='Bibliographic Citation'][0]
					citation=re.sub("&.*?;","",citation)
					citation=re.sub("<.*?>","",citation)
				except:
					citation=None
			else:
				citation=None
			
			print(citation)
			
			d=Doc(
				url=u,
				citation=citation
			)
			d.save()
			print(u)
		