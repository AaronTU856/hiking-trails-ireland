from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.db.models import Count, Avg, Q
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as DistanceFunction  # Add this import
from django.contrib.gis.db import models
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from .models import City
from .serializers import (
    TrailListSerializer, TrailDetailSerializer, TrailGeoJSONSerializer,
    TrailCreateSerializer, TrailSummarySerializer, DistanceSerializer,
    BoundingBoxSerializer
)
from .filters import TrailFilter

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny




class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema(tags=["Trails"], summary="List trails or Create", description="Filter, search and paginate.")
class CityListCreateView(generics.ListCreateAPIView):
    """
    List all cities or create a new city
    """
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['trail_name', 'county', 'region']
    ordering_fields = ['trail_name', 'county', 'distance_km', 'difficulty']
    ordering = ['trail_name']
   
# GeoJSON Endpoint 
@extend_schema(tags=["Trails"], summary="Retrieve, update or delete a trail")
class TrailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer
  
# Trails within radius  
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
    
    
    
    
def get_queryset(self):
    """Optionally filter queryset based on query parameters"""
    queryset = City.objects.all()
    
    # Additional custom filters
    min_population = self.request.query_params.get('min_population')
    if min_population:
        try:
            min_pop = int(min_population)
            queryset = queryset.filter(population__gte=min_pop)
        except ValueError:
            pass
    
    capitals_only = self.request.query_params.get('capitals_only')
    if capitals_only and capitals_only.lower() == 'true':
        queryset = queryset.filter(is_capital=True)
    
    return queryset

class TrailDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a city instance
    """
    queryset = Trail.objects.all()
    serializer_class = TrailDetailSerializer
    
    def get_serializer_class(self):
        """Use create serializer for updates"""
        if self.request.method in ['PUT', 'PATCH']:
            return CityCreateSerializer
        return CityDetailSerializer

class CityGeoJSONView(generics.ListAPIView):
    """
    Return cities as GeoJSON for mapping applications
    """
    queryset = Trail.objects.all()
    serializer_class = CityGeoJSONSerializer
    pagination_class = None
    #pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TrailFilter
    search_fields = ['name', 'country']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        geojson_data = serializer.data

        # FIX: handle nested FeatureCollection returned by serializer
        if isinstance(geojson_data, dict) and "features" in geojson_data:
            geojson_data = geojson_data["features"]

        return Response({
            "type": "FeatureCollection",
            "features": geojson_data
        })

@api_view(['GET'])
def trail_statistics(request):
    """
    Return statistical summary of cities data
    """
    stats = {
        'total_trails': Trail.objects.count(),
        'total_population': Trail.objects.aggregate(
            total=models.Sum('population')
        )['total'] or 0,
        'countries_count': Trail.objects.values('country').distinct().count(),
        'capitals_count': Trail.objects.filter(is_capital=True).count(),
        'average_population': Trail.objects.aggregate(
            avg=Avg('population')
        )['avg'] or 0,
    }
    
    # Largest and smallest cities
    largest = Trail.objects.order_by('-population').first()
    smallest = Trail.objects.order_by('population').first()
    
    stats['largest_trail'] = str(largest) if largest else 'N/A'
    stats['smallest_trail'] = str(smallest) if smallest else 'N/A'
    
    serializer = TrailSummarySerializer(stats)
    return Response(serializer.data)


@extend_schema(
    tags=["Spatial"],
    request=DistanceSerializer,
    responses={200: dict},
    examples=[
        OpenApiExample(
            "Find cities within 50km of Dublin",
            value={"latitude": 53.3498, "longitude": -6.2603, "radius_km": 50},
            request_only=True,
        )
    ],
)
@api_view(['POST'])
@authentication_classes([])          # <- no SessionAuthentication, so no CSRF
@permission_classes([AllowAny]) 



def trails_within_radius(request):
    """
    Find trails within specified radius of a point
    """
    serializer = DistanceSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        center_point = Point(
            data['longitude'], 
            data['latitude'], 
            srid=4326
        )
        
        # Use Django's built-in spatial lookup instead of custom manager method
        trails = Trail.objects.filter(
            location__distance_lte=(center_point, Distance(km=data['radius_km']))
        ).annotate(
            distance=DistanceFunction('location', center_point)  # Fixed: Use DistanceFunction
        ).order_by('distance')
        
        # Add distance to serialized data
        trail_data = TrailListSerializer(trails, many=True).data
        for i, trail in enumerate(trails):
            trail_data[i]['distance_km'] = round(trail.distance.km, 2)
        
        return Response({
            'center': {
                'latitude': data['latitude'],
                'longitude': data['longitude']
            },
            'radius_km': data['radius_km'],
            'count': trails.count(),
            'trails': trail_data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Spatial"],
    request=BoundingBoxSerializer,
    responses={200: dict},
    examples=[
        OpenApiExample(
            "BBox around Ireland-ish",
            value={
              "min_latitude": 51.3, "min_longitude": -10.6,
              "max_latitude": 55.5, "max_longitude": -5.4
            },
            request_only=True,
        )
    ],
)

@api_view(['POST'])
@authentication_classes([])          # <- no SessionAuthentication, so no CSRF
@permission_classes([AllowAny]) 
def cities_in_bounding_box(request):
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
        
        cities = City.objects.in_bounding_box(bbox)
        
        return Response({
            'bounding_box': {
                'min_longitude': data['min_longitude'],
                'min_latitude': data['min_latitude'],
                'max_longitude': data['max_longitude'],
                'max_latitude': data['max_latitude']
            },
            'count': cities.count(),
            'cities': CityListSerializer(cities, many=True).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def counties_list(request):
    """
    Return list of countries with city counts
    """
    counties = (Trails.objects
                 .values('country')
                 .annotate(city_count=Count('id'))
                 .annotate(total_population=models.Sum('population'))
                 .annotate(capitals_count=Count('id', filter=Q(is_capital=True)))
                 .order_by('country'))
    
    return Response(list(countries))

@api_view(['GET'])
def trail_search(request):
    """Simple trail search endpoint"""
    q = request.query_params.get('q', '')
    if not q:
        return Response([], status=200)
        trails = Trail.objects.filter(name__icontains=q)[:10]
    return Response(CityListSerializer(trails, many=True).data)

@api_view(['GET'])
def api_info(request):
    """
    Return API information and available endpoints
    """
    base_url = request.build_absolute_uri('/api/trails/')
    
    endpoints = {
        'cities_list': f"{base_url}",
        'cities_geojson': f"{base_url}geojson/",
        'city_detail': f"{base_url}{{id}}/",
        'cities_within_radius': f"{base_url}within-radius/",
        'cities_in_bbox': f"{base_url}bbox/",
        'statistics': f"{base_url}stats/",
        'countries': f"{base_url}countries/",
        'api_docs': request.build_absolute_uri('/api/docs/'),
    }
    
    return Response({
        'api_name': 'Trails API',
        'version': '1.0',
        'description': 'RESTful API for city data with spatial capabilities',
        'endpoints': endpoints,
        'features': [
            'Trails CRUD operations',
            'GeoJSON output',
            'Spatial queries (radius, bounding box)',
            'Filtering and search',
            'Pagination',
            'Statistics'
        ]
    })

def api_test_page(request):
    """Simple frontend for testing API"""
    return render(request, 'api_test.html')

def city_map(request):
    """Render the main project map (templates/cities/map.html)."""
    return render(request, 'trails/map.html')
