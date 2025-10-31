import pytest
from django.contrib.gis.geos import Point
from trails_api.models import Trail, Town

@pytest.mark.django_db
def test_trail_str():
    t = Trail.objects.create(
        trail_name="Test Trail", county="Mayo", distance_km=5,
        difficulty="Moderate", elevation_gain_m=200, start_point=Point(-9.4, 53.8, srid=4326)
    )
    assert "Test Trail" in str(t)

@pytest.mark.django_db
def test_town_str():
    town = Town.objects.create(name="Westport", town_type="Urban", population=6000, location=Point(-9.5167, 53.8, srid=4326))
    assert "Westport" in str(town)
