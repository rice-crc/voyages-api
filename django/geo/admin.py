from django.contrib import admin
from geo.models import Place, PlaceType

class PlaceAdmin(admin.ModelAdmin):
	fields=[
		'name',
		'longitude',
		'latitude',
		'child_of',
		'uid',
		'place_type'
	]
	
	model=Place
	
	@admin.display(description="Place Type")
	def get_place_type(self,obj):
		return obj.place_type.name
	
	list_display=('name','uid','longitude','latitude','get_place_type')
	search_fields=('name','uid','longitude','latitude')
	
admin.site.register(Place,PlaceAdmin)
admin.site.register(PlaceType)