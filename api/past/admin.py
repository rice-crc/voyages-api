from django.contrib import admin
from past.models import *
from document.models import *
from voyage.models import Place


class EnslavedInRelationInline(admin.StackedInline):
	model=EnslavedInRelation
	autocomplete_fields=['enslaved']
	readonly_fields=['relation']
	classes = ['collapse']
	extra=0

class EnslaverInRelationInline(admin.StackedInline):
	model=EnslaverInRelation
	autocomplete_fields=[
		'enslaver_alias'
	]
	readonly_fields=['relation']
	classes = ['collapse']
	extra=0


class EnslaverVoyageConnectionInline(admin.StackedInline):
	model=EnslaverVoyageConnection
	exclude=['order']
	autocomplete_fields=['voyage']
	classes = ['collapse']
	extra=0

class EnslaverAliasAdmin(admin.ModelAdmin):
	inlines=[EnslaverInRelationInline]
	autocomplete_fields=['identity']
	search_fields=['alias']


class EnslaverZoteroConnectionInline(admin.StackedInline):
	model=ZoteroEnslaverConnection
	autocomplete_fields=['zotero_source']
	extra=0
	classes=['collapse']

class EnslaverIdentityAdmin(admin.ModelAdmin):
	inlines=(
		EnslaverZoteroConnectionInline,
	)
	autocomplete_fields=['birth_place','death_place','principal_location']
	search_fields=['principal_alias',]

class EnslavedZoteroConnectionInline(admin.StackedInline):
	model=ZoteroEnslavedConnection
	autocomplete_fields=['zotero_source']
	extra=0
	classes=['collapse']

class EnslavedAdmin(admin.ModelAdmin):
	autocomplete_fields=[
		'post_disembark_location'
	]
	inlines=[EnslavedZoteroConnectionInline,EnslavedInRelationInline]
	search_fields=['documented_name']
	exclude=['voyage']

class EnslavementRelationAdmin(admin.ModelAdmin):
	model=EnslavementRelation
	readonly_fields=['is_from_voyages']
	exclude=['source','place','text_ref','unnamed_enslaved_count']
	
	inlines=[
		EnslavedInRelationInline,
		EnslaverInRelationInline
	]
	autocomplete_fields=[
		'voyage',
	]
	
admin.site.register(EnslavementRelation,EnslavementRelationAdmin)
admin.site.register(EnslaverIdentity,EnslaverIdentityAdmin)
admin.site.register(EnslaverAlias,EnslaverAliasAdmin)
admin.site.register(Enslaved,EnslavedAdmin)