from django.contrib import admin
from document.models import *

class SourcePageAdmin(admin.ModelAdmin):
	readonly_fields=['page_url','image_filename','iiif_manifest_url','iiif_baseimage_url']
	search_fields=['page_url','image_filename']
	list_display=['page_url','image_filename']
	model=SourcePage

class SourcePageConnectionInline(admin.StackedInline):
	model=SourcePageConnection
	extra=0
	fields=['source_page']
	classes = ['collapse']

class ZoteroSourceAdmin(admin.ModelAdmin):
	model=ZoteroSource
	search_fields=['zotero_title','zotero_date']
	readonly_fields=['item_url','zotero_url','legacy_source']
	autocomplete_fields=('voyages','enslaved_people','enslavers')
	list_display=('zotero_title','zotero_date')

class ZoteroVoyageConnectionAdmin(admin.ModelAdmin):
# 	readonly_fields=['zotero_source','voyage']
	search_fields=['zotero_source','voyage']
	autocomplete_fields=['zotero_source','voyage']

admin.site.register(ZoteroSource, ZoteroSourceAdmin)
admin.site.register(SourcePage,SourcePageAdmin)
admin.site.register(ZoteroVoyageConnection,ZoteroVoyageConnectionAdmin)