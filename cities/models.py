

# Create your models here.
from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    population = models.IntegerField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    area_km2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    def __str__(self):
        return f"{self.name}, {self.country}"

    @property
    def coordinates(self):
        return [float(self.latitude), float(self.longitude)]
