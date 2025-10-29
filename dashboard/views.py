from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from trails_api.models import Trail, Town
from django.db.models import Count, Avg, Sum

def index(request):
    """Main trail dashboard view"""
    context = {
        'total_trails': Trail.objects.count(),
        'total_towns': Town.objects.count(),
        'regions': Trail.objects.values_list('region', flat=True).distinct().order_by('region'),
        'difficulties': Trail.objects.values_list('difficulty', flat=True).distinct(),
        'trail_types': Trail.objects.values_list('trail_type', flat=True).distinct(),
    }
    return render(request, 'dashboard/index.html', context)

def analytics(request):
    """Trail analytics page"""
    trail_stats = Trail.objects.aggregate(
        total_trails=Count('id'),
        avg_distance=Avg('distance_km'),
        avg_elevation=Avg('elevation_gain_m'),
        total_distance=Sum('distance_km')
    )

    context = {
        'trail_stats': trail_stats,
        'total_towns': Town.objects.count(),
    }
    return render(request, 'dashboard/analytics.html', context)
