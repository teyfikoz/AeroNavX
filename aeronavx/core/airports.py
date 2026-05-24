from typing import Literal, Optional

from ..core.loader import (
    get_airport_by_iata,
    get_airport_by_icao,
)
from ..core.loader import (
    get_all_airports as loader_get_all,
)
from ..core.search import (
    airports_within_radius as nearby_impl,
)
from ..core.search import (
    search_airports_by_name as search_by_name_impl,
)
from ..models.airport import Airport

CodeType = Literal["iata", "icao", "auto"]


def get(code: str, code_type: CodeType = "auto") -> Optional[Airport]:
    if code_type == "iata":
        return get_airport_by_iata(code)
    elif code_type == "icao":
        return get_airport_by_icao(code)
    elif code_type == "auto":
        airport = get_airport_by_iata(code)
        if airport is None:
            airport = get_airport_by_icao(code)
        return airport
    else:
        raise ValueError(f"Invalid code_type: {code_type}. Must be 'iata', 'icao', or 'auto'")


def get_by_iata(code: str) -> Optional[Airport]:
    return get_airport_by_iata(code)


def get_by_icao(code: str) -> Optional[Airport]:
    return get_airport_by_icao(code)


def all() -> list[Airport]:
    return loader_get_all()


def search_by_name(name: str, limit: int = 20) -> list[Airport]:
    return search_by_name_impl(name, limit)


def nearby(lat: float, lon: float, radius_km: float) -> list[Airport]:
    return nearby_impl(lat, lon, radius_km)
