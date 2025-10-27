from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from trails_api.models import Trail

class Command(BaseCommand):
    help = 'Create sample Irish hiking trails'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample hiking trails...')

        trails_data = [
            ("Glendalough Spinc Trail", "Wicklow", "Leinster", 9.5, "moderate", 380, "Scenic trail overlooking Glendalough Valley.", -6.3406, 53.0107),
            ("Croagh Patrick Trail", "Mayo", "Connacht", 7.0, "hard", 750, "Pilgrimage route to the summit of Croagh Patrick.", -9.6583, 53.7644),
            ("Bray Head Loop", "Wicklow", "Leinster", 4.5, "easy", 240, "Coastal walk with views over Bray and the Irish Sea.", -6.0999, 53.2027),
            ("Ticknock Forest Trail", "Dublin", "Leinster", 6.0, "moderate", 350, "Forest loop with panoramic views of Dublin Bay.", -6.2521, 53.2563),
            ("Torc Waterfall Loop", "Kerry", "Munster", 6.5, "easy", 200, "Woodland trail to Torc Waterfall near Killarney.", -9.5012, 52.0092),
        ]

        for name, county, region, distance, difficulty, elevation, desc, lng, lat in trails_data:
            trail, created = Trail.objects.get_or_create(
                trail_name=name,
                defaults={
                    'county': county,
                    'region': region,
                    'distance_km': distance,
                    'difficulty': difficulty,
                    'elevation_gain_m': elevation,
                    'description': desc,
                    'start_point': Point(lng, lat),
                }
            )
            if created:
                self.stdout.write(f'✓ Created trail: {name}')
            else:
                self.stdout.write(f'- Trail already exists: {name}')

        self.stdout.write(
            self.style.SUCCESS(f'Sample trails created: {Trail.objects.count()} total.')
        )
