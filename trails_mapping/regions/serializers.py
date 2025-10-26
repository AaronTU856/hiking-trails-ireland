from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Region

class RegionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Region
        geo_field = "geometry"  
        fields = (
            "id",
            "name",
            "country",
            "region_code",
            "region_type",
            "area_km2",
            "total_population",
            "population_density",
            "gdp_per_capita",
            "unemployment_rate",
            "admin_level",
            "geometry",
        )