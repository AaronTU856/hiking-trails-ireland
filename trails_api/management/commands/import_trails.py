import csv
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from trails_api.models import Trail

class Command(BaseCommand):
    help = 'Import trails from a CSV file'
    
    def handle(self, *args, **kwargs):
        with open('data/trails.csv', newline='',encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Trail.objects.create(
                    trail_name=row['trail_name'],
                    county=row['county'],
                    region=row['region'],
                    distance_km=float(row['distance_km']),
                    difficulty=row['difficulty'],
                    elevation_gain_m=int(row['elevation_gain_m']),
                    description=row['description'],
                    start_point=Point(float(row['longitude']), float(row['latitude']), srid=4326),
                )
                self.stdout.write(f'Imported trail: {row["trail_name"]}')
        self.stdout.write(self.style.SUCCESS('Successfully imported trails from CSV'))