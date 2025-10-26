from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
from .models import Trail

class CityListSerializer(serializers.ModelSerializer):
    """Serializer for listing cities"""
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    
    class Meta:
        model = Trail
        fields = [
            'id', 'name', 'county', 'region', 'difficulty', 
            'latitude', 'longitude'
        ]


class TrailDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual trail"""
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    
    class Meta:
        model = Trail
        fields = [
            'id', 'name', 'county', 'region', 
            'location', 'latitude', 'longitude'
        ]



class CityGeoJSONSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for mapping applications"""
    
    class Meta:
        model = City
        geo_field = "location"
        fields = [
            "id",
            "name",
            "county",
            "area_km2",
            "timezone",
            "description",
            "latitude",
            "longitude",
        ]

class CityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating trails"""
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = Trail
        fields = [
            'name', 'county', 'region',
            'founded_year', 'latitude', 'longitude'
        ]
    
    def validate_latitude(self, value):
        """Validate latitude is within valid range"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude is within valid range"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value
    
    def create(self, validated_data):
        """Create city with Point geometry from lat/lng"""
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # Create Point geometry
        location = Point(longitude, latitude, srid=4326)
        validated_data['location'] = location
        
        return City.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update city, handling lat/lng if provided"""
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Update location if lat/lng provided
        if latitude is not None and longitude is not None:
            validated_data['location'] = Point(longitude, latitude, srid=4326)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class CitySummarySerializer(serializers.Serializer):
    """Serializer for city statistics summary"""
    total_trails = serializers.IntegerField()   
    counties_count = serializers.IntegerField()   
    largest_trail = serializers.CharField()
    smallest_trail = serializers.CharField()

class DistanceSerializer(serializers.Serializer):
    """Serializer for distance-based queries"""
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius_km = serializers.FloatField(min_value=0.1, max_value=20000)

class BoundingBoxSerializer(serializers.Serializer):
    """Serializer for bounding box queries"""
    min_latitude = serializers.FloatField(min_value=-90, max_value=90)
    min_longitude = serializers.FloatField(min_value=-180, max_value=180)
    max_latitude = serializers.FloatField(min_value=-90, max_value=90)
    max_longitude = serializers.FloatField(min_value=-180, max_value=180)
    
    def validate(self, data):
        """Validate that min values are less than max values"""
        if data['min_latitude'] >= data['max_latitude']:
            raise serializers.ValidationError("min_latitude must be less than max_latitude")
        
        if data['min_longitude'] >= data['max_longitude']:
            raise serializers.ValidationError("min_longitude must be less than max_longitude")
        
        return data