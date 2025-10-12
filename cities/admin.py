
# Register your models here.
from django.contrib import admin
from .models import City

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'population', 'latitude', 'longitude', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'country', 'description')
    ordering = ('name',)
   
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'population', 'description')
        }),
        ('Geographic Data', {
            'fields': ('latitude', 'longitude')
        }),
        ('Additional Details', {
            'fields': ('founded_year', 'area_km2', 'timezone'),
            'classes': ('collapse',)
        }),
    )