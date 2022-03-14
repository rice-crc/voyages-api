from django.contrib import admin
from django import forms
from voyage.models import *

class BroadRegionAdmin(admin.ModelAdmin):
    list_display = ('broad_region', 'value', 'show_on_map')
    list_display_links = ('broad_region',)
    search_fields = ['broad_region', 'value']
    list_editable = ['show_on_map']


class RegionAdmin(admin.ModelAdmin):
    list_display = ('region', 'value', 'broad_region', 'show_on_map',
                    'show_on_main_map')
    list_display_links = ('region',)
    search_fields = ['region', 'value']
    list_editable = ['show_on_map', 'show_on_main_map']


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('place', 'value', 'region', 'longitude', 'latitude',
                    'show_on_main_map', 'show_on_voyage_map')
    list_display_links = ('place',)
    search_fields = ['place', 'value']
    ordering = ['value']
    list_editable = ['show_on_main_map', 'show_on_voyage_map']


class VoyageCrewInline(admin.StackedInline):
	model=VoyageCrew
	max_num=1
	classes = ['collapse']

class VoyageDatesInline(admin.StackedInline):
	model = VoyageDates
	max_num=1
	classes = ['collapse']

class VoyageItineraryInline(admin.StackedInline):
	model = VoyageItinerary
	max_num = 1
	autocomplete_fields=['imp_broad_region_voyage_begin',
		'port_of_departure',
		'int_first_port_emb',
		'int_second_port_emb',
		'int_first_region_purchase_slaves',
		'int_second_region_purchase_slaves',
		'int_first_port_dis',
		'int_second_port_dis',
		'int_first_region_slave_landing',
		'imp_principal_region_slave_dis',
		'int_second_place_region_slave_landing',
		'first_place_slave_purchase',
		'second_place_slave_purchase',
		'third_place_slave_purchase',
		'first_region_slave_emb',
		'second_region_slave_emb',
		'third_region_slave_emb',
		'port_of_call_before_atl_crossing',
		'first_landing_place',
		'second_landing_place',
		'third_landing_place',
		'first_landing_region',
		'second_landing_region',
		'third_landing_region',
		'place_voyage_ended',
		'region_of_return',
		'broad_region_of_return',
		'imp_port_voyage_begin',
		'imp_region_voyage_begin',
		'imp_broad_region_voyage_begin',
		'principal_place_of_slave_purchase',
		'imp_principal_place_of_slave_purchase',
		'imp_principal_region_of_slave_purchase',
		'imp_broad_region_of_slave_purchase',
		'principal_port_of_slave_dis',
		'imp_principal_port_slave_dis',
		'imp_broad_region_slave_dis=BroadRegionSerializer'
	]
	classes = ['collapse']

class VoyageSourcesConnectionInline(admin.StackedInline):
	model=VoyageSourcesConnection
	autocomplete_fields=['source']
	classes = ['collapse']

class VoyageSourcesAdmin(admin.ModelAdmin):
	search_fields=['full_ref']
	model=VoyageSources

class VoyageShipOwnerConnectionInline(admin.StackedInline):
	model=VoyageShipOwnerConnection
	autocomplete_fields=['owner']
	classes = ['collapse']

class VoyageShipOwnerAdmin(admin.ModelAdmin):
	model=VoyageShipOwner
	search_fields=['name']
	classes = ['collapse']

class VoyageCaptainConnectionInline(admin.StackedInline):
	model=VoyageCaptainConnection
	autocomplete_fields=['captain']
	classes = ['collapse']

class VoyageCaptainAdmin(admin.ModelAdmin):
	model=VoyageCaptain
	search_fields=['name']

class VoyageOutcomeInline(admin.StackedInline):
	model=VoyageOutcome
	classes = ['collapse']


class VoyageAdmin(admin.ModelAdmin):

	inlines=(
		VoyageDatesInline,
		VoyageItineraryInline,
		VoyageSourcesConnectionInline,
		VoyageShipOwnerConnectionInline,
		VoyageCaptainConnectionInline,
		VoyageCrewInline,
	)
	fields=['voyage_id','dataset',]
	list_display=('voyage_id',)
	search_fields=('voyage_id',)
	model=Voyage



# Voyage (main section)
admin.site.register(Voyage, VoyageAdmin)
admin.site.register(VoyageSources, VoyageSourcesAdmin)
admin.site.register(BroadRegion, BroadRegionAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(VoyageCaptain, VoyageCaptainAdmin)
admin.site.register(VoyageShipOwner, VoyageShipOwnerAdmin)





