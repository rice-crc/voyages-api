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

def imgfilenamematch(django_source_pages,transkribus_page_json):
	transkribus_imgFileName=transkribus_page_json['imgFileName']
	matches=[]
	for dsp in django_source_pages:
# 		dsp_fname=dsp.image_filename
 		##Sept 27-28 uploads to transkribus had to use pk's instead of original filenames
		##because original filenames were null
		dsp_fname=str(dsp.id)
		dsp_nofileextension=re.sub("\..*","",dsp_fname)
		transkribus_imgFileName_noextension=re.sub("\..*","",transkribus_imgFileName)
		if dsp_nofileextension==transkribus_imgFileName_noextension:
			matches.append(dsp)
	return matches


class Command(BaseCommand):
	help = 'hits transkribus, pulls down image transcriptions'
	def handle(self, *args, **options):
# 		l=[
# 		'1437762SSC Add MS 25575',
# 		'1438141SSC Add MS 25577',
# 		'1439396SSC Add MS 25576',
# 		'1439405SSC Add MS 25582',
# 		'1449140SSC Add MS 25495',
# 		'1449222SSC Add MS 25496',
# 		'1449393SSC Add MS 25497',
# 		'1449420SSC Add MS 25498',
# 		'1449430SSC Add MS 25499',
# 		'1449440SSC Add MS 25500',
# 		'1449461SSC Add MS 25501',
# 		'1460954SSC Add MS 25502',
# 		'1460963SSC Add MS 25503',
# 		'1460974SSC Add MS 25504',
# 		'1460986SSC Add MS 25505',
# 		'1461076SSC Add MS 25507',
# 		'1461860SSC Add MS 25506',
# 		'1462319SSC Add MS 25508',
# 		'1462436SSC Add MS 25509',
# 		'1463252SSC Add MS 25510',
# 		'1465124SSC Add MS 25511',
# 		'1465146SSC Add MS 25544',
# 		'1469863SSC Add MS 25545',
# 		'1470747SSC Add MS 25550',
# 		'1470827SSC Add MS 25551',
# 		'1470863SSC Add MS 25553',
# 		'1470876SSC Add MS 25554',
# 		'1487718SSC Add MS 25552',
# 		'1487721SSC Add MS 25555',
# 		'1492844SSC Add MS 25556',
# 		'1492957SSC Add MS 25558',
# 		'1492986SSC Add MS 25560',
# 		'1493090SSC Add MS 25561',
# 		'1493096SSC Add MS 25562',
# 		'1494890SSC Add MS 25559',
# 		'1494915SSC Add MS 25563',
# 		'1494931SSC Add MS 25564',
# 		'1496973SSC Add MS 25565',
# 		'1497235SSC Add MS 25566',
# 		'1497274SSC Add MS 25567',
# 		'1497282SSC Add MS 25568',
# 		'1497296SSC Add MS 25569',
# 		'1497301SSC Add MS 25570']
# 
# 		for i in l:
# 			transkribus_id=int(re.search('^[0-9]+',i).group(0))
# 			short_ref_ms_id=re.search('(?<=Add MS )[0-9]+',i).group(0)
# 			try:
# 				short_ref="SSC Add MS "+short_ref_ms_id
# 				print(short_ref)
# 				short_ref=ShortRef.objects.get(name=short_ref)
# 			except:
# 				short_ref=None
# 			if short_ref is not None:
# 				short_ref.transkribus_docId=transkribus_id
# 				short_ref.save()





		#1. authenticate
		auth_headers=authenticate()
		
		print("auth headers:",auth_headers)
		
		collections_url='https://transkribus.eu/TrpServer/rest/collections/list'
		
		resp=requests.get(collections_url,headers=auth_headers)
		
		j=json.loads(resp.text)
		
# 		print(resp,json.dumps(j,indent=2))
		
		#2. flag all legacy sources with transkribus ids
		
		legacysources=Source.objects.all()
		transkribus_sources_queryset=legacysources.exclude(short_ref__transkribus_docId=None)
		transkribus_sources_queryset=transkribus_sources_queryset.filter(short_ref__name__icontains="SSC Add Ms")
		
		
		transkribus_sources={}
		for s in transkribus_sources_queryset:
			docid=int(s.short_ref.transkribus_docId)
			if docid in transkribus_sources:
				transkribus_sources[docid].append(s)
			else:
				transkribus_sources[docid]=[s]
		
# 		for s in tr
# 		
# 		{s.short_ref.transkribus_docId:s for s in transkribus_sources}
# 		
# 

		#now pull all docs, and flag those with transkribus ids in the db
		
		flagged_transkribus_documents=[]
		
# 		print(transkribus_sources)
		
		
		
		for transkribus_collection_id in transkribus_collection_ids:
		
			collection_url="https://transkribus.eu/TrpServer/rest/collections/%s/list" %transkribus_collection_id
			resp=requests.get(collection_url,headers=auth_headers)
			collection_documents=json.loads(resp.text)
		
# 			print(json.dumps(j,indent=2))
			
			for document_listing in collection_documents:
# 				print(json.dumps(document_listing,indent=2))
				if document_listing['docId'] in transkribus_sources:
					flagged_transkribus_documents.append(document_listing)
		
# 		print("-----------PULLING THESE DOCUMENTS\n",[[d['colId'],d['title']] for d in flagged_transkribus_documents])
		
		print("-----------PULLING THESE DOCUMENTS")
# 		print(json.dumps(flagged_transkribus_documents,indent=3))
		
		flagged_transkribus_documents.reverse()
		
		
		for transkribus_doc in flagged_transkribus_documents:
			print(transkribus_doc)
			doc_sources=transkribus_sources[transkribus_doc['docId']]
			docId=transkribus_doc['docId']
			doc_url="https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" %(transkribus_collection_id,docId)
			resp=requests.get(doc_url,headers=auth_headers)
			doc=json.loads(resp.text)
			
			docpagetranscripts={}
			
			for transkribus_page in doc['pageList']['pages']:
				pagetexturls=[]
				imgFileName=transkribus_page['imgFileName']
				pageId=transkribus_page['pageId']
				transcripts=transkribus_page['tsList']['transcripts']
				for transcript in transcripts:
					wordcount=transcript['nrOfCharsInLines']
# 					print("wordcount",transcript['nrOfCharsInLines'])
					if wordcount>0:
						pagetexturls.append([transcript['fileName'],transcript['url'],imgFileName,pageId])
				if len(pagetexturls)>0:
					try:
						reduced_imgfilename=re.search('[0-9]+[r|v]\.jpg',imgFileName).group(0)
					except:
						print("bad filename",imgFileName)
						reduced_imgfilename=None
					if reduced_imgfilename is not None:
						docpagetranscripts[reduced_imgfilename]=pagetexturls
			
			
# 			print(json.dumps(docpagetranscripts,indent=3))
			
			
			
			
			for source in doc_sources:
				print("SOURCE",source.id,source.title)
				source_pages=[spc.page for spc in source.page_connections.all()]
				source_pages_dict={sp.image_filename:sp for sp in source_pages}
				for pagefilename in source_pages_dict:
					if source.is_british_library:					
						try:
							reduced_imgfilename=re.search('[0-9]+[r|v]\.jpg',pagefilename).group(0)
						except:
							print("bad filename",imgFileName)
							reduced_imgfilename=None
						imgfilename=reduced_imgfilename
					else:
						imgfilename=pagefilename
					
					page_transcription=source_pages_dict[pagefilename].transcription
					
					if imgfilename is not None:
						if page_transcription is None:
							if imgfilename in docpagetranscripts:
								print("match",pagefilename)
								transcript_datachunks=docpagetranscripts[imgfilename]
								pagetext=''
								for transcript_data in transcript_datachunks:
									transcript_fname,transcript_url,ACTUAL_FING_FILENAME,transkribus_pageId=transcript_data
									connection_pool = urllib3.PoolManager()
									resp = connection_pool.request('GET',transcript_url,headers=auth_headers)
									
									
									tmpfilename="tmp/%s.xml" %docId
									f = open(tmpfilename, 'wb')
									f.write(resp.data)
									f.close()
									resp.release_conn()
									d=open(tmpfilename,"r")
									t=d.read()
									
# 									print(t)
							
									d.close()
									skipthis=False
									try:
										pagetree=ET.fromstring(t)
									except:
										print("failed with this textfile",t)
										skipthis=True	
									
									if not skipthis:
										textlines_trees=[e for e in pagetree.iter() if e.tag=="{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextLine"]
									
										textlines=[]
							
										try:
											os.remove(tmpfilename)
										except:
											print("tmp file does not exist?",tmpfilename)
							
										for textline_tree in textlines_trees:
											for child in textline_tree:
												if child.tag=='{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextEquiv':
													linetext=[e.text for e in child.iter() if e.tag=='{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode' and e.text is not None]
													textlines.append(' '.join(linetext))
										pagetext+='\n'.join(textlines)
									
									
# 									tmpfilename="tmp/"+transcript_fname
# 									f = open(tmpfilename, 'wb')
# 									f.write(resp.data)
# 									f.close()
# 									resp.release_conn()
# 									d=open(tmpfilename,"r")
# 									t=d.read()
# 									d.close()
# 									os.remove(tmpfilename)
# 									pagetree=ET.fromstring(t)
# 									textlines_trees=[e for e in pagetree.iter() if e.tag=="{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextLine"]
# 									textlines=[]
# 									for textline_tree in textlines_trees:
# 										linetext=[e.text for e in textline_tree.iter() if e.tag=='{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode' and e.text is not None]
# 										textlines.append(' '.join(linetext))
# 									pagetext+='\n'.join(textlines)
									
									
# 								print(pagetext)

								sp=source_pages_dict[pagefilename]
								sp.transkribus_pageid=transkribus_pageId
								sp.transcription=pagetext
								sp.image_filename=ACTUAL_FING_FILENAME
								try:
									sp.save()
								except:
									print("ERROR SAVING PAGE -- LIKELY DUPLICATE PAGE ID")
# 								print(sp.__dict__)
							else:
								print("no match",pagefilename)
						else:
							print('transcript already fetched')
					else:
						print('no image filename')
# 
				

# 				
# 				
# 				print(transkribus_doc)
# 				print(source_pages.image_filename)
# 				exit()
# 			
# 			
# 			zotero_refs=legacy_source.source_zotero_refs.all()
# 			for zotero_ref in zotero_refs:
# 				page_connections=zotero_ref.page_connection.all()
# 				for page_connection in page_connections:
# 					source_page=page_connection.source_page
# 					source_pages.append(source_page)
# 			print(source_pages)
# 			for sp in source_pages:
# 				print(sp.image_filename)
# 			
# 			docId=transkribus_doc['docId']
# 			doc_url="https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" %(transkribus_collection_id,docId)
# 			resp=requests.get(doc_url,headers=auth_headers)
# 			
# 			doc=json.loads(resp.text)
# # 			print(resp,json.dumps(doc,indent=2),doc.keys())
# 			
# 			
# 			for transkribus_page in doc['pageList']['pages']:
# # 				print("??????",transkribus_page)
# 				imgFileName=transkribus_page['imgFileName']
# 				imagfilenamematches=imgfilenamematch(source_pages,transkribus_page)
# 				
# 				
# 				if len(imagfilenamematches)==1:
# 					print('---')
# 					print("matched",imgFileName,imagfilenamematches)
# 					django_source_page=imagfilenamematches[0]
# # 					print(transkribus_page)
# 					if len(transkribus_page['tsList'])>0:
# 						transcriptsbundle=transkribus_page['tsList']
# 						if len(transcriptsbundle)>0:
# 							transcripts=transcriptsbundle['transcripts']
# 							nonblank_transcript_urls=[]
# 							for transcript in transcripts:
# 								if transcript['nrOfCharsInLines'] > 0:
# 									nonblank_transcript_urls.append([transcript['fileName'],transcript['url']])
# 							if len(nonblank_transcript_urls)>0:
# 								print("transcription urls-->",nonblank_transcript_urls)
# 							else:
# 								print('only blank transcripts')
# 								
# 							for transcript_data in nonblank_transcript_urls:
# 								transcript_fname,transcript_url=transcript_data
# 								connection_pool = urllib3.PoolManager()
# 								resp = connection_pool.request('GET',transcript_url,headers=auth_headers)
# 								f = open("tmp/"+transcript_fname, 'wb')
# 								f.write(resp.data)
# 								f.close()
# 								resp.release_conn()
# 								d=open("tmp/"+transcript_fname,"r")
# 								t=d.read()
# 								d.close()
# 								pagetree=ET.fromstring(t)
# 								textlines=[e.text for e in pagetree.iter() if e.tag=='{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode']
# 								textlines=[l for l in textlines if l is not None]
# 								pagetext='\n'.join(textlines)
# 								if django_source_page.transcription is None:
# 									django_source_page.transcription=pagetext
# 									django_source_page.save()
# # 								print(pagetext)
# 
# 									
# 						
# 						
# 					print("---")
# 					
# 				
# 				else:
# 					print("problem matching:",imgFileName,imagfilenamematches)
# 			
# # 			
# 
# 			
# 			
# 			
# 					
# 1296300	mssST_09
# 1296568	mssST_57_v17
# 1298211	mssST_57_v18
# 1300326	mssST_57_v21
# 1300594	mssST_57_v19
# 1301052	mssST_57_v24
# 1304905	mssST_57_v24_p114
# 1357529	043
# 1359783	044
# 1437762	SSC ADD MS 25575- 2
# 1438141	SSC ADD MS 25577
# 1439396	SSC ADD MS 25576
# 1439405	SSC ADD MS 25582
# 1449140	SSC ADD MS 25495
# 1449222	SSC ADD MS 25496
# 1449393	SSC ADD MS 25497
# 1449420	SSC ADD MS 25498
# 1449430	SSC ADD MS 25499
# 1449440	SSC ADD MS 25500
# 1449461	SSC ADD MS 25501
# 1460954	SSC ADD MS 25502
# 1460963	SSC ADD MS 25503
# 1460974	SSC ADD MS 25504
# 1460986	SSC ADD MS 25505
# 1461076	SSC ADD MS 25507
# 1461860	SSC ADD MS 25506
# 1462319	SSC ADD MS 25508
# 1462436	SSC ADD MS 25509
# 1463252	SSC ADD MS 25510
# 1465124	SSC ADD MS 25511
# 1465146	SSC ADD MS 25544
# 1469863	SSC ADD MS 25545
# 1470747	SSC ADD MS 25550
# 1470827	SSC ADD MS 25551
# 1470863	SSC ADD MS 25553
# 1470876	SSC ADD MS 25554
# 1487718	SSC ADD MS 25552
# 1487721	SSC ADD MS 25555
# 1492844	SSC ADD MS 25556
# 1492957	SSC ADD MS 25558
# 1492986	SSC ADD MS 25560
# 1493090	SSC ADD MS 25561
# 1493096	SSC ADD MS 25562
# 1494890	SSC ADD MS 25559
# 1494915	SSC ADD MS 25563
# 1494931	SSC ADD MS 25564
# 1496973	SSC ADD MS 25565
# 1497235	SSC ADD MS 25566
# 1497274	SSC ADD MS 25567
# 1497282	SSC ADD MS 25568
# 1497296	SSC ADD MS 25569
# 1497301	SSC ADD MS 25570
# 1590616	AP Clement 43
# 1591585	AP Clement 44
# 1592010	DOCP Huntington 57 19
# 1592013	DOCP Huntington 57 18
# 1592018	DOCP Huntington 57 17
# 1594526	DOCP Huntington 57 21


# 
# 
# import re
# from document.models import *
# l=['1437762SSC Add MS 25575','1438141SSC Add MS 25577','1439396SSC Add MS 25576','1439405SSC Add MS 25582','1449140SSC Add MS 25495','1449222SSC Add MS 25496','1449393SSC Add MS 25497','1449420SSC Add MS 25498','1449430SSC Add MS 25499','1449440SSC Add MS 25500','1449461SSC Add MS 25501','1460954SSC Add MS 25502','1460963SSC Add MS 25503','1460974SSC Add MS 25504','1460986SSC Add MS 25505','1461076SSC Add MS 25507','1461860SSC Add MS 25506','1462319SSC Add MS 25508','1462436SSC Add MS 25509','1463252SSC Add MS 25510','1465124SSC Add MS 25511','1465146SSC Add MS 25544','1469863SSC Add MS 25545','1470747SSC Add MS 25550','1470827SSC Add MS 25551','1470863SSC Add MS 25553','1470876SSC Add MS 25554','1487718SSC Add MS 25552','1487721SSC Add MS 25555','1492844SSC Add MS 25556','1492957SSC Add MS 25558','1492986SSC Add MS 25560','1493090SSC Add MS 25561','1493096SSC Add MS 25562','1494890SSC Add MS 25559','1494915SSC Add MS 25563','1494931SSC Add MS 25564','1496973SSC Add MS 25565','1497235SSC Add MS 25566','1497274SSC Add MS 25567','1497282SSC Add MS 25568','1497296SSC Add MS 25569','1497301SSC Add MS 25570']
# 
# for i in l:
# 	transkribus_id=int(re.search('^[0-9]+',i).group(0))
# 	short_ref_ms_id=re.search('(?<=Add MS )[0-9]+',i).group(0)
# 	try:
# 		short_ref="SSC Add MS "+short_ref_ms_id
# 		print(short_ref)
# 		short_ref=ShortRef.objects.get(name=short_ref)
# 	except:
# 		short_ref=None
# 	if short_ref is not None:
# 		short_ref.transkribus_docId=transkribus_id
# 		short_ref.save()


# 
# from document.models import *
# transkribus_sources=Source.objects.all().filter(short_ref__name__icontains="SSC Add Ms")
# transkribus_sources.count()
# for s in transkribus_sources:
# 	for sc in s.page_connections.all():
# 		page=sc.page
# 		page.transcription=None
# 		page.save()