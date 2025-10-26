import pytest
from django.urls import reverse
from django.contrib.gis.geos import Point
from cities_api.models import City

@pytest.mark.django_db
def test_list_cities(client):
    City.objects.create(name="Dublin", country="IE", region="Leinster",
                        population=1200000, location=Point(-6.26, 53.35, srid=4326))
    url = reverse('city-list')
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data['results'][0]['name'] == "Dublin"

@pytest.mark.django_db
def test_within_radius(client):
    City.objects.create(name="Dublin", country="IE", region="Leinster",
                        population=1200000, location=Point(-6.26, 53.35, srid=4326))
    url = reverse('city-radius')
    payload = {"latitude": 53.3498, "longitude": -6.2603, "radius_km": 50}
    resp = client.post(url, payload, content_type="application/json")
    assert resp.status_code == 200
    assert resp.data['count'] >= 1
