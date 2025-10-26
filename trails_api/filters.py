import django_filters
from .models import Trail

class TrailFilter(django_filters.FilterSet):
    """Filter set for Trail model"""
   
    name = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    region = django_filters.CharFilter(lookup_expr='icontains')
   
    smallest_mountain = django_filters.NumberFilter(
        field_name='smallest',
        lookup_expr='gte'
    )
    highest_mountain = django_filters.NumberFilter(
        field_name='highest',
        lookup_expr='lte'
    )
   
    longest_trail = django_filters.NumberFilter(
        field_name='longest_trail',
        lookup_expr='gte'
    )
    shortest_trail = django_filters.NumberFilter(
        field_name='shortest_trail',
        lookup_expr='lte'
    )
   
   
    class Meta:
        model = Trail
        fields = ['county', 'difficulty', 'region']