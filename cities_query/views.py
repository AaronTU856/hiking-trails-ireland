# filepath: cities_query/views.py
from django.shortcuts import render
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SpatialCity
 
def city_list(request):
    """Display list of all spatial cities"""
    cities = SpatialCity.objects.all().order_by('name')
    return render(request, 'cities_query/city_list.html', {'cities': cities})
 
def map_view(request):
    """Display map view for spatial cities with proximity search"""
    return render(request, 'cities_query/map.html')
 
@api_view(['POST'])
def find_nearest_cities(request):
    """
    Find the 10 nearest cities to a given point
   
    POST /cities_query/api/nearest/
    Body: {"lat": 53.3498, "lng": -6.2603}
    """
    try:
        data = request.data
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
       
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return Response({
                'error': 'Invalid coordinates. Lat must be -90 to 90, lng must be -180 to 180'
            }, status=400)
       
        # Create a point from coordinates (PostGIS uses lng, lat order)
        search_point = Point(lng, lat, srid=4326)
       
        # Query for nearest 10 cities using PostGIS distance calculation
        nearest_cities = SpatialCity.objects.annotate(
            distance=Distance('location', search_point)
        ).order_by('distance')[:10]
       
        # Serialize results
        results = []
        for i, city in enumerate(nearest_cities, 1):
            results.append({
                'rank': i,
                'id': city.id,
                'name': city.name,
                'country': city.country,
                'population': city.population,
                'coordinates': {
                    'lat': city.latitude,
                    'lng': city.longitude
                },
                'distance_km': round(city.distance.km, 2),
                'distance_miles': round(city.distance.mi, 2),
                'description': city.description,
                'founded_year': city.founded_year,
                'area_km2': city.area_km2,
                'timezone': city.timezone
            })
       
        return Response({
            'search_point': {'lat': lat, 'lng': lng},
            'total_found': len(results),
            'nearest_cities': results
        })
       
    except (ValueError, TypeError) as e:
        return Response({
            'error': f'Invalid input: {str(e)}'
        }, status=400)
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=500)
 
@api_view(['POST'])
def cities_within_radius(request):
    """
    Find all cities within a specified radius
   
    POST /cities_query/api/radius/
    Body: {"lat": 53.3498, "lng": -6.2603, "radius_km": 100}
    """
    try:
        data = request.data
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        radius_km = float(data.get('radius_km', 100))  # Default 100km
       
        # Validate inputs
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return Response({'error': 'Invalid coordinates'}, status=400)
       
        if radius_km <= 0 or radius_km > 20000:  # Max ~half Earth circumference
            return Response({'error': 'Radius must be between 0 and 20000 km'}, status=400)
       
        search_point = Point(lng, lat, srid=4326)
       
        # Use PostGIS distance filter
        from django.contrib.gis.measure import Distance as D
       
        cities_in_radius = SpatialCity.objects.filter(
            location__distance_lte=(search_point, D(km=radius_km))
        ).annotate(
            distance=Distance('location', search_point)
        ).order_by('distance')
       
        results = []
        for city in cities_in_radius:
            results.append({
                'id': city.id,
                'name': city.name,
                'country': city.country,
                'population': city.population,
                'coordinates': {
                    'lat': city.latitude,
                    'lng': city.longitude
                },
                'distance_km': round(city.distance.km, 2),
                'distance_miles': round(city.distance.mi, 2),
                'description': city.description,
                'founded_year': city.founded_year,
                'area_km2': city.area_km2,
                'timezone': city.timezone
            })
       
        return Response({
            'search_point': {'lat': lat, 'lng': lng},
            'radius_km': radius_km,
            'total_found': len(results),
            'cities': results
        })
       
    except (ValueError, TypeError) as e:
        return Response({
            'error': f'Invalid input: {str(e)}'
        }, status=400)
    except Exception as e:
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=500)