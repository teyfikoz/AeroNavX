from .core.airports import get as get_airport
from .core.airports import get_by_iata, get_by_icao
from .core.airports import search_by_name as search_airports_by_name
from .core.distance import distance, distance_km, distance_mi, distance_nmi
from .core.emissions import estimate_co2_kg_by_codes as estimate_co2_kg_for_segment
from .core.emissions_advanced import (
    AircraftType,
    EmissionsResult,
    FuelType,
    SafSavings,
    calculate_flight_emissions,
    compare_saf_savings,
)
from .core.geodesy import great_circle_path, initial_bearing, midpoint
from .core.network_intelligence import (
    HubScore,
    NetworkIntelligence,
    hub_intelligence_score,
    identify_global_hubs,
)
from .core.passenger_experience import (
    JetLagResult,
    JetLagSeverity,
    TravelDirection,
    calculate_jet_lag,
)
from .core.routing import estimate_flight_time_hours as estimate_flight_time
from .core.routing import route_distance
from .core.runways import (
    get_longest_runway,
    get_paved_runways,
    get_runways_by_airport,
)
from .core.search import airports_within_radius, nearest_airport, nearest_airports
from .core.statistics import (
    get_continent_stats,
    get_country_stats,
    get_global_stats,
    get_top_countries_by_airports,
    get_top_countries_by_large_airports,
)
from .core.synthetic_routes import (
    SyntheticRoute,
    Waypoint,
    generate_route,
    generate_route_by_codes,
)
from .core.timezone import get_timezone_offset
from .core.weather import get_metar, get_taf
from .exceptions import (
    AeroNavXError,
    AirportNotFoundError,
    DataLoadError,
    InvalidAirportCodeError,
    RoutingError,
    WeatherDataError,
)
from .models import Airport, Runway

_semantic_engine = None


def semantic_search(query: str, top_k: int = 5, return_format: str = "auto"):
    global _semantic_engine

    if _semantic_engine is None:
        try:
            from .hf.semantic_search import SemanticAirportSearch
        except ImportError as exc:
            raise ImportError(
                "Semantic search requires the HF extra. Install with " "`pip install aeronavx[hf]`."
            ) from exc

        from .core.loader import get_all_airports

        airports = get_all_airports()
        _semantic_engine = SemanticAirportSearch(airports)

    return _semantic_engine.search(query, top_k=top_k, return_format=return_format)


def clear_semantic_search_cache() -> None:
    global _semantic_engine
    _semantic_engine = None


__version__ = "3.1.0"

__all__ = [
    "Airport",
    "Runway",
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
    "nearest_airports",
    "airports_within_radius",
    "estimate_flight_time",
    "route_distance",
    "estimate_co2_kg_for_segment",
    "calculate_flight_emissions",
    "compare_saf_savings",
    "AircraftType",
    "FuelType",
    "EmissionsResult",
    "SafSavings",
    "calculate_jet_lag",
    "JetLagResult",
    "JetLagSeverity",
    "TravelDirection",
    "NetworkIntelligence",
    "identify_global_hubs",
    "hub_intelligence_score",
    "HubScore",
    "generate_route",
    "generate_route_by_codes",
    "SyntheticRoute",
    "Waypoint",
    "search_airports_by_name",
    "get_metar",
    "get_taf",
    "get_timezone_offset",
    "get_runways_by_airport",
    "get_longest_runway",
    "get_paved_runways",
    "get_country_stats",
    "get_continent_stats",
    "get_global_stats",
    "get_top_countries_by_airports",
    "get_top_countries_by_large_airports",
    "semantic_search",
    "clear_semantic_search_cache",
    "AeroNavXError",
    "AirportNotFoundError",
    "InvalidAirportCodeError",
    "DataLoadError",
    "RoutingError",
    "WeatherDataError",
]
