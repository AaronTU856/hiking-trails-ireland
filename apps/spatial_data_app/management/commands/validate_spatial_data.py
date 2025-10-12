# filepath: Week 1/spatial_data_app/management/commands/validate_spatial_data.py
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from apps.spatial_data_app.models import IrishCounty, EuropeanCity, TransportationRoute

class Command(BaseCommand):
    help = 'Validate imported spatial data and perform test queries'
   
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting spatial data validation..."))
       
        # Test 1: Count features
        counties_count = IrishCounty.objects.count()
        cities_count = EuropeanCity.objects.count()
        routes_count = TransportationRoute.objects.count()
       
        self.stdout.write(f"✓ Irish Counties: {counties_count}")
        self.stdout.write(f"✓ European Cities: {cities_count}") 
        self.stdout.write(f"✓ Transportation Routes: {routes_count}")
       
        # Test 2: Geometry validation
        invalid_geometries = 0
        for county in IrishCounty.objects.all():
            if not county.geom.valid:
                invalid_geometries += 1
                self.stdout.write(f"✗ Invalid geometry: {county.countyname}")
       
        if invalid_geometries == 0:
            self.stdout.write(self.style.SUCCESS("✓ All geometries are valid"))
       
        # Test 3: Spatial queries
        dublin_point = Point(-6.2603, 53.3498, srid=4326)
        nearby_cities = EuropeanCity.objects.within_distance_of_point(dublin_point, 500)
        self.stdout.write(f"✓ Cities within 500km of Dublin: {nearby_cities.count()}")
       
        # Test 4: Model properties
        largest_county = IrishCounty.objects.all().first()
        if largest_county:
            self.stdout.write(f"✓ Sample county area: {largest_county.area_km2:.0f} km²")
       
        # Test 5: Manager methods
        major_cities = EuropeanCity.objects.major_cities()
        self.stdout.write(f"✓ Major cities (>1M population): {major_cities.count()}")
       
        self.stdout.write(self.style.SUCCESS("Spatial data validation complete!"))