from docs.models import *
from django.db.models import Avg,Sum,Min,Max,Count,Q
import json
from django.core.management.base import BaseCommand, CommandError
import time
import os
import re
import requests
from docs.models import Doc,DocTag

class Command(BaseCommand):
	help = 'there ain\'t no balm in gilead'
	def handle(self, *args, **options):
		
		print('deleting all docs')
		docs=Doc.objects.all()
		for doc in docs:
			doc.delete()
		
		print('deleting all tags')
		DocTags=DocTag.objects.all()
		for doctag in DocTags:
			doctag.delete()
		
		base_path='docs/management/commands/'
		
		d=open(os.path.join(base_path,'manifests.txt'))
		t=d.read()
		d.close()
		urls=[l for l in t.split('\n') if l!='']
		
		def get_and_clean_field(jsonresponse,field):
			try:
				fieldvalue=[i['value']['none'][0] for i in j['metadata'] if i['label']['none'][0]==field][0]
				fieldvalue=re.sub("&.*?;","",fieldvalue)
				fieldvalue=re.sub("<.*?>","",fieldvalue)
			except:
				fieldvalue=None
			return fieldvalue
		
		for u in urls:
			r=requests.get(u)
			if r.status_code==200:
				j=json.loads(r.text)
				title=get_and_clean_field(j,"Title")
				citation=get_and_clean_field(j,'Bibliographic Citation')
				pub_year=get_and_clean_field(j,"Date")
				pub_year=int(pub_year)
				tags=get_and_clean_field(j,"Type")
			
				d=Doc(
					url=u,
					citation=citation,
					title=title,
					pub_year=pub_year
				)
				d.save()
				for tag in tags:
					tag_obj=DocTags.filter(tag=tag)
					if tag_obj is None:
						t=DocTag(tag=tag)
						t.save()
						tag_obj=DocTags.filter(tag=tag)
					
					d.tag.set(tag_obj)
					d.save()
				print(u,title,tags)
				
			else:
				print("bad url:",u)
		