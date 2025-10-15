#filepath: cities_query/models.py
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
 
# Keep your existing City model from Week 1
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    population = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    founded_year = models.IntegerField()
    area_km2 = models.FloatField()
    timezone = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"{self.name}, {self.country}"
 
# New spatial-enabled model
class SpatialCity(models.Model):
    # All fields from original City
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    population = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    founded_year = models.IntegerField()
    area_km2 = models.FloatField()
    timezone = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    # New spatial field
    location = models.PointField()  # PostGIS spatial field
   
    # Spatial database manager
    objects = models.Manager()
   
    def save(self, *args, **kwargs):
        # Automatically create Point from lat/lng when saving
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
        super().save(*args, **kwargs)
   
    @property
    def coordinates(self):
        return [self.longitude, self.latitude]
   
    def __str__(self):
        return f"{self.name}, {self.country}"
   
    class Meta:
        db_table = 'cities_spatialcity'