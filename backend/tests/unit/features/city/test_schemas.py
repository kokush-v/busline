import pytest
from pydantic import ValidationError

from app.features.city.schemas import CityCreate


def test_city_create_valid_bounds():
    payload = CityCreate(name="Valid", longitude=10.5, latitude=-20.1)
    assert payload.longitude == 10.5
    assert payload.latitude == -20.1


def test_city_create_invalid_longitude():
    with pytest.raises(ValidationError):
        CityCreate(name="BadLon", longitude=181.0, latitude=0.0)


def test_city_create_invalid_latitude():
    with pytest.raises(ValidationError):
        CityCreate(name="BadLat", longitude=0.0, latitude=91.0)
