from django.contrib import admin
from geo.models import Place
from past.models import *
from event.models import Event

# Register your models here.

class EventInline(admin.TabularInline):
	model=Event

class PersonEventConnectionInline(admin.TabularInline):
	model=EnslaverAlias.enslavement_events.through
	extra=0

class EnslaverAliasAdmin(admin.ModelAdmin):
	model=EnslaverAlias
	fields=['alias','uid']
	search_fields=['alias','uid']
	inlines=(PersonEventConnectionInline,)

class EnslaverAliasInline(admin.TabularInline):
	model=EnslaverAlias
	inlines=(PersonEventConnectionInline,)
	extra=0

class EnslaverIdentityAdmin(admin.ModelAdmin):
	inlines=(
		EnslaverAliasInline,
	)
	fields=[
		'principal_alias',
		'birth',
		'death',
		'father_name',
		'father_occupation',
		'mother_name',
		'marriages',
		'probate_date',
		'will_value_pounds',
		'will_value_dollars',
		'will_court',
		'text_id',
		'first_active_year',
		'last_active_year',
		'number_enslaved',
		'principal_location',
		'references'
	]
	

admin.site.register(Role)
admin.site.register(EnslaverIdentity,EnslaverIdentityAdmin)
admin.site.register(EnslaverAlias,EnslaverAliasAdmin)
admin.site.register(PersonEventConnection)