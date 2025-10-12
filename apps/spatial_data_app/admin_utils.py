# filepath: Week 1/spatial_data_app/admin_utils.py
from django.contrib import admin

from django.contrib.gis.admin import OSMGeoAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.gis.geos import Point

class SpatialDataAdminMixin:
    """Mixin for common spatial admin functionality"""
   
    def view_on_map_link(self, obj):
        """Create a link to view object on map"""
        if hasattr(obj, 'geom') and obj.geom:
            # Create link to a map view (you'd implement this view)
            url = reverse('admin:view_on_map', kwargs={
                'app_label': obj._meta.app_label,
                'model_name': obj._meta.model_name,
                'object_id': obj.pk
            })
            return format_html('<a href="{}" target="_blank">View on Map</a>', url)
        return "No geometry"
    view_on_map_link.short_description = "Map View"
   
    def geometry_type(self, obj):
        """Display geometry type"""
        if hasattr(obj, 'geom') and obj.geom:
            return obj.geom.geom_type
        return "None"
    geometry_type.short_description = "Geometry Type"

# Enhanced admin classes using the mixin
class EnhancedIrishCountyAdmin(OSMGeoAdmin, SpatialDataAdminMixin):
    list_display = ['countyname', 'area_display', 'geometry_type', 'view_on_map_link']
    # ... rest of configuration

