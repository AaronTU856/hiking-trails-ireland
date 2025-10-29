from django.db import models

# Create your models here.
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class TrailManager(models.Manager):
    """Custom manager for trail model with spatial queries"""
    
    def within_radius(self, center_point, radius_km):
        """
        Find trails within a specified radius of a point
        
        Args:
            center_point: Point object (longitude, latitude)
            radius_km: Radius in kilometers
        
        Returns:
            QuerySet of trails within the radius
        """
        return self.filter(
            start_point__distance_lte=(center_point, Distance(km=radius_km))
        )
    
    def in_bounding_box(self, bbox):
        """
        Find trails within a bounding box
        
        Args:
            bbox: List [min_lng, min_lat, max_lng, max_lat]
        
        Returns:
            QuerySet of trails within the bounding box
        """
        min_lng, min_lat, max_lng, max_lat = bbox
        
        # Create polygon from bounding box coordinates
        bbox_polygon = Polygon.from_bbox((min_lng, min_lat, max_lng, max_lat))
        
        return self.filter(start_point__within=bbox_polygon)
    
    def nearest_to_point(self, point, limit=10):
        """
        Find nearest trails to a point
        
        Args:
            point: Point object (longitude, latitude)
            limit: Maximum number of trails to return
        
        Returns:
            QuerySet of nearest trails ordered by distance
        """
        from django.contrib.gis.db.models.functions import Distance as DistanceFunction
        
        return self.annotate(
            distance=DistanceFunction('location', point)
        ).order_by('distance')[:limit]



# class City(models.Model):
#     """
#     Comprehensive city model with spatial capabilities
#     """
#     # Basic information
#     name = models.CharField(max_length=200, db_index=True)
#     country = models.CharField(max_length=100, db_index=True)
#     region = models.CharField(max_length=200, blank=True)
   
#     # Demographics
#     population = models.PositiveIntegerField()
   
#     # Geographic information
#     location = models.PointField(srid=4326, help_text="City center coordinates")
#     elevation_m = models.IntegerField(
#         null=True,
#         blank=True,
#         help_text="Elevation above sea level in meters"
#     )
   
#     # Historical data
#     founded_year = models.IntegerField(
#         null=True,
#         blank=True,
#         validators=[MinValueValidator(-4000), MaxValueValidator(2025)]
#     )
    
#     # Spatial field
#     location = models.PointField(srid=4326, help_text="Geographic coordinates")

#     description = models.TextField(blank=True, null=True)
#     area_km2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

   
#     # Administrative
#     is_capital = models.BooleanField(default=False)
#     timezone = models.CharField(max_length=50, blank=True)
   
#     # Metadata
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # Add the custom manager
#     objects = CityManager()

   
#     class Meta:
#         verbose_name_plural = "Cities"
#         ordering = ['-population']
#         indexes = [
#             models.Index(fields=['name']),
#             models.Index(fields=['country']),
#             models.Index(fields=['population']),
#         ]

   
    def __str__(self):
        return f"{self.trail_name}, {self.county}"
   
    @property
    def latitude(self):
        """Return latitude coordinate"""
        return self.start_point.y if self.start_point else None
   
    @property
    def longitude(self):
        """Return longitude coordinate"""
        return self.start_point.x if self.start_point else None
   
    @property
    def coordinates(self):
        """Return coordinates as [longitude, latitude] for GeoJSON"""
        return [self.longitude, self.latitude] if self.start_point else None
   
    # @property
    # def population_category(self):
    #     """Categorize city by population size"""
    #     if self.population >= 10000000:
    #         return "Megacity"
    #     elif self.population >= 5000000:
    #         return "Large Metropolis"
    #     elif self.population >= 1000000:
    #         return "Metropolis"
    #     elif self.population >= 500000:
    #         return "Large City"
    #     elif self.population >= 100000:
    #         return "City"
    #     else:
    #         return "Town"
   
    # @property
    # def age_years(self):
    #     """Calculate city age in years"""
    #     if self.founded_year:
    #         current_year = timezone.now().year
    #         return current_year - self.founded_year
    #     return None



class Trail(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('hard', 'Hard'),
    ]
    trail_name = models.CharField(max_length=100)

    path = gis_models.LineStringField(srid=4326, null=True, blank=True)
    trail_name = models.CharField(max_length=200, db_index=True)
    county = models.CharField(max_length=100, db_index=True)
    region = models.CharField(max_length=200, blank=True)
    distance_km = models.DecimalField(max_digits=20, decimal_places=2, help_text="Trail length in kilometers")
    difficulty = models.CharField(max_length=100, choices=DIFFICULTY_CHOICES, default='moderate')
    elevation_gain_m = models.IntegerField(help_text="Total elevation gain in meters")
    description = models.TextField(blank=True, null=True)
    start_point = gis_models.PointField(srid=4326, help_text="Trail start coordinates, longitude, latitude")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activity = models.CharField(max_length=100, blank=True)
    nearest_town = models.CharField(max_length=100, blank=True)
    dogs_allowed = models.CharField(max_length=50, blank=True)
    facilities = models.TextField(blank=True)
    public_transport = models.TextField(blank=True)
   
    trail_type = models.CharField(max_length=100, blank=True)
    parking_available = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Trail'
        verbose_name_plural = "Trails"
        ordering = ['trail_name']
        indexes = [
            models.Index(fields=['county'], name='trails_api_county_idx'),
            models.Index(fields=['difficulty'], name='trails_api_difficulty_idx'),
        ]

    def __str__(self):
        return f"{self.trail_name or 'Unnamed Trail'} ({self.county})"



# Add custom manager to City model
#City.add_to_class('objects', CityManager())