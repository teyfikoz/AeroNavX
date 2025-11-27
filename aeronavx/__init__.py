from .models import Airport
from .core.airports import get as get_airport, get_by_iata, get_by_icao, search_by_name as search_airports_by_name
from .core.distance import distance, distance_km, distance_mi, distance_nmi
from .core.geodesy import initial_bearing, midpoint, great_circle_path
from .core.search import nearest_airports as nearest_airport, airports_within_radius
from .core.routing import estimate_flight_time_hours as estimate_flight_time, route_distance
from .core.emissions import estimate_co2_kg_by_codes as estimate_co2_kg_for_segment
from .core.weather import get_metar, get_taf
from .exceptions import (
    AeroNavXError,
    AirportNotFoundError,
    InvalidAirportCodeError,
    DataLoadError,
    RoutingError,
    WeatherDataError,
)


__version__ = "0.1.0"

__all__ = [
    "Airport",
    "get_airport",
    "get_by_iata",
    "get_by_icao",
    "distance",
    "distance_km",
    "distance_mi",
    "distance_nmi",
    "initial_bearing",
    "midpoint",
    "great_circle_path",
    "nearest_airport",
    "airports_within_radius",
    "estimate_flight_time",
    "route_distance",
    "estimate_co2_kg_for_segment",
    "search_airports_by_name",
    "get_metar",
    "get_taf",
    "AeroNavXError",
    "AirportNotFoundError",
    "InvalidAirportCodeError",
    "DataLoadError",
    "RoutingError",
    "WeatherDataError",
]
