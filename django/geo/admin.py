from django.contrib import admin
from django import forms
from geo.models import *

class PolygonAdmin(admin.ModelAdmin):
    list_display = ('shape',)
    list_display_links = ('shape',)
    search_fields = ['shape']
    ordering = ['shape']

class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ['name']
    ordering = ['name']

class SpatialExtentInLine(admin.StackedInline):
	
	model=Polygon
	
class LocationTypeInLine(admin.StackedInline):
	model=LocationType

class ChildOfInLine(admin.StackedInline):
	model=Location
	verbose_name = "Parent"
	verbose_name_plural="Parents"

class ParentOfInLine(admin.StackedInline):
	model=Location
	verbose_name = "Child"
	verbose_name_plural = "Children"

class AdjacencyAdmin(admin.ModelAdmin):
	list_display = ('source','target')
	list_display_links = ('source','target')
	search_fields = ['source','target']

class LocationAdmin(admin.ModelAdmin):
	inlines=(
		ChildOfInLine,
		ParentOfInLine
	)
	fields=[
		'name',
		'value',
		'location_type',
		'spatial_extent',
		'longitude',
		'latitude',
		'show_on_map',
		'show_on_main_map'
	]
	list_display=('id','name','value','longitude','latitude')
	search_fields=('name',)
	model=Location

# Voyage (main section)
admin.site.register(Adjacency, AdjacencyAdmin)
admin.site.register(Polygon, PolygonAdmin)
admin.site.register(LocationType,LocationTypeAdmin)
admin.site.register(Location, LocationAdmin)

