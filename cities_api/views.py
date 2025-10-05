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
    CityListSerializer, CityDetailSerializer, CityGeoJSONSerializer,
    CityCreateSerializer, CitySummarySerializer, DistanceSerializer,
    BoundingBoxSerializer
)
from .filters import CityFilter

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny




class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema(tags=["Cities"], summary="List cities", description="Filter, search and paginate.")
class CityListCreateView(generics.ListCreateAPIView):
    """
    List all cities or create a new city
    """
    queryset = City.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CityFilter
    search_fields = ['name', 'country', 'region']
    ordering_fields = ['name', 'country', 'population', 'founded_year']
    ordering = ['-population']  # Default ordering
    
    def get_serializer_class(self):
        """Use different serializers for list vs create"""
        if self.request.method == 'POST':
            return CityCreateSerializer
        return CityListSerializer
    
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

class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a city instance
    """
    queryset = City.objects.all()
    serializer_class = CityDetailSerializer
    
    def get_serializer_class(self):
        """Use create serializer for updates"""
        if self.request.method in ['PUT', 'PATCH']:
            return CityCreateSerializer
        return CityDetailSerializer

class CityGeoJSONView(generics.ListAPIView):
    """
    Return cities as GeoJSON for mapping applications
    """
    queryset = City.objects.all()
    serializer_class = CityGeoJSONSerializer
    pagination_class = None
    #pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CityFilter
    search_fields = ['name', 'country']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        geojson_data = {
            "type": "FeatureCollection",
            "features": serializer.data
        }
        return Response(geojson_data)

@api_view(['GET'])
def city_statistics(request):
    """
    Return statistical summary of cities data
    """
    stats = {
        'total_cities': City.objects.count(),
        'total_population': City.objects.aggregate(
            total=models.Sum('population')
        )['total'] or 0,
        'countries_count': City.objects.values('country').distinct().count(),
        'capitals_count': City.objects.filter(is_capital=True).count(),
        'average_population': City.objects.aggregate(
            avg=Avg('population')
        )['avg'] or 0,
    }
    
    # Largest and smallest cities
    largest = City.objects.order_by('-population').first()
    smallest = City.objects.order_by('population').first()
    
    stats['largest_city'] = str(largest) if largest else 'N/A'
    stats['smallest_city'] = str(smallest) if smallest else 'N/A'
    
    serializer = CitySummarySerializer(stats)
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



def cities_within_radius(request):
    """
    Find cities within specified radius of a point
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
        cities = City.objects.filter(
            location__distance_lte=(center_point, Distance(km=data['radius_km']))
        ).annotate(
            distance=DistanceFunction('location', center_point)  # Fixed: Use DistanceFunction
        ).order_by('distance')
        
        # Add distance to serialized data
        city_data = CityListSerializer(cities, many=True).data
        for i, city in enumerate(cities):
            city_data[i]['distance_km'] = round(city.distance.km, 2)
        
        return Response({
            'center': {
                'latitude': data['latitude'],
                'longitude': data['longitude']
            },
            'radius_km': data['radius_km'],
            'count': cities.count(),
            'cities': city_data
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
    Find cities within a bounding box
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
def countries_list(request):
    """
    Return list of countries with city counts
    """
    countries = (City.objects
                 .values('country')
                 .annotate(city_count=Count('id'))
                 .annotate(total_population=models.Sum('population'))
                 .annotate(capitals_count=Count('id', filter=Q(is_capital=True)))
                 .order_by('country'))
    
    return Response(list(countries))

@api_view(['GET'])
def api_info(request):
    """
    Return API information and available endpoints
    """
    base_url = request.build_absolute_uri('/api/cities/')
    
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
        'api_name': 'Cities API',
        'version': '1.0',
        'description': 'RESTful API for city data with spatial capabilities',
        'endpoints': endpoints,
        'features': [
            'City CRUD operations',
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
