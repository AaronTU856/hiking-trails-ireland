from django.urls import path
from . import views

urlpatterns = [
    path('', views.CityListView.as_view(), name='city-list'),
    path('statistics/', views.city_statistics, name='city-statistics'),
    path('welcome/', views.welcome, name='city-welcome'),
]