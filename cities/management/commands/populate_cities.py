import os
from django.core.management.base import BaseCommand
from cities.models import City

class Command(BaseCommand):
    help = 'Populate database with sample city data'

    def handle(self, *args, **options):
        sample_cities = [
            {
                'name': 'Dublin',
                'country': 'Ireland',
                'population': 1388000,
                'latitude': 53.349805,
                'longitude': -6.26031,
                'description': 'Capital city of Ireland, known for its historic architecture and vibrant culture.',
                'founded_year': 988,
                'area_km2': 317.5,
                'timezone': 'Europe/Dublin'
            },
            {
                'name': 'New York',
                'country': 'United States',
                'population': 8336817,
                'latitude': 40.7128,
                'longitude': -74.0060,
                'description': 'The most populous city in the United States, known as "The Big Apple".',
                'founded_year': 1624,
                'area_km2': 783.8,
                'timezone': 'America/New_York'
            },
            {
                'name': 'Tokyo',
                'country': 'Japan',
                'population': 13960000,
                'latitude': 35.6762,
                'longitude': 139.6503,
                'description': 'Capital of Japan and one of the most populous metropolitan areas in the world.',
                'founded_year': 1603,
                'area_km2': 627.57,
                'timezone': 'Asia/Tokyo'
            },
            {
                'name': 'London',
                'country': 'United Kingdom',
                'population': 8982000,
                'latitude': 51.5074,
                'longitude': -0.1278,
                'description': 'Capital city of England and the United Kingdom, rich in history and culture.',
                'founded_year': 43,
                'area_km2': 1572.0,
                'timezone': 'Europe/London'
            },
            {
                'name': 'Sydney',
                'country': 'Australia',
                'population': 5312000,
                'latitude': -33.8688,
                'longitude': 151.2093,
                'description': 'Largest city in Australia, famous for its Opera House and Harbour Bridge.',
                'founded_year': 1788,
                'area_km2': 12367.7,
                'timezone': 'Australia/Sydney'
            },
            {
                'name': 'Paris',
                'country': 'France',
                'population': 2161000,
                'latitude': 48.8566,
                'longitude': 2.3522,
                'description': 'Capital of France, known as the "City of Light" and famous for art, fashion, and culture.',
                'founded_year': 250,
                'area_km2': 105.4,
                'timezone': 'Europe/Paris'
            },
            {
                'name': 'Berlin',
                'country': 'Germany',
                'population': 3669000,
                'latitude': 52.5200,
                'longitude': 13.4050,
                'description': 'Capital of Germany, known for its history, art scene, and nightlife.',
                'founded_year': 1237,
                'area_km2': 891.8,
                'timezone': 'Europe/Berlin'
            },
            {
                'name': 'São Paulo',
                'country': 'Brazil',
                'population': 12325000,
                'latitude': -23.5505,
                'longitude': -46.6333,
                'description': 'Largest city in Brazil and South America, major financial center.',
                'founded_year': 1554,
                'area_km2': 1521.11,
                'timezone': 'America/Sao_Paulo'
            }
        ]

        for city_data in sample_cities:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                country=city_data['country'],
                defaults=city_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created city: {city.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'City already exists: {city.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample cities population completed!')
        )