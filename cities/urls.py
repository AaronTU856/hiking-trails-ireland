from django.urls import path
from . import views

app_name = 'cities'

urlpatterns = [
    path('', views.map_view, name='map'),
    path('api/cities/', views.CityListCreateView.as_view(), name='city-list'),
    path('api/cities/<int:pk>/', views.CityDetailView.as_view(), name='city-detail'),
    path('api/cities/geojson/', views.cities_geojson, name='cities-geojson'),
    path('api/cities/search/', views.city_search, name='city-search'),
]


 