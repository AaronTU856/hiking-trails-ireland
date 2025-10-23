# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, RegionViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'regions', RegionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# european_mapping/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('dashboard.urls')),
]