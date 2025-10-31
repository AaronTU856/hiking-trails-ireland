import pytest
from django.urls import reverse
from django.contrib.gis.geos import Point
from trails_api.models import Trail, Town


@pytest.mark.django_db
def test_list_trails(client):
    # Use namespaced name with underscore
    url = reverse('trails:trails_geojson')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_towns_geojson(client):
    # Use namespaced name and underscores
    url = reverse('trails:towns_geojson')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_trails_within_radius(client):
    url = reverse('trails:trails_within_radius')
    response = client.post(
        url,
        {'latitude': 53.0, 'longitude': -6.0, 'radius_km': 100},
        format='json'
    )
    assert response.status_code == 200

