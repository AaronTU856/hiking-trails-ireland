from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
from .models import Trail

class TrailListSerializer(serializers.ModelSerializer):
    """Serializer for listing cities"""
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    
    class Meta:
        model = Trail
        fields = [
            'id', 'trail_name', 'county', 'region', 'distance_km',
            'difficulty', 'elevation_gain_m', 'latitude', 'longitude'
        ]


class TrailDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual trail"""
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    
    class Meta:
        model = Trail
        fields = '__all__'
        



class TrailGeoJSONSerializer(GeoFeatureModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Trail
        geo_field = 'start_point'
        fields = (
            'id', 'trail_name', 'county',
            'distance_km', 'difficulty',
            'latitude', 'longitude'
        )

    def get_latitude(self, obj):
        return obj.start_point.y if obj.start_point else None

    def get_longitude(self, obj):
        return obj.start_point.x if obj.start_point else None
        

class TrailCreateSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = Trail
        fields = [
            'trail_name', 'county', 'region', 'distance_km',
            'difficulty', 'elevation_gain_m', 'description',
            'latitude', 'longitude'
        ]

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        validated_data['start_point'] = Point(longitude, latitude, srid=4326)
        return Trail.objects.create(**validated_data)

        
class TrailSummarySerializer(serializers.Serializer):
        total_trails = serializers.IntegerField()
        average_distance_km = serializers.FloatField()
        max_elevation_gain = serializers.FloatField()

class DistanceSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius_km = serializers.FloatField(min_value=0.1, max_value=20000)


class BoundingBoxSerializer(serializers.Serializer):
    min_latitude = serializers.FloatField(min_value=-90, max_value=90)
    min_longitude = serializers.FloatField(min_value=-180, max_value=180)
    max_latitude = serializers.FloatField(min_value=-90, max_value=90)
    max_longitude = serializers.FloatField(min_value=-180, max_value=180)

    def validate(self, data):
        if data['min_latitude'] >= data['max_latitude']:
            raise serializers.ValidationError("min_latitude must be less than max_latitude")
        if data['min_longitude'] >= data['max_longitude']:
            raise serializers.ValidationError("min_longitude must be less than max_longitude")
        return data