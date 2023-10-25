from django.contrib import admin
from document.models import *
from past.models import *
from voyage.models import *

# class SourcePageAdmin(admin.ModelAdmin):
# 	readonly_fields=['page_url','image_filename','iiif_manifest_url','iiif_baseimage_url']
# 	search_fields=['page_url','image_filename']
# 	list_display=['page_url','image_filename']
# 	model=SourcePage

class ShortRefAdmin(admin.ModelAdmin):
	model=ShortRef
	search_fields=('name',)
	list_display=('name',)

class SourcePageConnectionInline(admin.StackedInline):
	model=SourcePageConnection
	extra=0
	fields=['source_page']
	classes = ['collapse']

class SourceEnslavedConnectionInline(admin.StackedInline):
	model=SourceEnslavedConnection
	autocomplete_fields=['enslaved']
	exclude_fields=['source']
	extra=0
	classes=['collapse']

class SourceEnslaverConnectionInline(admin.StackedInline):
	model=SourceEnslaverConnection
	autocomplete_fields=['enslaver']
	exclude_fields=['source']
	extra=0
	classes=['collapse']

class SourceVoyageConnectionInline(admin.StackedInline):
	model=SourceVoyageConnection
	autocomplete_fields=['voyage']
	exclude_fields=['source']
	extra=0
	classes=['collapse']

class SourceAdmin(admin.ModelAdmin):
	model=Source
# 	inlines=[
# 		SourceEnslavedConnectionInline,
# 		SourceEnslaverConnectionInline,
# 		SourceVoyageConnectionInline
# 	]
	autocomplete_fields=['short_ref']
	search_fields=['title','short_ref__name']
	readonly_fields=['item_url','zotero_item_id','zotero_group_id']
	list_display=('title','short_ref')

admin.site.register(Source, SourceAdmin)
admin.site.register(ShortRef,ShortRefAdmin)
# admin.site.register(SourcePage,SourcePageAdmin)