from django.contrib import admin
from event.models import Event,Date,EventType

admin.site.register(Event)
admin.site.register(Date)
admin.site.register(EventType)