import pytest
from django.urls import reverse
from django.contrib.gis.geos import Point
from trails_api.models import Trail

@pytest.mark.django_db
def test_list_trails(client):
    """Test the list endpoint for trails"""
    Trail.objects.create(
        trail_name="Bray Head Loop",
        county="Wicklow",
        region="Leinster",
        distance_km=5.5,
        difficulty="Moderate",
        elevation_gain_m=250,
        description="A scenic coastal loop.",
        start_point=Point(-6.092, 53.200, srid=4326)
    )

    url = reverse('trails_api:trail-list-create')
    response = client.get(url)

    assert response.status_code == 200
    assert 'results' in response.data
    assert response.data['results'][0]['trail_name'] == "Bray Head Loop"


@pytest.mark.django_db
def test_within_radius(client):
    """Test the within-radius endpoint"""
    Trail.objects.create(
        trail_name="Croagh Patrick Trail",
        county="Mayo",
        region="Connacht",
        distance_km=7.6,
        difficulty="Hard",
        elevation_gain_m=750,
        description="Pilgrimage mountain trail.",
        start_point=Point(-9.667, 53.763, srid=4326)
    )

    url = reverse('trails_api:trails-within-radius')
    payload = {"latitude": 53.8, "longitude": -9.7, "radius_km": 50}

    response = client.post(url, payload, content_type="application/json")

    assert response.status_code == 200
    assert 'trails' in response.data
    assert response.data['count'] >= 1