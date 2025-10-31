from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers import serialize
from django.db import models
from django.db.models import Count, Q
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance as DistanceFunction
from rest_framework import generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Trail, Town
from .serializers import (
    TrailListSerializer, TrailDetailSerializer, TrailGeoJSONSerializer,
    TrailCreateSerializer, TrailSummarySerializer, DistanceSerializer,
    BoundingBoxSerializer
)
from .filters import TrailFilter





# Pagination setup

class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class with default and max page size"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    
# Trail List and create
@extend_schema(tags=["Trails"], summary="List all trails or create a new trail")
class TrailListCreateView(generics.ListCreateAPIView):
    """
    List all trails or allows the creation a new trail
    """
    queryset = Trail.objects.all()
    serializer_class = None
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['trail_name', 'county', 'region']
    ordering_fields = ['trail_name', 'county', 'distance_km', 'difficulty']
    ordering = ['trail_name']

    def get_serializer_class(self):
        print(f"Serializer in use for {self.request.method}")
        if self.request.method == 'POST':
            return TrailCreateSerializer
        return TrailListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        min_length = self.request.query_params.get('min_length')
        max_length = self.request.query_params.get('max_length')
        difficulty = self.request.query_params.get('difficulty')

        if min_length:
            queryset = queryset.filter(distance_km__gte=min_length)
        if max_length:
            queryset = queryset.filter(distance_km__lte=max_length)
        if difficulty:
            queryset = queryset.filter(difficulty__iexact=difficulty)

        return queryset
   
    
# Trail details view
@extend_schema(tags=["Trails"], summary="Retrieve, update or delete a trail")
class TrailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trail.objects.all()
    serializer_class = TrailDetailSerializer
  
  
# Find Trails within a certain radius of a point  
@extend_schema(
    tags=["Spatial"],
    request=DistanceSerializer,
    responses={200: dict},
    examples=[
        OpenApiExample(
            "Find trails within 50km of Killarney",
            value={"latitude": 52.059, "longitude": -9.507, "radius_km": 50},
            request_only=True,
        )
    ],
)    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def trails_within_radius(request):
    try:
        lat = float(request.data.get("latitude"))
        lng = float(request.data.get("longitude"))
        radius_km = float(request.data.get("radius_km", 50))

        # Create Point object for user location
        user_location = Point(lng, lat, srid=4326)

        # Annotate and filter trails based on distance
        trails = (
            Trail.objects.annotate(distance=DistanceFunction("start_point", user_location))
            .filter(distance__lte=radius_km * 1000)
            .order_by("distance")
        )

        results = []
        for t in trails:
            results.append({
                "id": t.id,
                "name": t.trail_name,
                "county": t.county,
                "difficulty": t.difficulty,
                "distance_km": round(t.distance_km or 0, 2),
                "distance_from_point_km": round(t.distance.km, 2),
                "latitude": t.start_point.y,
                "longitude": t.start_point.x,
            })

        return Response({
            "search_point": {"lat": lat, "lng": lng},
            "radius_km": radius_km,
            "total_found": len(results),
            "nearest_trails": results,
        })

    except Exception as e:
        print("❌ Error in trails_within_radius:", e)
        return Response({"error": str(e)}, status=500)


# Find trails in bounding box
@extend_schema(
    tags=["Spatial"],
    request=BoundingBoxSerializer,
    responses={200: dict},
)
@api_view(['POST'])
@authentication_classes([])         
@permission_classes([AllowAny]) 
def trails_in_bounding_box(request):
    """
    Find trails within a bounding box
    """
    serializer = BoundingBoxSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        bbox = [
            data['min_longitude'],
            data['min_latitude'],
            data['max_longitude'],
            data['max_latitude']
        ]
        
        trails = Trail.objects.in_bounding_box(bbox)
        
        return Response({
            'bounding_box': {
                'min_longitude': data['min_longitude'],
                'min_latitude': data['min_latitude'],
                'max_longitude': data['max_longitude'],
                'max_latitude': data['max_latitude']
            },
            'count': trails.count(),
            'trails': TrailListSerializer(trails, many=True).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
     
# Trail statistics view
@api_view(['GET'])
def trail_statistics(request):
    stats = {
        "total_trails": Trail.objects.count(),
        "average_distance_km": Trail.objects.aggregate(avg=models.Avg("distance_km"))["avg"] or 0,
        "max_elevation_gain": Trail.objects.aggregate(max=models.Max("elevation_gain_m"))["max"] or 0,
        "easy_count": Trail.objects.filter(difficulty__iexact="easy").count(),
        "moderate_count": Trail.objects.filter(difficulty__iexact="moderate").count(),
        "hard_count": Trail.objects.filter(difficulty__in=["hard", "challenging"]).count(),

    }
    serializer = TrailSummarySerializer(stats)
    return Response(serializer.data)


# Sample map view
def trail_map(request):
    """Render the main project map (templates/trails/map.html)."""
    return render(request, 'trails/map.html')

# Return towns in GeoJSON format
@api_view(['GET'])
def towns_geojson(request):
    towns = Town.objects.all()

    # Fiters
    min_population = request.GET.get('min_population')
    max_population = request.GET.get('max_population')
    town_type = request.GET.get('town_type')

    if min_population:
        towns = towns.filter(population__gte=int(min_population))
    if max_population:
        towns = towns.filter(population__lte=int(max_population))
    if town_type:
        towns = towns.filter(town_type__iexact=town_type.strip())

    geojson = serialize(
        'geojson',
        towns,
        geometry_field='location',
        fields=('name', 'town_type', 'population', 'area')
    )
    return HttpResponse(geojson, content_type='application/json')

# Find nearest town with given coordinates
@api_view(['POST'])
def nearest_town(request):
    lat = request.data.get('latitude')
    lng = request.data.get('longitude')
    if not lat or not lng:
        return Response({'error': 'Latitude and longitude required'}, status=400)

    user_location = Point(float(lng), float(lat), srid=4326)
    nearest = Town.objects.annotate(distance=Distance('location', user_location)).order_by('distance').first()

    if not nearest:
        return Response({'error': 'No towns found'}, status=404)

    return Response({
        'name': nearest.name,
        'town_type': nearest.town_type,
        'distance_km': round(nearest.distance.km, 2)
    })


# Load towns from GeoJSON file
@api_view(['GET'])
def load_towns(request):
    with open("trails_api/data/sample_towns.geojson") as f:
        data = json.load(f)

    Town.objects.all().delete()

    count = 0
    for feature in data["features"]:
        props = feature["properties"]
        name = props.get("ENGLISH") or props.get("name")
        area = props.get("AREA")
        population = props.get("POPULATION") or props.get("population") or 0
        town_type = props.get("TOWN_TYPE") or props.get("town_type") or "Urban"

        lon, lat = feature["geometry"]["coordinates"]
        point = Point(float(lon), float(lat), srid=4326)  
        Town.objects.create(
            name=name,
            area=area,
            population=population,
            town_type=town_type,
            location=point
        )
        count += 1

    return Response({"status": f"✅ Loaded {count} towns successfully"})

# Return trails in GeoJSON format
@api_view(['GET'])
def trails_geojson(request):
    trails = Trail.objects.all()

    min_length = request.GET.get('min_length')
    max_length = request.GET.get('max_length')
    difficulty = request.GET.get('difficulty')
    county = request.GET.get('county')
    trail_type = request.GET.get('trail_type')

    if min_length:
        trails = trails.filter(distance_km__gte=float(min_length))
    if max_length:
        trails = trails.filter(distance_km__lte=float(max_length))
    if difficulty and difficulty.lower() in ['easy', 'moderate', 'hard']:
        trails = trails.filter(difficulty__iexact=difficulty.lower())
    if county:
        trails = trails.filter(county__icontains=county)
    if trail_type:
        trails = trails.filter(trail_type__icontains=trail_type)

    geojson = serialize(
        'geojson', trails,
        geometry_field='start_point',
        fields=('trail_name', 'county', 'distance_km', 'difficulty', 'dogs_allowed', 'parking_available')
    )
    return HttpResponse(geojson, content_type='application/json')


# Return basic API info
@api_view(['GET'])
def api_info(request):
    """
    Returns basic information about the Trails API.
    """
    info = {
        "api_name": "Trails API",
        "version": "1.0",
        "description": "Provides trail data, GeoJSON views, and trail search functionality for hiking routes in Ireland.",
        "endpoints": [
            "/api/trails/",
            "/api/trails/<id>/",
            "/api/trails/geojson/",
            "/api/trails/counties/",
            "/api/trails/info/",
            "/api/trails/search/",
        ],
    }
    return Response(info)


# Return list of countries with trails counts
@api_view(['GET'])
def counties_list(request):
    """
    Return list of countries with trails counts
    """
    counties = (Trail.objects
                 .values('country')
                 .annotate(trail_count=Count('id'))
                 .annotate(total_population=models.Sum('population'))
                 .annotate(capitals_count=Count('id', filter=Q(is_capital=True)))
                 .order_by('country'))
    
    return Response(list(counties))

# Trail search endpoint
@api_view(['GET'])
def trail_search(request):
    """Simple trail search endpoint"""
    q = request.query_params.get('q', '')
    if not q:
        return Response([], status=200)
    
    trails = Trail.objects.filter(name__icontains=q)[:10]
    return Response(TrailListSerializer(trails, many=True).data)

# Testing page
def api_test_page(request):
    """Simple frontend for testing API"""
    return render(request, 'api_test.html')

# Render map view
def trail_map(request):
    """Render the main project map (templates/cities/map.html)."""
    return render(request, 'trails/map.html')
