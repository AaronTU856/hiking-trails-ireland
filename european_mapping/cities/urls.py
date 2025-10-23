from django.urls import path
from . import views

urlpatterns = [
    path('', views.CityListView.as_view(), name='city-list'),
    path('statistics/', views.CityStatisticsView.as_view(), name='city-statistics'),
]