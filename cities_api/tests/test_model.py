import pytest
from django.contrib.gis.geos import Point
from cities_api.models import City

@pytest.mark.django_db
def test_city_str():
    c = City.objects.create(
        name="Testville", country="IE", region="Leinster",
        population=123456, location=Point(-6.26, 53.35, srid=4326)
    )
    assert "Testville" in str(c)
