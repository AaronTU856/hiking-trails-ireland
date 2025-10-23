"""
URL configuration for european_mapping_v2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cities/', include('cities.urls')),
    path('api/regions/', include('regions.urls')),
    path('', views.map_view, name='map'),  # homepage map
    path('analytics/', views.analytics_view, name='analytics'),
    
    path('dashboard/', views.dashboard_index, name='dashboard_index'),
    path('dashboard/analytics/', views.analytics_view, name='dashboard_analytics'),
]

