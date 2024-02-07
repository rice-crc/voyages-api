import requests
import json
from django.core.management.base import BaseCommand, CommandError
from voyage.models import Voyage
from past.models import *
from blog.models import Post
import pysolr
import numpy as np


class Command(BaseCommand):
	help = 'rebuilds the solr indices'
	def handle(self, *args, **options):
		indices=[			{
				"model":Voyage,
				"core_name":"voyages",
				"fields":[
					"id",
					"voyage_ship__ship_name"
				]
			},
			{
				"model":EnslaverIdentity,
				"core_name":"enslavers",
				"fields":[
					'id',
					'aliases__alias',
					'principal_alias'
				]
			},
			{
				"model":Enslaved,
				"core_name":"enslaved",
				"fields":[
					'id',
					'documented_name',
					'name_first',
					'name_second',
					'name_third',
					'modern_name'
				]
			},
			{
				"model":Post,
				"core_name":"blog",
				"fields":[
					'id',
					'authors__name',
					'tags__name',
					'tags__intro',
					'title',
					'subtitle',
					'content'
				]
			}
		]
		
		results_per_page=1000
		
		for idx in indices:
			
			model=idx["model"]
			fields=idx["fields"]
			core_name=idx["core_name"]
			print("INDEXING",core_name,"on",len(fields),"fields")
			
			if fields[0]!="id":
				print("FIRST FIELD INDEX MUST BE NAMED `ID`")
				exit()

			solr = pysolr.Solr(
				'http://voyages-solr:8983/solr/%s/' %core_name,
				always_commit=True,
				timeout=10
			)
			
			queryset=model.objects.all()
			
			ids=[i[0] for i in queryset.values_list('id')]
			
			if len(ids)>0:
			
				batch_size=5000
			
				pagecount=int(len(ids)/batch_size)
				if pagecount==0:
					pagecount=1
				
				pages=np.array_split(np.array(ids),pagecount)
			
				p=1
			
				for page in pages:
					print("--page",p,'of',pagecount)
				
					pageidlist=[int(v) for v in page]
				
					pagedict={v:[] for v in pageidlist}
				
					pagequeryset=queryset.filter(id__in=pageidlist)
				
					for f in fields:
						vl=pagequeryset.values_list('id',f)
						for v in vl:
							id,i=v
							if i!=None:
								pagedict[id].append(str(i))
				
					solrpage=[
						{
							"id":k,
							"text":" ".join(pagedict[k])
						}
						for k in pagedict
					]
				
					solr.add(solrpage)
					p+=1
			else:
				print("-----FOUND NO RESULTS----")