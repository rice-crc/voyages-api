"""
Management command for generating IIIF manifests
"""

import json
import pathlib
import re
import requests

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Prefetch
from api.models import DocumentRevision, EntityDocument

# We special case these sources as they have issues with their IIIF Image
# Service preventing us from creating manifests that point directly to the image
# service, instead manifests from these sources will link directly to the image
# files.
_special_case_no_img_service = ['catalog.archives.gov']

def _get_api_and_profile(img_info):
	profile_source = img_info['profile'][0]
	level_match = re.match('.*(level[0-9]).*', profile_source)
	img_profile = re.match(".*/api/image/([0-9]+)/(level[0-9]).json$", profile_source)
	if img_profile:
		api_version = img_profile.group(1)
	else:
		# Try to get the api version from the context
		profile_source = img_info.get('@context', '')
		api_match = re.match("/api/image/([0-9]+)", profile_source)
		api_version = api_match.group(1) if api_match else None
	return (api_version, level_match.group(1) if level_match else None)

class Command(BaseCommand):
	"""
	IIIF manifest generation command
	"""

	help = """This command generate manifest files based on the documents
		marked for publication in the database"""

	def add_arguments(self, parser):
		parser.add_argument("--base-url")
		parser.add_argument("--out-dir", type=pathlib.Path,
							help="The output directory where the manifests should be placed")
		parser.add_argument("--status", nargs="*", type=int,
							default=DocumentRevision.Status.APPROVED,
							help="Only generate manifests with these status codes. " +
							"Default = PUBLISHED")

	def handle(self, *args, **options):
		revisions = DocumentRevision.objects \
			.select_related('document') \
			.prefetch_related('transcriptions') \
			.prefetch_related( \
				Prefetch('document__entities', EntityDocument.objects.prefetch_related('entity_type'))) \
			.filter(status__in=[int(s) for s in options['status']])
		revisions = list(revisions)
		print(f"Found {len(revisions)} revisions to publish")
		generated_count = 0
		for rev in revisions:
			with transaction.atomic():
				content = rev.content
				page_images = content['page_images']
				if not page_images:
					# Do not generate manifest without images.
					rev.status = DocumentRevision.Status.NO_IMAGES
					rev.save()
					continue
				# Generate manifest for this revision.
				base_id = f"{options['base_url']}/{rev.document.key}"
				first_thumb = None
				canvas = []
				abort = False
				transcriptions = list(rev.transcriptions.all())
				# We support multiple languages in the transcription so the same
				# page may appear multiple times.
				transcriptions = {page_num: [t for t in transcriptions if t.page_number == page_num]
								for page_num in {t.page_number for t in transcriptions}}
				for i, page in enumerate(page_images, 1):
					# A canvas page.
					host_addr = page[0]
					img_url_base = f"https://{host_addr}{page[1]}"
					img_info = requests.get(f"{img_url_base}/info.json", timeout=30).json()
					(api_version, profile_level) = _get_api_and_profile(img_info)
					use_img_service = not any(s in host_addr for s in _special_case_no_img_service)
					if use_img_service and not (api_version and profile_level):
						print("Failed to find API version and level for image service: " +
							  f"{rev.label} [{rev.document.key}]")
						abort = True
						break
					thumb = [
						{
							"id": f"{img_url_base}/full/300,300/0/default.jpg",
							"type": "Image",
							"format": "image/jpeg"
						}
					]
					if i == 1:
						first_thumb = thumb
					w = int(img_info['width'])
					h = int(img_info['height'])
					max_dim = max(w, h)
					max_len = 1920
					if max_dim > max_len:
						w = int(round(w * max_len / max_dim))
						h = int(round(h * max_len / max_dim))
					img_size_urlparam = f"{w},{h}" if use_img_service else 'max'
					canvas_body = {
						"id": f"{img_url_base}/full/{img_size_urlparam}/0/default.jpg",
						"type": "Image",
						"format": "image/jpeg",
						"width": img_info['width'],
						"height": img_info['height']
					}
					if use_img_service:
						canvas_body['service'] = [{
							"id": img_url_base,
							"type": f"ImageService{api_version}",
							"profile": profile_level
						}]
					canvas_id = f"{base_id}/canvas{i}"
					canvas_data = {
						"id": canvas_id,
						"type": "Canvas",
						"thumbnail": thumb,
						"height": h,
						"width": w,
						"items": [{
							"id": f"{canvas_id}/item1",
							"type": "AnnotationPage",
							"items": [{
								"id": f"{canvas_id}/item1/image1",
								"type": "Annotation",
								"motivation": "painting",
								"body": canvas_body,
								"target": canvas_id
							}]
						}]
					}
					transc = transcriptions.get(i)
					if transc:
						canvas_data["annotations"] = [{
							"id": f"{canvas_id}/annopage{idx_t}",
							"type": "AnnotationPage",
							"items": [{
								"id": f"{canvas_id}/annopage{idx_t}/anno1",
								"type": "Annotation",
								"motivation": "commenting",
								"body": {
									"type": "TextualBody",
									"language": t.language_code,
									"format": "text/html",
									"value": t.text
								},
								"target": canvas_id
							}]
						} for idx_t, t in enumerate(transc, 1)]
					canvas.append(canvas_data)
				if abort:
					break
				# Append entity connections to metadata.
				doc_links = {}
				for entity in rev.document.entities.all():
					et = entity.entity_type
					entity_links = doc_links.setdefault(et.name, [])
					link_url = et.url_format.format(key=entity.entity_key)
					link_label = et.url_label.format(key=entity.entity_key)
					entity_links.append(f"<span><a href='{link_url}'>{link_label}</a></span>")
				# Make a copy of the metadata so as not to overwrite the
				# revision's version.
				metadata = list(content['metadata'])
				for typename, entries in doc_links.items():
					link_item = {
						"label": { 'en': [f"Linked {typename}"] },
						"value": { 'en': entries }
					}
					metadata.append(link_item)
				manifest = {
					"@context": "http://iiif.io/api/presentation/3/context.json",
					"id": base_id,
					"type": "Manifest",
					"label": { 'en': [rev.label] },
					"metadata": metadata,
					"viewingDirection": "left-to-right",
					"behavior": ["paged"],
					"navDate": str(rev.timestamp),
					"thumbnail": first_thumb,
					"items": canvas
				}
				filename = f"{rev.document.key}_rev{str(rev.revision_number).zfill(3)}.json"
				out_dir: pathlib.Path = options['out_dir']
				with open(out_dir.joinpath(filename), 'w', encoding='utf-8') as f:
					json.dump(manifest, f)
				rev.status = DocumentRevision.Status.PUBLISHED
				rev.save()
				doc = rev.document
				doc.current_rev = rev.revision_number
				doc.thumbnail = first_thumb[0]['id']
				doc.save()
				generated_count += 1
				if generated_count % 50 == 0:
					print(f"Generated {generated_count} manifests")
