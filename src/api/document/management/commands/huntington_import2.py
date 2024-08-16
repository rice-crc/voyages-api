import csv
import re
from pyzotero import zotero
from django.core.management.base import BaseCommand, CommandError
from document.models import *
from past.models import *
from voyage.models import *
from voyages3.settings import *
import requests
import json
import os
import time

class Command(BaseCommand):
	help = 'imports BL volumes from dd41 student segmentations -- purpose-built'
	def handle(self, *args, **options):

		basepath="document/management/commands/Huntington_Sources"
		csvpaths=[i for i in os.listdir(basepath) if i.endswith('.csv')]
		
		library_id='5538644'
		grouplibrary_name='sv-docp-huntington'
		library_type=zotero_credentials['library_type']
		api_key=zotero_credentials['api_key']
		zot = zotero.Zotero(library_id, library_type, api_key)

		ms_template = zot.item_template('manuscript')
		letter_template = zot.item_template('letter')
		
		
		
		for csvpath in csvpaths:
			fpath=os.path.join(basepath,csvpath)
			
			MS_ID=re.search("[0-9]+ v[0-9]+",fpath).group(0).strip()
			print(MS_ID)
			with open(fpath,'r',encoding='ISO-8859-1') as csvfile:
				reader=csv.DictReader(csvfile)
				printedalready=False
				
				thisdoc={'image_filenames':[]}
				endofdoc=False
				
				doccount=0
				
				for row in reader:
# 					print(row)
					print("-->",thisdoc)
					page_label=row['Page Labels']
					image_filename=row['image_filename']
					date=row['Dates']
					if re.match('[0-9]+,\s*[0-9]+,\s*[0-9]+',date):
						mm,dd,yyyy=[d.strip() if d!='' else None for d in re.search('[0-9]+,\s*[0-9]+,\s*[0-9]+',date).group(0).split(',')]
						mm=int(mm)
						dd=int(dd)
# 						print("----->",dd,mm,yyyy,len(yyyy))
						if len(yyyy)==2:
							yyyy=int("17"+yyyy)
						elif len(yyyy)==1:
							yyyy=int("170"+yyyy)
						else:
							yyyy=int(yyyy)
							
						date=[mm,dd,yyyy]
					else:
						date=None
					doctype=row['Types']
					
					
					if doctype!='':
						thisdoc['image_filenames'].append([image_filename,page_label])
						thisdoc['doctype']=doctype
						thisdoc['title']=row['Slave Voyages Notes']
						if date is not None:
							thisdoc['date']=date
						if 'pagelabels' not in thisdoc:
							thisdoc['pagelabels']=[page_label]
						else:
							thisdoc['pagelabels'].append(page_label)
					else:
						if thisdoc!={'image_filenames': []}:
							callNumber=f"Duke of Chandos, Stowe Papers {MS_ID}"
							shortTitle=f"DOCP {MS_ID}"
							
							doctitle=thisdoc['title']
							
							if thisdoc['doctype'].strip() in [
								'Copy of Correspondence',
								'Correspondence',
								'Court Correspondence',
								'Court of Directors Correspondence',
								'Letter',
								'Letters of Correspondence'
							]:
								template_type="letter"
								docdict=dict(letter_template)
							else:
								template_type="ms"
								docdict=dict(ms_template)							
							
							
							if 'date' in thisdoc:
								thisdocdate=thisdoc['date']
							else:
								thisdocdate=None
							
							if thisdocdate is not None:
								datestr='/'.join([str(d) for d in thisdocdate])
							else:
								datestr="No Date"
								
							docdict["date"]=datestr
							
# 							print(thisdoc['pagelabels'],len(thisdoc['pagelabels']))

							pagelabels=[i[1] for i in thisdoc['image_filenames'] if i[1].strip()!='']
							numpages=len(pagelabels)
							
# 							print("pp",pp)
							
							pagelabels_str='; '.join(pagelabels)
							#per dd41 -- no dates in the titles. fair enough.
# 							if datestr=="No Date":
# 								title="%s (%s)" %(thisdoc['doctype'],datestr)
# 							else:
# 								title="%s %s" %(datestr,thisdoc['doctype'])
							
							doctype=thisdoc['doctype']
							if doctype.lower()=="letter":
								title=f"{thisdoc['title']} (letter)"
							elif doctype.lower()=="journal entry":
								title=f"{thisdoc['title']} (journal)"
							else:
								print("DOCTYPE",doctype)
							
							docdict["archiveLocation"]= "%s, %s" %(callNumber,pagelabels_str)
							docdict['shortTitle']=shortTitle
							
							docdict['archive']='The Huntington Library'
							if template_type=='ms':
								docdict['numPages']=numpages
								docdict['place']="San Marino, CA"
							else:
								docdict['extra']="Place: San Marino, CA"
							docdict['title']=title
							docdict['language']='en-UK'
							
							shortref,shortref_isnew=ShortRef.objects.get_or_create(
								name=shortTitle
							)
							
# 							docdict['title']+=': %s' %pagelabels_str
							
							thisdocpages=[]
							
							
							
							image_filenames=thisdoc['image_filenames']
							
							for image_filename_tuple in image_filenames:
								image_filename,pagelabel=image_filename_tuple
								
								try:
									page=Page.objects.get(
										image_filename=image_filename
									)
								except:								
									page=Page.objects.create(
										is_british_library=False,
										image_filename=image_filename
									)
								thisdocpages.append(page)
							
							while True:
								try:
									resp = zot.create_items([docdict])
									break
								except:
									time.sleep(10)
							
							
							
							try:
								zotero_url=resp['successful']['0']['links']['self']['href']
								print(zotero_url)
							except:
								print("error with zotero call")
								print(resp)
								exit()
							
							group_id=re.search("(?<=groups/)[0-9]+",zotero_url).group(0)
							item_id=re.search("(?<=items/)[A-Z|0-9]+",zotero_url).group(0)
							
							if thisdocdate is not None:
								mm,dd,yyyy=thisdocdate
								docsparsedate=DocSparseDate.objects.create(
									month=mm,
									day=dd,
									year=yyyy
								)
							else:
								docsparsedate=None
							
							doccount+=1
							
							source=Source.objects.create(
								short_ref=shortref,
								zotero_group_id=group_id,
								zotero_item_id=item_id,
								zotero_grouplibrary_name=grouplibrary_name,
								title=title,
								date=docsparsedate,
								order_in_shortref=doccount,
								is_british_library=True,
								
							)
							docpageorder=1
							for page in thisdocpages:
								SourcePageConnection.objects.create(
									source=source,
									page=page,
									order=docpageorder
								)
								docpageorder+=1
								
							
							thisdoc={'image_filenames':[]}
						
						
						
				print("%d sub-documents" %doccount)
				
				
# made a column named "skip" and flag goofy entries to ignore them
# cleared out rows that seem to be sitting between separate docs
# merged some data into the title colum, such as in 25563, where there's details on some of the letters
# tried to split some blocks like on 25561, where we see numerous notes within a block like "same date as previous entry, but different entry"
# 
# If there is a column like "VID" then we want to tag that voyage when we create the source!! -- see MS 25575
# 
# 
# **** 25560 HAD THE HEADER NOTE: "Henry Kelsall, Under-Secretary to the Treasury: 
# Letters to, from the South Sea Company: 1721-1730."
# 
# **** 25555 HAD THE HEADER NOTE: "The following appear to be letters sent & received by South Sea Co."
# 
# **** 25449 AND 25495 HAD A BUNCH OF EXTRA ITEMS AT THE BOTTOM OF THE SHEET THAT APPEAR TO BE BACKMATTER -- BUT WEREN'T GIVEN PAGE NUMERS. THESE WERE CUT FROM THE IMPORT.
# 
# **** 25550 HAS THE HEADER:  All following pertain to Committee of Correspondence
# 
# **** 25545 HAS THE HEADER, A LITTLE WAYS IN?: "All following meetings pertain to dividends annuities and balances of South Sea Company"
# 
# **** 25565 LOOKS WRONG TO ME
# 
# **** Without access to the metadata, I had to leave the 2-digit years assigned by the data entry folks. This will have to be updated later.
# 
# get filenames from 
# * "add" + csv filename + fse??? + 3-digit version of numeric portion of pagenumber + recto or verso + '.jpg'
# * like "add_ms_25570_fse004r.jpg"
# * ... and how do i make the iiif image urls? what's that pattern?
# # 
# 

# they were imported as 1800's -- have bumped them down to the 1700's
## squash them in django
# from document.models import *
# bl_sources=Source.objects.all().filter(short_ref__name__icontains='SSC Add MS')
# bl_sources.count()
# bl_sources.filter(date__year__lte=1799).count()
# bl_sources.filter(date__year__gte=1799).count()
# 
# for bls in bl_sources:
# 	bls_date=bls.date
# 	if bls_date is not None:
# 		if bls_date.year is not None:
# 			if bls_date.year > 1800:
# 				bls_date.year=bls_date.year-100
# 				bls_date.save()
# 
# bl_sources.filter(date__year__lte=1799).count()
# bl_sources.filter(date__year__gte=1799).count()

## and now do it for Zotero
# import re
# for page in range(259):
# 	offset=pagelength*page
# 	page_items=zot.items(limit=pagelength,start=offset)
# 	print(page,offset)
# 	updateitems=[]
# 	for pi in page_items:
# 		pi_date=pi['data']['date']
# 		if pi_date not in ['',None]:
# 			dateyear=re.findall('[0-9]{4}',pi_date)
# 			if len(dateyear)>0:
# 				year=int(dateyear[0])
# 				if year > 1799:
# 					newyear=year-100
# 					pi2=dict(pi)
# 					newdate=re.sub(str(year),str(newyear),pi_date)
# 					pi2['data']['date']=newdate
# 					pi2['meta']['parsedDate']=re.sub("/",'-',newdate)
# 					updateitems.append(pi2)
# 	if len(updateitems)>0:
# 		print("updating-->",[i['key'] for i in updateitems])
# 		zot.update_items(updateitems)