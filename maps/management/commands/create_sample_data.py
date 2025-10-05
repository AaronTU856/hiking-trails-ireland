import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, Polygon
from maps.models import Location, TestArea

class Command(BaseCommand):
    help = 'Create sample spatial data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample locations...')
        
        # Sample locations around Europe
        locations_data = [
            ("TUD Grangegorman Campus", 53.3515, -6.2749, "Technological University Dublin main campus"),
            ("Trinity College Dublin", 53.3438, -6.2546, "Historic university in Dublin city center"),
            ("Phoenix Park", 53.3558, -6.3298, "Large enclosed park in Dublin"),
            ("Dublin Castle", 53.3429, -6.2674, "Historic castle and government complex"),
            ("Temple Bar", 53.3448, -6.2635, "Cultural quarter with pubs and galleries"),
        ]
        
        for name, lat, lng, description in locations_data:
            location, created = Location.objects.get_or_create(
                name=name,
                defaults={
                    'point': Point(lng, lat),
                    'description': description
                }
            )
            if created:
                self.stdout.write(f'✓ Created location: {name}')
            else:
                self.stdout.write(f'- Location already exists: {name}')
        
        # Sample test areas (simplified polygons)
        areas_data = [
            ("Dublin City Center", [
                [-6.2800, 53.3350],
                [-6.2500, 53.3350], 
                [-6.2500, 53.3550],
                [-6.2800, 53.3550],
                [-6.2800, 53.3350]
            ]),
            ("Phoenix Park Area", [
                [-6.3400, 53.3500],
                [-6.3200, 53.3500],
                [-6.3200, 53.3600], 
                [-6.3400, 53.3600],
                [-6.3400, 53.3500]
            ])
        ]
        
        for name, coordinates in areas_data:
            area, created = TestArea.objects.get_or_create(
                name=name,
                defaults={
                    'boundary': Polygon(coordinates)
                }
            )
            if created:
                self.stdout.write(f'✓ Created test area: {name} ({area.area_km2:.2f} km²)')
            else:
                self.stdout.write(f'- Test area already exists: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data creation complete! '
                f'Locations: {Location.objects.count()}, '
                f'Test Areas: {TestArea.objects.count()}'
            )
        )
