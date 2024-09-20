from django.core.management.base import BaseCommand, CommandError
import json
import urllib3
import urllib
import xml.etree.ElementTree as ET
from document.models import *
from past.models import *
from voyage.models import *
from voyages3.localsettings import transkribus_credentials,transkribus_collection_ids
import requests
import re
import os

def authenticate():
	
	auth_url="https://transkribus.eu/TrpServer/rest/auth/login"
	
	payload=urllib.parse.urlencode(transkribus_credentials)
	
	headers={'Content-Type': 'application/x-www-form-urlencoded'}
	
	response = requests.request("POST", auth_url, headers=headers, data=payload)
	
	if response.status_code!=200:
		print("error",response,response.text)
		exit()

	root = ET.fromstring(response.text)
	sessionId=[c.text for c in root if c.tag=='sessionId'][0]
	headers['Cookie']='='.join([ 'JSESSIONID',sessionId])
	return headers


class Command(BaseCommand):
	help = 'hits transkribus, pulls down image transcriptions'
	def handle(self, *args, **options):
		
		#when the non-BL images were re-uploaded using their smaller jpg files to be processable
		#we lost the filenames. so now we're just going to have to count on pagination doing the trick for us
		
		#1. authenticate
		auth_headers=authenticate()
		
		print("auth headers:",auth_headers)
		
		collections_url='https://transkribus.eu/TrpServer/rest/collections/list'
		
		resp=requests.get(collections_url,headers=auth_headers)
		
		j=json.loads(resp.text)
		
# 		print(resp,json.dumps(j,indent=2))
		
		transkribus_shortrefs=ShortRef.objects.all().exclude(transkribus_docId=None)
		transkribus_shortrefs=transkribus_shortrefs.exclude(name__icontains="SSC Add Ms")
# 		transkribus_shortrefs=transkribus_shortrefs.exclude(transkribus_docId__in=[1301052,1594526])
		
# 		transkribus_shortrefs=transkribus_shortrefs.filter(transkribus_docId=1296568)
		
		# transkribus_shortrefs=transkribus_shortrefs.exclude(transkribus_docId__in=[1301052,1594526])
		
		print(transkribus_shortrefs)
		
		transkribus_collection_id=transkribus_collection_ids[0]
		
		page_pks=transkribus_shortrefs.values_list('transkribus_docId','short_ref_sources__page_connections__page__id')
		print(page_pks)
		pd={}
		for ppk in page_pks:
			a,b=ppk
			if b is not None:
				if a in pd:
					pd[a].append(b)
				else:
					pd[a]=[b]
		
		for docId in pd:
			print('DOCIDS',docId)
			pages=pd[docId]
			pages.sort()
			print('PAGES',pages)
			
			for pagepk in pages:
				page=Page.objects.get(id=pagepk)
				page.transkribus_pageid=None
				page.transcription=None
				page.save()
			
			doc_url="https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" %(transkribus_collection_id,docId)
			resp=requests.get(doc_url,headers=auth_headers)
			doc=json.loads(resp.text)
			
			c=1
			for transkribus_page in doc['pageList']['pages']:
# 				print("PAGES",pages,'COUNT',len(pages))
# 				print("C=",c)
				pagetexturls=[]
				sp=Page.objects.get(id=pages[c-1])
				print(sp.source_connections.first().source)
				
				
				if sp.transcriptions.all() != []:
					print("transcription already exists")
				else:
					imgFileName=transkribus_page['imgFileName']
					## but as a backstop we can capture the pageid on the transkribus side as well
					## and then bump them as necessary and re-pull (i don't want to do this!!!!)
					transkribus_pageId=transkribus_page['pageId']
					transcripts=transkribus_page['tsList']['transcripts']
# 					if c==8:
# 						print(json.dumps(transkribus_page,indent=2))
					
					pagetext=''
					for transcript in transcripts:
						wordcount=transcript['nrOfCharsInLines']
						if wordcount>0:
							transcript_url=transcript['url']
	# 							print(transcript_url)
							connection_pool = urllib3.PoolManager()
							resp = connection_pool.request('GET',transcript_url,headers=auth_headers)
							tmpfilename="tmp/%s.xml" %docId
							f = open(tmpfilename, 'wb')
							f.write(resp.data)
							f.close()
							resp.release_conn()
							d=open(tmpfilename,"r")
							t=d.read()
							
							d.close()
							pagetree=ET.fromstring(t)
							textlines_trees=[e for e in pagetree.iter() if e.tag=="{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextLine"]
							textlines=[]
							
							os.remove(tmpfilename)
							
							for textline_tree in textlines_trees:
								linetext=[e.text for e in textline_tree.iter() if e.tag=='{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode' and e.text is not None]
								textlines.append(' '.join(linetext))
							pagetext+='\n'.join(textlines)
# 					print(pagetext)
					if re.match('\s+',pagetext,re.S):
						pagetext=None
					
# 					sp.transkribus_pageid=transkribus_pageId
					Transcription.objects.create(
						page=sp,
						language_code='en',
						text=pagetext,
						is_translation=False
					)
					
# 					sp.transcriptions.add=pagetext
# 					sp.save()
					
					
					

				c+=1
# 				if c>10:
# 					exit()