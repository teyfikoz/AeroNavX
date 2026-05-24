import pytest

from aeronavx.core.emissions_advanced import (
    AircraftType,
    FuelType,
    calculate_flight_emissions,
    compare_saf_savings,
)


def test_calculate_flight_emissions_basic():
    result = calculate_flight_emissions(
        "IST",
        "JFK",
        aircraft_type=AircraftType.WIDE_BODY,
        fuel_type=FuelType.JET_A1,
        load_factor=0.85,
        code_type="iata",
    )

    assert result.distance_km > 0
    assert result.fuel_kg > 0
    assert result.total_co2_kg > 0
    assert result.co2_per_passenger_kg > 0


def test_compare_saf_savings():
    savings = compare_saf_savings(
        "IST",
        "JFK",
        saf_percentage=50.0,
        aircraft_type=AircraftType.WIDE_BODY,
        load_factor=0.85,
        code_type="iata",
    )

    assert savings.co2_reduction_kg > 0
    assert 0 < savings.reduction_percentage < 100


def test_invalid_load_factor():
    with pytest.raises(ValueError):
        calculate_flight_emissions("IST", "JFK", load_factor=1.5)
