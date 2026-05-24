from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..core.distance import distance
from ..core.loader import get_airport_by_iata, get_airport_by_icao
from ..exceptions import RoutingError
from ..utils.constants import DEFAULT_CO2_KG_PER_PAX_KM


class AircraftType(Enum):
    REGIONAL = "regional"
    NARROW_BODY = "narrow_body"
    WIDE_BODY = "wide_body"
    BUSINESS_JET = "business_jet"


class FuelType(Enum):
    JET_A1 = "jet_a1"
    SAF = "saf"


AIRCRAFT_SEATS = {
    AircraftType.REGIONAL: 90,
    AircraftType.NARROW_BODY: 180,
    AircraftType.WIDE_BODY: 300,
    AircraftType.BUSINESS_JET: 8,
}

FUEL_BURN_KG_PER_KM = {
    AircraftType.REGIONAL: 1200 / 1000.0,
    AircraftType.NARROW_BODY: 2500 / 1000.0,
    AircraftType.WIDE_BODY: 5200 / 1000.0,
    AircraftType.BUSINESS_JET: 900 / 1000.0,
}

FUEL_CO2_MULTIPLIER = {
    FuelType.JET_A1: 1.0,
    FuelType.SAF: 0.5,
}

CO2_PER_KG_FUEL = 3.16


@dataclass(frozen=True)
class EmissionsResult:
    distance_km: float
    fuel_kg: float
    total_co2_kg: float
    co2_per_passenger_kg: float
    load_factor: float
    aircraft_type: AircraftType
    fuel_type: FuelType


@dataclass(frozen=True)
class SafSavings:
    base_co2_kg: float
    saf_co2_kg: float
    co2_reduction_kg: float
    reduction_percentage: float


def _resolve_airports(from_code: str, to_code: str, code_type: str) -> tuple:
    if code_type == "iata":
        from_airport = get_airport_by_iata(from_code)
        to_airport = get_airport_by_iata(to_code)
    elif code_type == "icao":
        from_airport = get_airport_by_icao(from_code)
        to_airport = get_airport_by_icao(to_code)
    else:
        from_airport = get_airport_by_iata(from_code) or get_airport_by_icao(from_code)
        to_airport = get_airport_by_iata(to_code) or get_airport_by_icao(to_code)

    if from_airport is None:
        raise RoutingError(f"Origin airport not found: {from_code}")
    if to_airport is None:
        raise RoutingError(f"Destination airport not found: {to_code}")

    return from_airport, to_airport


def calculate_flight_emissions(
    from_code: str,
    to_code: str,
    aircraft_type: AircraftType = AircraftType.NARROW_BODY,
    fuel_type: FuelType = FuelType.JET_A1,
    load_factor: float = 0.85,
    code_type: str = "iata",
    model: str = "haversine",
) -> EmissionsResult:
    if not 0 < load_factor <= 1.0:
        raise ValueError("load_factor must be in (0, 1].")

    from_airport, to_airport = _resolve_airports(from_code, to_code, code_type)

    dist_km = distance(
        from_airport.latitude_deg,
        from_airport.longitude_deg,
        to_airport.latitude_deg,
        to_airport.longitude_deg,
        model=model,
        unit="km",
    )

    seats = AIRCRAFT_SEATS.get(aircraft_type, 180)
    passengers = max(int(seats * load_factor), 1)

    fuel_burn = FUEL_BURN_KG_PER_KM.get(aircraft_type, 2.5)
    fuel_kg = dist_km * fuel_burn

    co2_multiplier = FUEL_CO2_MULTIPLIER.get(fuel_type, 1.0)
    total_co2 = fuel_kg * CO2_PER_KG_FUEL * co2_multiplier
    per_passenger = total_co2 / passengers

    baseline_per_pax = dist_km * DEFAULT_CO2_KG_PER_PAX_KM
    per_passenger = max(per_passenger, baseline_per_pax * 0.5)

    return EmissionsResult(
        distance_km=dist_km,
        fuel_kg=fuel_kg,
        total_co2_kg=total_co2,
        co2_per_passenger_kg=per_passenger,
        load_factor=load_factor,
        aircraft_type=aircraft_type,
        fuel_type=fuel_type,
    )


def compare_saf_savings(
    from_code: str,
    to_code: str,
    saf_percentage: float = 50.0,
    aircraft_type: AircraftType = AircraftType.NARROW_BODY,
    load_factor: float = 0.85,
    code_type: str = "iata",
    model: str = "haversine",
) -> SafSavings:
    if not 0 <= saf_percentage <= 100:
        raise ValueError("saf_percentage must be between 0 and 100.")

    base = calculate_flight_emissions(
        from_code,
        to_code,
        aircraft_type=aircraft_type,
        fuel_type=FuelType.JET_A1,
        load_factor=load_factor,
        code_type=code_type,
        model=model,
    )

    saf_multiplier = 1.0 - 0.7 * (saf_percentage / 100.0)
    saf_co2 = base.total_co2_kg * saf_multiplier
    reduction = base.total_co2_kg - saf_co2
    reduction_pct = (reduction / base.total_co2_kg) * 100 if base.total_co2_kg else 0.0

    return SafSavings(
        base_co2_kg=base.total_co2_kg,
        saf_co2_kg=saf_co2,
        co2_reduction_kg=reduction,
        reduction_percentage=reduction_pct,
    )
