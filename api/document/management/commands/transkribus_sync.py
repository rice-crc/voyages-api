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

def imgfilenamematch(django_source_pages,transkribus_page_json):
	transkribus_imgFileName=transkribus_page_json['imgFileName']
	matches=[]
	for dsp in django_source_pages:
		dsp_fname=dsp.image_filename
		dsp_nofileextension=re.sub("\..*","",dsp_fname)
		transkribus_imgFileName_noextension=re.sub("\..*","",transkribus_imgFileName)
		if dsp_nofileextension==transkribus_imgFileName_noextension:
			matches.append(dsp)
	return matches


class Command(BaseCommand):
	help = 'hits transkribus, pulls down image transcriptions'
	def handle(self, *args, **options):
		
		#1. authenticate
		auth_headers=authenticate()
		
		print("auth headers:",auth_headers)
		
		collections_url='https://transkribus.eu/TrpServer/rest/collections/list'
		
		resp=requests.get(collections_url,headers=auth_headers)
		
		j=json.loads(resp.text)
		
		print(resp,json.dumps(j,indent=2))
		
		#flag all legacy sources with transkribus ids
		
		legacysources=VoyageSources.objects.all()
		transkribus_sources=legacysources.exclude(transkribus_docid=None)
		transkribus_sources={s.transkribus_docid:s for s in transkribus_sources}

		#now pull all docs, and flag those with transkribus ids in the db
		
		flagged_transkribus_documents=[]
		
		for transkribus_collection_id in transkribus_collection_ids:
		
			collection_url="https://transkribus.eu/TrpServer/rest/collections/%s/list" %transkribus_collection_id
			
			resp=requests.get(collection_url,headers=auth_headers)
			
			collection_documents=json.loads(resp.text)
		
# 			print(resp,json.dumps(j,indent=2))
			
			for document_listing in collection_documents:
				if document_listing['docId'] in transkribus_sources:
					flagged_transkribus_documents.append(document_listing)
		
		print("-----------PULLING THESE DOCUMENTS\n",[[d['docId'],d['title']] for d in flagged_transkribus_documents])
		
		
		
		
		for transkribus_doc in flagged_transkribus_documents:
			source_pages=[]
			
			legacy_source=transkribus_sources[transkribus_doc['docId']]
			zotero_refs=legacy_source.source_zotero_refs.all()
			for zotero_ref in zotero_refs:
				page_connections=zotero_ref.page_connection.all()
				for page_connection in page_connections:
					source_page=page_connection.source_page
					source_pages.append(source_page)
			print(source_pages)
			for sp in source_pages:
				print(sp.image_filename)
			
			docId=transkribus_doc['docId']
			doc_url="https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" %(transkribus_collection_id,docId)
			resp=requests.get(doc_url,headers=auth_headers)
			
			doc=json.loads(resp.text)
# 			print(resp,json.dumps(doc,indent=2),doc.keys())
			
			
			for transkribus_page in doc['pageList']['pages']:
# 				print("??????",transkribus_page)
				imgFileName=transkribus_page['imgFileName']
				imagfilenamematches=imgfilenamematch(source_pages,transkribus_page)
				
				
				if len(imagfilenamematches)==1:
					print('---')
					print("matched",imgFileName,imagfilenamematches)
					django_source_page=imagfilenamematches[0]
# 					print(transkribus_page)
					if len(transkribus_page['tsList'])>0:
						transcriptsbundle=transkribus_page['tsList']
						if len(transcriptsbundle)>0:
							transcripts=transcriptsbundle['transcripts']
							nonblank_transcript_urls=[]
							for transcript in transcripts:
								if transcript['nrOfCharsInLines'] > 0:
									nonblank_transcript_urls.append([transcript['fileName'],transcript['url']])
							if len(nonblank_transcript_urls)>0:
								print("transcription urls-->",nonblank_transcript_urls)
							else:
								print('only blank transcripts')
								
							for transcript_data in nonblank_transcript_urls:
								transcript_fname,transcript_url=transcript_data
								connection_pool = urllib3.PoolManager()
								resp = connection_pool.request('GET',transcript_url,headers=auth_headers)
								f = open("tmp/"+transcript_fname, 'wb')
								f.write(resp.data)
								f.close()
								resp.release_conn()
								d=open("tmp/"+transcript_fname,"r")
								t=d.read()
								d.close()
								pagetree=ET.fromstring(t)
								textlines=[e.text for e in pagetree.iter() if e.tag=='{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode']
								textlines=[l for l in textlines if l is not None]
								pagetext='\n'.join(textlines)
								if django_source_page.transcription is None:
									django_source_page.transcription=pagetext
									django_source_page.save()
# 								print(pagetext)

									
						
						
					print("---")
					
				
				else:
					print("problem matching:",imgFileName,imagfilenamematches)
			
# 			

			
			
			
					
					