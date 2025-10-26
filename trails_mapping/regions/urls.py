from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegionListView.as_view(), name='region-list'),
    path('statistics/', views.RegionStatisticsView.as_view(), name='region-statistics'),
]
