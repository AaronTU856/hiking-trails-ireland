from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_map, name='hello_map'),
    path('api/locations/add/', views.add_location_api, name='add_location_api'),
    path('api/status/', views.api_status, name='api_status'),
    path('test/', views.environment_test, name='environment_test'),
]
