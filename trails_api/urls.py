from django.urls import path
from . import views
from .views import trail_map 
app_name = 'trails'

urlpatterns = [
    # Basic CRUD endpoints
    path('', views.TrailListCreateView.as_view(), name='trail-list-create'),
    path('<int:pk>/', views.TrailDetailView.as_view(), name='trail-detail'),
    
    path('search/', views.trail_search, name='trail_search'), 
   
    path('map/', trail_map, name='map'),
    
    # Special format endpoints
    path('geojson/', views.trails_geojson, name='trails_geojson'),

    path('towns/geojson/', views.TownGeoJSONView.as_view(), name='towns-geojson'),
    
    # Spatial query endpoints
    path('within-radius/', views.trails_within_radius, name='trails-within-radius'),
    path('bbox/', views.trails_in_bounding_box, name='trails-bbox'),
   
    # Statistics and metadata
    path('stats/', views.trail_statistics, name='trail-statistics'),
    path('counties/', views.counties_list, name='countries-list'),
    path('info/', views.api_info, name='api-info'),
    path('test/', views.api_test_page, name='api-test'),
    
    
    


]

