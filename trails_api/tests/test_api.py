import pytest
from django.urls import reverse
from django.contrib.gis.geos import Point
from trails_api.models import Trail, Town

@pytest.mark.django_db
def test_list_trails(client):
    Trail.objects.create(
        trail_name="Croagh Patrick", county="Mayo", distance_km=7.5,
        difficulty="Hard", elevation_gain_m=764, start_point=Point(-9.657, 53.764, srid=4326)
    )
    url = reverse('trails-geojson')  # or your endpoint name
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_towns_geojson(client):
    Town.objects.create(name="Westport", town_type="Urban", population=6000, location=Point(-9.5167, 53.8, srid=4326))
    url = reverse('towns-geojson')  # adjust to match your route
    resp = client.get(url)
    assert resp.status_code == 200
