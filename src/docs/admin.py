from django.contrib import admin
from django import forms
from docs.models import *
from voyage.models import VoyageSources
from voyage.admin import VoyageSourcesAdmin

##BUG IN HERE SOMEWHERE. ONCE YOU CHOOSE A SOURCE YOU CAN'T NULL THE FIELD AGAIN?
class DocAdmin(admin.ModelAdmin):
	autocomplete_fields=[
		'source',]
	fields=['url','source']
	list_display=('id','url','source')
	search_fields=('id','url','source')
	model=Doc

# Voyage (main section)
admin.site.register(Doc, DocAdmin)