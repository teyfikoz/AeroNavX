import pytest

from aeronavx.core.passenger_experience import calculate_jet_lag, JetLagSeverity, TravelDirection
from aeronavx.models.airport import Airport


def _airport(code, lon):
    return Airport(
        id=None,
        ident=code,
        type="large_airport",
        name=f"{code} Airport",
        latitude_deg=0.0,
        longitude_deg=lon,
        elevation_ft=None,
        continent=None,
        iso_country=None,
        iso_region=None,
        municipality=None,
        scheduled_service=None,
        gps_code=code,
        iata_code=code,
        local_code=None,
        home_link=None,
        wikipedia_link=None,
        keywords=None,
    )


def test_calculate_jet_lag_direction_and_severity():
    origin = _airport("AAA", 0.0)
    destination = _airport("BBB", 90.0)

    result = calculate_jet_lag(
        origin,
        destination,
        age=30,
        origin_offset=0.0,
        destination_offset=6.0,
    )

    assert result.timezone_difference_hours == 6.0
    assert result.direction == TravelDirection.EASTWARD
    assert result.severity == JetLagSeverity.SEVERE
    assert result.estimated_recovery_days > 0


def test_jet_lag_age_adjustment():
    origin = _airport("AAA", 0.0)
    destination = _airport("BBB", -60.0)

    younger = calculate_jet_lag(
        origin,
        destination,
        age=18,
        origin_offset=0.0,
        destination_offset=-4.0,
    )
    older = calculate_jet_lag(
        origin,
        destination,
        age=55,
        origin_offset=0.0,
        destination_offset=-4.0,
    )

    assert younger.estimated_recovery_days < older.estimated_recovery_days


def test_jet_lag_invalid_age():
    origin = _airport("AAA", 0.0)
    destination = _airport("BBB", 15.0)

    with pytest.raises(ValueError):
        calculate_jet_lag(origin, destination, age=0, origin_offset=0.0, destination_offset=1.0)
