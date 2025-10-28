import requests
import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, LineString
from trails_api.models import Trail
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = 'Fetch trail data from ArcGIS API and populate the database'
    
    def handle(self, *args, **options):
        url = (
                "https://services-eu1.arcgis.com/CltcWyRoZmdwaB7T/ArcGIS/rest/services/GetIrelandActiveTrailRoutes/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson&outSR=4326"

        )

        
        self.stdout.write(f"Fetching trail data from ArcGIS...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        self.stdout.write(f"Found {len(features)} trails to import.")

        imported, skipped = 0, 0
        for feature in features:
            props = feature.get("properties", {})
            
            if not imported:
                print(props.keys())
                
            geom = feature.get("geometry", {})

            name = props.get("Name") or props.get("Trail_Name") or "Unnamed Trail"
            if name.lower().startswith("unnamed"):
                skipped += 1
                continue

            # Handle line geometry (routes)
            if geom.get("type") == "LineString":
                coords = geom.get("coordinates")
                line = LineString(coords, srid=4326)
                start = Point(coords[0][0], coords[0][1], srid=4326)
            else:
                skipped += 1
                continue
            
            ascent_raw = props.get("AscentMetres")
            try:
                ascent = int(float(ascent_raw))
            except (ValueError, TypeError):
                ascent = 0
                
            # Distance in km
            length_value = (
                                props.get("LengthKm") or 
                                props.get("LengthKM") or 
                                props.get("Length in Km") or 
                                props.get("Length_km") or 
                                0
                            )

            try:
                distance = Decimal(str(length_value))
            except (ValueError, TypeError, InvalidOperation):
                distance = Decimal("0.00")

            Trail.objects.update_or_create(
                trail_name=name,
                defaults={
                    "activity": props.get("Activity") or props.get("TrailActivity"),
                    "county": props.get("County", "Unknown"),
                    "region": "Unknown",
                    "distance_km": distance,
                    "difficulty": (props.get("Difficulty") or "moderate").lower(),
                    "elevation_gain_m": ascent,
                    "description": props.get("Description", "Imported from ArcGIS"),
                    "start_point": start,
                    "dogs_allowed": props.get("DogsAllowed"),
                    "facilities": props.get("Facilities"),
                    "public_transport": props.get("PublicTransport"),
                    "trail_type": props.get("TrailType"),
                    "nearest_town": props.get("NearestTownStart") or "",
                },
            )
            if imported == 0:  # just print one example
                print(props.keys())

            imported += 1
            
       

        self.stdout.write(self.style.SUCCESS(f"✅ Imported {imported} new trails"))
        if skipped:
            self.stdout.write(self.style.WARNING(f"⚠️ Skipped {skipped} unnamed or invalid ones."))