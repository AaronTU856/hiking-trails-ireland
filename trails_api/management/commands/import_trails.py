
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from trails_api.models import Trail
import json

class Command(BaseCommand):
    help = 'Import trails from a GeoJSON file'
    
    def handle(self, *args, **options):
        path = 'trails_api/data/irish_mountains.geojson'

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {path}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid GeoJSON: {e}"))
            return

            
        features = data.get("features", [])
        if not features:
            self.stdout.write(self.style.WARNING("No features found in GeoJSON file."))
            return
        
        imported, skipped, duplicates = 0, 0, 0
        
        for feature in features:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})


            # Use NAMN1 for name
            name = (
                properties.get("NAMN1")
                or properties.get("name")
                or properties.get("trail_name")
            )
            
             # Skip unnamed trails/mountains
            if not name or name.strip().lower() in ["unnamed", ""]:
                skipped += 1
                continue

            # Get coordinates
            coords = geometry.get("coordinates")
            if not coords or len(coords) < 2:
                skipped += 1
                continue

            longitude, latitude = coords[0], coords[1]
            
            # Prevent any duplicates
            if Trail.objects.filter(
                trail_name=name,
                start_point__x=longitude,
                start_point__y=latitude,
            ).exists():
                duplicates += 1
                continue

            
            # Create or get trail
            Trail.objects.create(
                trail_name=name,
                county=properties.get("county", "Unknown"),
                region=properties.get("region", "Unknown"),
                distance_km=0.0,
                difficulty="moderate",
                elevation_gain_m=0,
                description="Imported from GeoJSON dataset",
                start_point=Point(longitude, latitude, srid=4326),
            )

            imported += 1
        
            # Print Results
            self.stdout.write(self.style.SUCCESS(f" Successfully imported {imported} trails!"))
            if duplicates:
                self.stdout.write(self.style.WARNING(f" Skipped {duplicates} duplicates."))
            if skipped:
                self.stdout.write(self.style.WARNING(f" Skipped {skipped} unnamed or invalid features."))

            # Display a few sample trails
            sample = Trail.objects.all()[:5]
            if sample:
                self.stdout.write("\nSample imported trails:")
                for trail in sample:
                    self.stdout.write(f" - {trail.trail_name} ({trail.start_point.y}, {trail.start_point.x})")
