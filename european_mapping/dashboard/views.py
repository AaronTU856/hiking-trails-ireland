# dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from cities.models import City
from regions.models import Region
from django.db.models import Sum, Count, Avg

def index(request):
    """Main dashboard view"""
    context = {
        'total_cities': City.objects.count(),
        'total_regions': Region.objects.count(),
        'countries': City.objects.values_list('country', flat=True).distinct().order_by('country'),
        'region_types': Region.objects.values_list('region_type', flat=True).distinct(),
        'city_types': [choice[0] for choice in City._meta.get_field('city_type').choices],
    }
    return render(request, 'dashboard/index.html', context)

def analytics(request):
    """Analytics page with detailed statistics"""
    city_stats = City.objects.aggregate(
        total=Count('id'),
        avg_population=Avg('population'),
        total_population=Sum('population')
    )

    region_stats = Region.objects.aggregate(
        total=Count('id'),
        avg_population=Avg('total_population'),
        avg_area=Avg('area_km2'),
        total_population=Sum('total_population'),
        total_area=Sum('area_km2')
    )

    context = {
        'city_stats': city_stats,
        'region_stats': region_stats,
    }
    return render(request, 'dashboard/analytics.html', context)