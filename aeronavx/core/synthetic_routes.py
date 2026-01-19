from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Union

from ..exceptions import RoutingError
from ..models.airport import Airport
from ..core.airports import get as get_airport
from ..core.distance import distance
from ..core.geodesy import great_circle_path
from ..utils.constants import DEFAULT_CRUISE_SPEED_KTS


@dataclass(frozen=True)
class Waypoint:
    name: str
    latitude: float
    longitude: float
    distance_from_origin_km: float


@dataclass(frozen=True)
class SyntheticRoute:
    origin: Airport
    destination: Airport
    waypoints: list[Waypoint]
    total_distance_km: float
    total_time_hours: float


def _resolve_airport(value: Union[str, Airport]) -> Airport:
    if isinstance(value, Airport):
        return value

    airport = get_airport(value, code_type="auto")
    if airport is None:
        raise RoutingError(f"Airport not found: {value}")
    return airport


def generate_route(
    origin: Union[str, Airport],
    destination: Union[str, Airport],
    num_waypoints: int = 12,
    model: str = "haversine",
    speed_kts: float = DEFAULT_CRUISE_SPEED_KTS,
) -> SyntheticRoute:
    if num_waypoints < 0:
        raise ValueError("num_waypoints must be >= 0")

    origin_airport = _resolve_airport(origin)
    destination_airport = _resolve_airport(destination)

    num_points = max(num_waypoints + 2, 2)
    path_points = great_circle_path(
        origin_airport.latitude_deg,
        origin_airport.longitude_deg,
        destination_airport.latitude_deg,
        destination_airport.longitude_deg,
        num_points=num_points,
    )

    waypoints: list[Waypoint] = []
    for idx, (lat, lon) in enumerate(path_points[1:-1], start=1):
        dist_km = distance(
            origin_airport.latitude_deg,
            origin_airport.longitude_deg,
            lat,
            lon,
            model=model,
            unit="km",
        )
        waypoints.append(
            Waypoint(
                name=f"WP{idx}",
                latitude=lat,
                longitude=lon,
                distance_from_origin_km=dist_km,
            )
        )

    total_distance_km = 0.0
    for start, end in zip(path_points[:-1], path_points[1:]):
        total_distance_km += distance(
            start[0],
            start[1],
            end[0],
            end[1],
            model=model,
            unit="km",
        )

    speed_kmh = speed_kts * 1.852
    total_time_hours = total_distance_km / speed_kmh if speed_kmh > 0 else 0.0

    return SyntheticRoute(
        origin=origin_airport,
        destination=destination_airport,
        waypoints=waypoints,
        total_distance_km=total_distance_km,
        total_time_hours=total_time_hours,
    )


def generate_route_by_codes(
    codes: Sequence[str],
    model: str = "haversine",
    speed_kts: float = DEFAULT_CRUISE_SPEED_KTS,
) -> SyntheticRoute:
    if len(codes) < 2:
        raise RoutingError("At least two airport codes are required.")

    origin = _resolve_airport(codes[0])
    destination = _resolve_airport(codes[-1])

    return generate_route(origin, destination, model=model, speed_kts=speed_kts)
