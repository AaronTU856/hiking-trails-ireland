from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import City

class CityGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = City
        geo_field = "geometry"
        fields = ("id", "name", "population", "country", "geom")

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CityGeoSerializer