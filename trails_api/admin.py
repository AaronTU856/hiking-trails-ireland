
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Trail

# Admin configuration for the Trail model using Leaflet map integration
@admin.register(Trail)
class TrailAdmin(LeafletGeoAdmin):
    list_display = (
        'trail_name',
        'county',
        'nearest_town',
        'difficulty',
        'distance_km',
        'dogs_allowed',
        'parking_available',
    )
 # Enables search by these fields
    search_fields = ('trail_name', 'county', 'nearest_town')
    
 # Adds filter options in the sidebar
    list_filter = ('county', 'difficulty', 'dogs_allowed')
