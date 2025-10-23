from rest_framework import generics
from .models import Region
from .serializers import RegionSerializer

# ✅ This view returns a list of regions (used by /api/regions/)
class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all().order_by("id")
    serializer_class = RegionSerializer


# ✅ This view returns summary statistics (used by /api/regions/statistics/)
from rest_framework.response import Response
from rest_framework.views import APIView

class RegionStatisticsView(APIView):
    def get(self, request, *args, **kwargs):
        total_regions = Region.objects.count()
        total_area = sum(r.area_km2 for r in Region.objects.all() if r.area_km2)
        avg_population_density = (
            sum(r.population_density for r in Region.objects.all() if r.population_density)
            / total_regions if total_regions else 0
        )

        data = {
            "total_regions": total_regions,
            "total_area_km2": round(total_area, 2),
            "avg_population_density": round(avg_population_density, 2),
        }
        return Response(data)