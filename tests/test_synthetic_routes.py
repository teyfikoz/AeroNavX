import pytest

from aeronavx.core.synthetic_routes import generate_route
from aeronavx.models.airport import Airport


def _airport(code, lat, lon):
    return Airport(
        id=None,
        ident=code,
        type="large_airport",
        name=f"{code} Airport",
        latitude_deg=lat,
        longitude_deg=lon,
        elevation_ft=None,
        continent=None,
        iso_country=None,
        iso_region=None,
        municipality=None,
        scheduled_service=True,
        gps_code=code,
        iata_code=code,
        local_code=None,
        home_link=None,
        wikipedia_link=None,
        keywords=None,
    )


def test_generate_route_basic():
    origin = _airport("AAA", 0.0, 0.0)
    destination = _airport("BBB", 10.0, 10.0)

    route = generate_route(origin, destination, num_waypoints=5)

    assert route.total_distance_km > 0
    assert route.total_time_hours > 0
    assert len(route.waypoints) == 5


def test_generate_route_zero_waypoints():
    origin = _airport("AAA", 0.0, 0.0)
    destination = _airport("BBB", 5.0, 5.0)

    route = generate_route(origin, destination, num_waypoints=0)
    assert len(route.waypoints) == 0


def test_generate_route_invalid_waypoints():
    origin = _airport("AAA", 0.0, 0.0)
    destination = _airport("BBB", 5.0, 5.0)

    with pytest.raises(ValueError):
        generate_route(origin, destination, num_waypoints=-1)
