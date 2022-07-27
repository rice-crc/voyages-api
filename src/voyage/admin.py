from django.contrib import admin
from django import forms
from voyage.models import *

class BroadRegionAdmin(admin.ModelAdmin):
    list_display = ('geo_location',)
    list_display_links = ('geo_location',)
    search_fields = ['geo_location']
    ordering = ['geo_location']

class RegionAdmin(admin.ModelAdmin):
    list_display = ('geo_location',)
    list_display_links = ('geo_location',)
    search_fields = ['geo_location']
    ordering = ['geo_location']

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('geo_location',)
    list_display_links = ('geo_location',)
    search_fields = ['geo_location']
    ordering = ['geo_location']

class VoyageCrewInline(admin.StackedInline):
	model=VoyageCrew
	max_num=1
	classes = ['collapse']

class VoyageDatesInline(admin.StackedInline):
	model = VoyageDates
	max_num=1
	classes = ['collapse']

class VoyageSlavesNumbersInline(admin.StackedInline):
	model=VoyageSlavesNumbers
	classes = ['collapse']
	max_num=1

class ParticularOutcomeAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=ParticularOutcome
	search_fields=['name']
	classes = ['collapse']

class SlavesOutcomeAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=SlavesOutcome
	search_fields=['name']
	classes = ['collapse']
	
class VesselCapturedOutcomeAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=VesselCapturedOutcome
	search_fields=['name']
	classes = ['collapse']

class OwnerOutcomeAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=OwnerOutcome
	search_fields=['name']
	classes = ['collapse']

class ResistanceAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=Resistance
	search_fields=['name']
	classes = ['collapse']

##Autocomplete won't work on this
##Until we update the voyages table to explicitly point at outcomes
##Which I'm still unclear about why it wasn't done that way
##But the number of selections on the outcome table is small enough
##That we don't hit any performance issues here
##So it can stay for now
##Until I figure out what's going to break when I migrate that.
##It is worth saying that I think it's currently broken
##Insofar as you can apply more than one outcome entry to each voyage
##But it doesn't appear that this has ever been done
##which on this admin page results in multiple possible outcome fields being allowed
class VoyageOutcomeInline(admin.StackedInline):
	max_num = 0
	classes = ['collapse']
	model=VoyageOutcome

class NationalityAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=Nationality
	search_fields=['name']
	classes = ['collapse']

class TonTypeAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=TonType
	search_fields=['name']
	classes = ['collapse']

class RigOfVesselAdmin(admin.ModelAdmin):
	list_display = ('name','value')
	list_display_links = ('name',)
	model=RigOfVessel
	search_fields=['name']
	classes = ['collapse']


class VoyageShipInline(admin.StackedInline):
	model = VoyageShip
	max_num = 1
	autocomplete_fields=[
		'nationality_ship',
		'ton_type',
		'rig_of_vessel',
		'vessel_construction_place',
		'vessel_construction_region',
		'registered_place',
		'registered_region',
		'imputed_nationality'
	]
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
		'imp_broad_region_slave_dis'
	]
	classes = ['collapse']

class VoyageSourcesConnectionInline(admin.StackedInline):
	model=VoyageSourcesConnection
	autocomplete_fields=['source','doc']
	fields=['source','text_ref','doc']
	classes = ['collapse']

class VoyageSourcesAdmin(admin.ModelAdmin):
	search_fields=['full_ref',]
	list_display=['full_ref','short_ref']
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
		VoyageOutcomeInline,
		VoyageShipInline,
		VoyageSlavesNumbersInline
	)
	fields=['voyage_id','dataset','voyage_groupings','voyage_in_cd_rom']
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
admin.site.register(ParticularOutcome, ParticularOutcomeAdmin)
admin.site.register(SlavesOutcome, SlavesOutcomeAdmin)
admin.site.register(VesselCapturedOutcome, VesselCapturedOutcomeAdmin)
admin.site.register(OwnerOutcome, OwnerOutcomeAdmin)
admin.site.register(Resistance, ResistanceAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(TonType, TonTypeAdmin)
admin.site.register(RigOfVessel, RigOfVesselAdmin)


