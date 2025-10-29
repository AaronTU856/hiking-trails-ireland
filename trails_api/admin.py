# Register your models here.
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Trail

@admin.register(Trail)
class TrailAdmin(LeafletGeoAdmin):
    list_display = ('trail_name', 'county', 'nearest_town', 'difficulty', 'distance_km')
    search_fields = ('trail_name', 'county', 'nearest_town')
    list_filter = ('county', 'difficulty', 'dogs_allowed')
