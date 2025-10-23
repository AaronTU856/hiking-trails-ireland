from rest_framework import generics
from .models import City
from .serializers import CitySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg


class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = None


# ✅ Must be defined outside the class
@api_view(['GET'])
def city_statistics(request):
    data = {
        'total_cities': City.objects.count(),
        'avg_population': City.objects.aggregate(Avg('population'))['population__avg'] or 0,
    }
    return Response(data)


@api_view(['GET'])
def welcome(request):
    return Response({"message": "Welcome to the European Mapping API Service!"})
