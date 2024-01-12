from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Document, DocumentRevision, EntityDocument, EntityType, Transcription
from xml.etree import ElementTree
import json
import re
import requests

_dublin_core_labels = {
	"abstract": "Abstract",
	"accessRights": "Access Rights",
	"accrualMethod": "Accrual Method",
	"accrualPeriodicity": "Accrual Periodicity",
	"accrualPolicy": "Accrual Policy",
	"alternative": "Alternative Title",
	"audience": "Audience",
	"available": "Date Available",
	"bibliographicCitation": "Bibliographic Citation",
	"conformsTo": "Conforms To",
	"contributor": "Contributor",
	"coverage": "Coverage",
	"created": "Date Created",
	"creator": "Creator",
	"date": "Date",
	"dateAccepted": "Date Accepted",
	"dateCopyrighted": "Date Copyrighted",
	"dateSubmitted": "Date Submitted",
	"educationLevel": "Audience Education Level",
	"extent": "Extent",
	"format": "Format",
	"hasFormat": "Has Format",
	"hasPart": "Has Part",
	"hasVersion": "Has Version",
	"identifier": "Identifier",
	"instructionalMethod": "Instructional Method",
	"isFormatOf": "Is Format Of",
	"isPartOf": "Is Part Of",
	"isReferencedBy": "Is Referenced By",
	"isReplacedBy": "Is Replaced By",
	"isRequiredBy": "Is Required By",
	"issued": "Date Issued",
	"isVersionOf": "Is Version Of",
	"language": "Language",
	"license": "License",
	"mediator": "Mediator",
	"medium": "Medium",
	"modified": "Date Modified",
	"provenance": "Provenance",
	"publisher": "Publisher",
	"references": "References",
	"relation": "Relation",
	"replaces": "Replaces",
	"requires": "Requires",
	"rights": "Rights",
	"rightsHolder": "Rights Holder",
	"source": "Source",
	"spatial": "Spatial Coverage",
	"subject": "Subject",
	"tableOfContents": "Table Of Contents",
	"temporal": "Temporal Coverage",
	"valid": "Date Valid",
	"description": "Description",
	"title": "Title",
	"type": "Type",
	"DCMIType": "DCMI Type Vocabulary",
	"DDC": "DDC",
	"IMT": "IMT",
	"LCC": "LCC",
	"LCSH": "LCSH",
	"MESH": "MeSH",
	"NLM": "NLM",
	"TGN": "TGN",
	"UDC": "UDC",
	"Box": "DCMI Box",
	"ISO3166": "ISO 3166",
	"ISO639-2": "ISO 639-2",
	"ISO639-3": "ISO 639-3",
	"Period": "DCMI Period",
	"Point": "DCMI Point",
	"RFC1766": "RFC 1766",
	"RFC3066": "RFC 3066",
	"RFC4646": "RFC 4646",
	"RFC5646": "RFC 5646",
	"URI": "URI",
	"W3CDTF": "W3C-DTF",
	"Agent": "Agent",
	"AgentClass": "Agent Class",
	"BibliographicResource": "Bibliographic Resource",
	"FileFormat": "File Format",
	"Frequency": "Frequency",
	"Jurisdiction": "Jurisdiction",
	"LicenseDocument": "License Document",
	"LinguisticSystem": "Linguistic System",
	"Location": "Location",
	"LocationPeriodOrJurisdiction": "Location, Period, or Jurisdiction",
	"MediaType": "Media Type",
	"MediaTypeOrExtent": "Media Type or Extent",
	"MethodOfAccrual": "Method of Accrual",
	"MethodOfInstruction": "Method of Instruction",
	"PeriodOfTime": "Period of Time",
	"PhysicalMedium": "Physical Medium",
	"PhysicalResource": "Physical Resource",
	"Policy": "Policy",
	"ProvenanceStatement": "Provenance Statement",
	"RightsStatement": "Rights Statement",
	"SizeOrDuration": "Size or Duration",
	"Standard": "Standard",
	"Collection": "Collection",
	"Dataset": "Dataset",
	"Event": "Event",
	"Image": "Image",
	"InteractiveResource": "Interactive Resource",
	"MovingImage": "Moving Image",
	"PhysicalObject": "Physical Object",
	"Service": "Service",
	"Software": "Software",
	"Sound": "Sound",
	"StillImage": "Still Image",
	"Text": "Text",
	"domainIncludes": "Domain Includes",
	"memberOf": "Member Of",
	"rangeIncludes": "Range Includes",
	"VocabularyEncodingScheme": "Vocabulary Encoding Scheme"
}

_max_errors = 5 # Maximum number of *consecutive* errors for the APIs we call.
_voyages_cache_filename = '.cached_voyages_data'
_zotero_cache_filename = '.cached_zotero_data'

def _makeLabelValue(label, value, lang):
	return { 'label': { lang: [label] }, 'value': { lang: value } }

class Command(BaseCommand):
	help = """This command fetches data from multiple APIs and consolidates
	the information into a local Document entity"""
	
	def add_arguments(self, parser):
		parser.add_argument("--voyages-key")
		parser.add_argument("--voyages-url")
		parser.add_argument("--zotero-key")
		parser.add_argument("--zotero-url", default="https://api.zotero.org")
		parser.add_argument("--zotero-userid")
		parser.add_argument("--ignore-cache")

	@staticmethod
	def _get_zotero_data(options, group_ids: list[int]):
		# Check if we already have cached data from the Zotero API.
		if not options.get('--ignore-cache', False):
			try:
				with open(_zotero_cache_filename, encoding='utf-8') as f:
					cached = json.load(f)
					print(f"Imported {len(cached.keys())} Zotero entries from cached file")
					return cached
			except:
				print("No cached Zotero data")

		def extract_from_rdf(rdf):
			# Map all the entries first and later keep only those that have a
			# Dublin Core label, and for those we use that label for the key
			# value instead of the original XML tag's name.
			complete = {}
			for e in rdf:
				key = re.match('^{.*}(.*)$', e.tag)[1]
				val = complete.setdefault(key, [])
				val.append(e.text)
			return { _dublin_core_labels[key]: val
					for key, val in complete.items() if key in _dublin_core_labels }

		def zotero_page(start: int, group_id: str, limit=100):
			res = requests.get( \
				f"{options['zotero_url']}/groups/{group_id}/items?" + \
				f"start={start}&limit={limit}&content=rdf_dc", \
				headers={ 'Authorization': f"Bearer {options['zotero_key']}" }, \
				timeout=60)
			page = ElementTree.fromstring(res.content)
			# Select the content nodes and navigate through RDF elements until
			# we reach http://www.w3.org/1999/02/22-rdf-syntax-ns#Description.
			# The following will build a dictionary, indexed by Zotero ids,
			# where each entry is the RDF data of the Zotero item.
			entries = {
				e.find('{http://zotero.org/ns/api}key').text:
					e.find('.//{http://www.w3.org/2005/Atom}content/*[1]/*[1]') for
					e in page.findall('.//{http://www.w3.org/2005/Atom}entry')
			}
			count = len(entries)
			# Replace the XML element in the dict values by a dictionary of RDF
			# attributes with their respective values.
			page = {
				key: extract_from_rdf(rdf)
				for key, rdf in entries.items() if rdf is not None
			}
			return (page, count)

		zotero_data = {}
		for group_id in group_ids:
			zotero_start = 0
			error_count = 0
			last_error = None
			while True:
				if error_count >= _max_errors:
					raise Exception(f"Too many failures fetching data from the Zotero API: {last_error}")
				try:
					(page, count) = zotero_page(zotero_start, group_id, 100)
					print(f"Fetched {count} records from Zotero's API/{len(page)} items with proper data.")
					if count == 0:
						break
					zotero_start += count
					zotero_data.update(page)
					error_count = 0
				except Exception as ex:
					last_error = ex
					error_count += 1
			# Now get bib info from Zotero.
			error_count = 0
			zotero_start = 0
			while True:
				if error_count >= _max_errors:
					raise Exception(f"Too many failures fetching data from the Zotero API: {last_error}")
				try:
					res = requests.get( \
						f"{options['zotero_url']}/groups/{group_id}/items?start={zotero_start}" + \
						"&limit=100&format=json&include=bib&style=chicago-fullnote-bibliography", \
						headers={ 'Authorization': f"Bearer {options['zotero_key']}" }, \
						timeout=60)
					page = res.json()
					if not page:
						break
					print(f"Fetched bibliography from Zotero's API [{len(page)}].")
					for item in page:
						key = item['key']
						if key in zotero_data:
							zd = zotero_data[key]
							zd['bib'] = item['bib']
							zd['zotero_doc_url'] = item['links']['alternate']['href']
					zotero_start += len(page)
				except Exception as ex:
					last_error = ex
					error_count += 1
		# Save to a local cache
		try:
			with open(_zotero_cache_filename, 'w', encoding='utf-8') as f:
				json.dump(zotero_data, f)
		except:
			print("Failed to write Zotero data to the cache")
		return zotero_data
	
	@staticmethod
	def _get_voyages_data(options):
		# Check if we already have cached data from the Zotero API.
		if not options.get('--ignore-cache', False):
			try:
				with open(_voyages_cache_filename, encoding='utf-8') as f:
					cached = json.load(f)
					print(f"Imported {len(cached.keys())} Voyage entries from cached file")
					return cached
			except:
				print("No cached Voyage data")
		voyages_data = {}
		sv_headers = { "Authorization": f"Token {options['voyages_key']}" }
		offset = 0
		error_count = 0
		last_error = None
		while True:
			if error_count >= _max_errors:
				raise Exception(f"Too many failures fetching data from the Voyages API: {last_error}")
			try:
				res = requests.get(
					f"{options['voyages_url']}/docs/GENERIC/?limit=10&offset={offset}",
					headers=sv_headers,
					timeout=60)
				page = res.json()['results']
				if not page:
					break
				voyages_data.update({ item['zotero_item_id']: item for item in page })
				print(f"Fetched {len(page)} rows [first id={page[0]['id']}]")
				error_count = 0
				offset += len(page)
			except Exception as ex:
				last_error = ex
				error_count += 1
				continue
		# Save to a local cache
		try:
			with open(_voyages_cache_filename, 'w', encoding='utf-8') as f:
				json.dump(voyages_data, f)
		except:
			print("Failed to write Voyages data to the cache")
		return voyages_data
	
	@staticmethod
	def _map_connections(doc, etype, connections, field_name):
		conn = set()
		for item in connections:
			if item.get(field_name):
				entity_key = item[field_name].get('id')
				if entity_key:
					conn.add(entity_key)
		for ekey in conn:
			edoc = EntityDocument(document=doc, entity_type=etype, entity_key=ekey)
			edoc.save()

	@staticmethod
	def _extract_iiif_url(url):
		if url is None or url == '':
			return None
		m = re.match('^(https?://)([^/]+)(.*)/full/(full|max)/0/default.jpg$', url)
		if not m:
			raise Exception(f"Bad format for IIIF url: '{url}'")
		return [m.group(i) for i in [2, 3]]
	
	def handle(self, *args, **options):
		zotero_groups_url = f"{options['zotero_url']}/users/{options['zotero_userid']}/groups"
		res = requests.get(zotero_groups_url, timeout=30)
		# Retrieve the group ids from the Zotero API.
		group_ids = [item['id'] for item in res.json() if item['data']['name']]
		print(f"Zotero group ids are: {group_ids}")
		zotero_data = Command._get_zotero_data(options, group_ids)
		voyages_data = Command._get_voyages_data(options)
		docs = {d.key: d for d in Document.objects.prefetch_related('revisions').all()}
		entity_types = {t.name: t for t in EntityType.objects.all()}
		timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
		imported_count = 0
		with transaction.atomic():
			for key, voyage_data in voyages_data.items():
				pages = [p['page'] for p in voyage_data['page_connections']]
				rdf = zotero_data.get(key)
				if not rdf:
					continue
				page_images = [pimg for pimg in
					[Command._extract_iiif_url(p.get('iiif_baseimage_url')) for p in pages]
					if pimg is not None]
				# At this point we have enough data to import to our db.
				doc = docs.get(key)
				if doc is None:
					doc = Document()
					doc.key = key
				# TODO: check whether there is already an identical revision and
				# prevent the creation of a duplicate.
				try:
					timestamp = datetime.strptime(voyage_data['last_updated'], timestamp_format)
				except:
					timestamp = datetime.now()
				doc.bib = rdf.pop('bib', None)
				doc.save()
				rev = DocumentRevision(
					document=doc, label=rdf.get('Title', 'No title'),
					status=DocumentRevision.Status.IMPORTED,
					timestamp=timestamp)
				rev.revision_number = 1
				# Generate metadata for the document.
				zotero_doc_url = rdf.pop('zotero_doc_url', None)
				metadata = [_makeLabelValue(k, val, 'en') for k, val in rdf.items()]
				if zotero_doc_url:
					metadata.append(_makeLabelValue('Citation', [f"<span><a href='{zotero_doc_url}'>Zotero Entry</a></span>"], 'en'))
				rev.content = {
					'metadata': metadata,
					'page_images': page_images
				}
				rev.save()
				# Create entity links to the document.
				Command._map_connections(doc, entity_types['Voyages'], voyage_data.get('source_voyage_connections'), 'voyage')
				Command._map_connections(doc, entity_types['Enslaved'], voyage_data.get('source_enslaved_connections'), 'enslaved')
				Command._map_connections(doc, entity_types['Enslavers'], voyage_data.get('source_enslaver_connections'), 'enslaver')
				Command._map_connections(doc, entity_types['Voyage sources'], [{ 'src': voyage_data }], 'src')
				# Import transcript data.
				for i, page in enumerate(pages, 1):
					page_transc = page.get('transcription')
					if page_transc:
						# TODO: for now there is no language code in the source API
						transcription = Transcription(
							document_rev=rev, page_number=i,
							language_code='en', text=page_transc,
							is_translation=False)
						transcription.save()
				imported_count += 1
				if imported_count % 100 == 0:
					print(f"Imported {imported_count} documents")
		print("Import finished")
