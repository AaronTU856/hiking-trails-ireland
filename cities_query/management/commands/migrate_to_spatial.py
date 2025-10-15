# filepath -> management/commands/migrate_to_spatial.py
from django.core.management.base import BaseCommand
from cities_query.models import SpatialCity
 
class Command(BaseCommand):
    help = 'Populate database with sample spatial city data'
 
    def handle(self, *args, **options):
        cities_data = [
            {
                'name': 'Dublin',
                'country': 'Ireland',
                'population': 1173179,
                'latitude': 53.3498,
                'longitude': -6.2603,
                'description': 'The capital and largest city of Ireland',
                'founded_year': 988,
                'area_km2': 117.8,
                'timezone': 'Europe/Dublin'
            },
            {
                'name': 'London',
                'country': 'United Kingdom',
                'population': 8982000,
                'latitude': 51.5074,
                'longitude': -0.1278,
                'description': 'The capital and largest city of England and the United Kingdom',
                'founded_year': 47,
                'area_km2': 1572.0,
                'timezone': 'Europe/London'
            },
            {
                'name': 'Paris',
                'country': 'France',
                'population': 2161000,
                'latitude': 48.8566,
                'longitude': 2.3522,
                'description': 'The capital and most populous city of France',
                'founded_year': 259,
                'area_km2': 105.4,
                'timezone': 'Europe/Paris'
            },
            {
                'name': 'Berlin',
                'country': 'Germany',
                'population': 3669491,
                'latitude': 52.5200,
                'longitude': 13.4050,
                'description': 'The capital and largest city of Germany',
                'founded_year': 1237,
                'area_km2': 891.8,
                'timezone': 'Europe/Berlin'
            },
            {
                'name': 'Madrid',
                'country': 'Spain',
                'population': 3223334,
                'latitude': 40.4168,
                'longitude': -3.7038,
                'description': 'The capital and most populous city of Spain',
                'founded_year': 865,
                'area_km2': 604.3,
                'timezone': 'Europe/Madrid'
            },
            {
                'name': 'Rome',
                'country': 'Italy',
                'population': 2872800,
                'latitude': 41.9028,
                'longitude': 12.4964,
                'description': 'The capital city of Italy',
                'founded_year': -753,
                'area_km2': 1285.0,
                'timezone': 'Europe/Rome'
            },
            {
                'name': 'Amsterdam',
                'country': 'Netherlands',
                'population': 821752,
                'latitude': 52.3676,
                'longitude': 4.9041,
                'description': 'The capital and most populous city of the Netherlands',
                'founded_year': 1275,
                'area_km2': 219.3,
                'timezone': 'Europe/Amsterdam'
            },
            {
                'name': 'Brussels',
                'country': 'Belgium',
                'population': 1208542,
                'latitude': 50.8503,
                'longitude': 4.3517,
                'description': 'The capital and largest city of Belgium',
                'founded_year': 979,
                'area_km2': 161.4,
                'timezone': 'Europe/Brussels'
            },
            {
                'name': 'Vienna',
                'country': 'Austria',
                'population': 1911191,
                'latitude': 48.2082,
                'longitude': 16.3738,
                'description': 'The capital and largest city of Austria',
                'founded_year': 500,
                'area_km2': 414.6,
                'timezone': 'Europe/Vienna'
            },
            {
                'name': 'Copenhagen',
                'country': 'Denmark',
                'population': 602481,
                'latitude': 55.6761,
                'longitude': 12.5683,
                'description': 'The capital and most populous city of Denmark',
                'founded_year': 1167,
                'area_km2': 86.4,
                'timezone': 'Europe/Copenhagen'
            },
            {
                'name': 'Stockholm',
                'country': 'Sweden',
                'population': 975551,
                'latitude': 59.3293,
                'longitude': 18.0686,
                'description': 'The capital and largest city of Sweden',
                'founded_year': 1252,
                'area_km2': 188.0,
                'timezone': 'Europe/Stockholm'
            },
            {
                'name': 'Oslo',
                'country': 'Norway',
                'population': 695391,
                'latitude': 59.9139,
                'longitude': 10.7522,
                'description': 'The capital and most populous city of Norway',
                'founded_year': 1040,
                'area_km2': 454.0,
                'timezone': 'Europe/Oslo'
            }
        ]
 
        created_count = 0
        for city_data in cities_data:
            city, created = SpatialCity.objects.get_or_create(
                name=city_data['name'],
                country=city_data['country'],
                defaults=city_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {city.name}, {city.country}")
            else:
                self.stdout.write(f"Already exists: {city.name}, {city.country}")
 
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new cities')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total spatial cities in database: {SpatialCity.objects.count()}')
        )