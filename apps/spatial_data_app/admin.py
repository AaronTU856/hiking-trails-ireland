# filepath: apps/spatial_data_app/admin.py
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import IrishCounty, EuropeanCity, TransportationRoute


@admin.register(IrishCounty)
class IrishCountyAdmin(OSMGeoAdmin):
    """Admin interface for Irish counties with map widget"""
    list_display = ("display_name_admin", "name_en", "name_ga", "area_display")
    search_fields = ("name_tag", "name_en", "name_ga", "alt_name")
    list_filter = ("name_en",)

    # Map widget defaults
    default_zoom = 7
    default_lat = 53.41291
    default_lon = -8.24389

    # ---- helpers shown in list_display ----
    def display_name_admin(self, obj):
        return obj.display_name
    display_name_admin.short_description = "County"

    def area_display(self, obj):
        # prefer stored area if present, otherwise from geometry helper
        if obj.area is not None:
            try:
                return f"{float(obj.area):.0f} units"
            except Exception:
                return f"{obj.area}"
        if getattr(obj, "area_km2", None):
            return f"{obj.area_km2:.0f} km²"
        return "N/A"
    area_display.short_description = "Area"


# ---- action helper (outside class so we can reuse/assign) ----
def export_selected_cities(modeladmin, request, queryset):
    """Export selected cities as CSV"""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="cities.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Country", "Population", "Latitude", "Longitude"])
    for city in queryset:
        lat = getattr(city, "latitude", None)
        lon = getattr(city, "longitude", None)
        writer.writerow([city.name, city.country, city.population, lat, lon])
    modeladmin.message_user(request, f"Exported {queryset.count()} cities to CSV")
    return response
export_selected_cities.short_description = "Export selected cities to CSV"


@admin.register(EuropeanCity)
class EuropeanCityAdmin(OSMGeoAdmin):
    """Admin interface for European cities with enhanced features"""
    list_display = ("name", "country", "population_formatted", "population_category", "coordinates")
    list_filter = ("country",)
    search_fields = ("name", "country")
    actions = [export_selected_cities]

    # Map widget defaults
    default_zoom = 4
    default_lat = 54.5260
    default_lon = 15.2551

    # ---- helpers shown in list_display / read-only rendering ----
    def population_formatted(self, obj):
        return f"{obj.population:,}"
    population_formatted.short_description = "Population"
    population_formatted.admin_order_field = "population"

    def coordinates(self, obj):
        try:
            return f"({obj.latitude:.4f}, {obj.longitude:.4f})"
        except Exception:
            return "N/A"
    coordinates.short_description = "Coordinates"


@admin.register(TransportationRoute)
class TransportationRouteAdmin(OSMGeoAdmin):
    """Admin interface for transportation routes"""
    list_display = ("route_name", "route_type", "length_display")
    list_filter = ("route_type",)
    search_fields = ("route_name",)

    # Map widget defaults
    default_zoom = 5
    default_lat = 52.0
    default_lon = 5.0

    def length_display(self, obj):
        try:
            return f"{obj.length_km:.1f} km"
        except Exception:
            return "N/A"
    length_display.short_description = "Length"
