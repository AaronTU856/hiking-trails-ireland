from rest_framework import serializers
from .models import City

class CitySerializer(serializers.ModelSerializer):
    coordinates = serializers.ReadOnlyField()
   
    class Meta:
        model = City
        fields = [
            'id', 'name', 'country', 'population', 'latitude',
            'longitude', 'coordinates', 'description', 'founded_year',
            'area_km2', 'timezone', 'created_at', 'updated_at'
        ]

class CityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    coordinates = serializers.ReadOnlyField()
   
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'population', 'coordinates']