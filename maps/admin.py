from django.contrib import admin as dj_admin
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.gis.db.models import PointField, PolygonField
from django.contrib.gis.forms import OSMWidget
from .models import Location, TestArea

@dj_admin.register(Location)
class LocationAdmin(GISModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

    formfield_overrides = {
        PointField: {"widget": OSMWidget(attrs={
            "default_zoom": 12,
            "map_width": 600,
            "map_height": 400,
            "display_wkt": True,
            "display_srid": True,
        })}
    }

@dj_admin.register(TestArea)
class TestAreaAdmin(GISModelAdmin):
    list_display = ['name', 'area_km2']
    readonly_fields = ['area_km2']

    formfield_overrides = {
        PolygonField: {"widget": OSMWidget(attrs={
            "default_zoom": 10,
            "map_width": 700,
            "map_height": 500,
        })}
    }
