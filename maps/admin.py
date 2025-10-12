from django.contrib.gis import admin
from .models import Location, TestArea

@admin.register(Location)
class LocationAdmin(admin.OSMGeoAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    # Map configuration
    default_zoom = 12
    display_wkt = True
    display_srid = True
    map_width = 600
    map_height = 400

@admin.register(TestArea)
class TestAreaAdmin(admin.OSMGeoAdmin):
    list_display = ['name', 'area_km2']
    readonly_fields = ['area_km2']
    
    # Map configuration for polygons
    default_zoom = 10
    map_width = 700
    map_height = 500


