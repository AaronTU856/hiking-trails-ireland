# filepath: cities_query/urls.py
from django.urls import path
from . import views
 
urlpatterns = [
    # Fixed URL pattern
    path('', views.city_list, name='city_list'),
    path('map/', views.map_view, name='map_view'),  # Add this if you want a map view
   
    # New proximity search endpoints
    path('api/nearest/', views.find_nearest_cities, name='find_nearest_cities'),
    path('api/radius/', views.cities_within_radius, name='cities_within_radius'),
]


