from django.contrib import admin
from document.models import *
from past.models import *
from voyage.models import *

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

class ZoteroEnslavedConnectionInline(admin.StackedInline):
	model=ZoteroEnslavedConnection
	autocomplete_fields=['enslaved']
	exclude_fields=['zotero_source']
	extra=0
	classes=['collapse']

class ZoteroEnslaverConnectionInline(admin.StackedInline):
	model=ZoteroEnslaverConnection
	autocomplete_fields=['enslaver']
	exclude_fields=['zotero_source']
	extra=0
	classes=['collapse']

class ZoteroVoyageConnectionInline(admin.StackedInline):
	model=ZoteroVoyageConnection
	autocomplete_fields=['voyage']
	exclude_fields=['zotero_source']
	extra=0
	classes=['collapse']

class ZoteroSourceAdmin(admin.ModelAdmin):
	model=ZoteroSource
	inlines=[
		ZoteroEnslavedConnectionInline,
		ZoteroEnslaverConnectionInline,
		ZoteroVoyageConnectionInline
	]
	search_fields=['zotero_title','zotero_date']
	readonly_fields=['item_url','zotero_url','legacy_source']
	list_display=('zotero_title','zotero_date')

admin.site.register(ZoteroSource, ZoteroSourceAdmin)
admin.site.register(SourcePage,SourcePageAdmin)