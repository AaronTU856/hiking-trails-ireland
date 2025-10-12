
# Create your views here.
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.http import JsonResponse
from .models import City
from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db import models
from .serializers import CitySerializer, CityListSerializer

@method_decorator(cache_page(60 * 5), name='get')  # Cache for 5 minutes
class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
   
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CityListSerializer
        return CitySerializer
    
    def perform_create(self, serializer):
        try:
            # Validate coordinates
            lat = float(serializer.validated_data['latitude'])
            lng = float(serializer.validated_data['longitude'])
           
            if not (-90 <= lat <= 90):
                raise ValidationError("Latitude must be between -90 and 90")
            if not (-180 <= lng <= 180):
                raise ValidationError("Longitude must be between -180 and 180")
           
            serializer.save()
        except (ValueError, ValidationError) as e:
            raise ValidationError(f"Invalid data: {str(e)}")

class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

@api_view(['GET'])
def cities_geojson(request):
    """Return cities data in GeoJSON format for Leaflet"""
    cities = City.objects.all()
   
    features = []
    for city in cities:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(city.longitude), float(city.latitude)]
            },
            "properties": {
                "id": city.id,
                "name": city.name,
                "country": city.country,
                "population": city.population,
                "description": city.description or "",
                "founded_year": city.founded_year,
                "area_km2": float(city.area_km2) if city.area_km2 else None,
                "timezone": city.timezone or "",
            }
        }
        features.append(feature)
   
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
   
    return JsonResponse(geojson, safe=False)

def map_view(request):
    """Render the main map page"""
    return render(request, 'cities/map.html')

@api_view(['GET'])
def city_search(request):
    """Search cities by name or country"""
    query = request.GET.get('q', '')
    if query:
        cities = City.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(country__icontains=query)
        )
    else:
        cities = City.objects.all()
   
    serializer = CityListSerializer(cities, many=True)
    return Response(serializer.data)
