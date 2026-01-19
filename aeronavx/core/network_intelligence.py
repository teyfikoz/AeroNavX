from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Optional

from ..core.airports import get as get_airport
from ..core.loader import get_all_airports
from ..models.airport import Airport
from ..utils.spatial_index import build_spatial_index


@dataclass(frozen=True)
class HubScore:
    airport: Airport
    hub_score: float
    connectivity_score: float
    type_score: float


def _airport_type_score(airport: Airport) -> float:
    if airport.type == "large_airport":
        return 1.0
    if airport.type == "medium_airport":
        return 0.6
    if airport.type == "small_airport":
        return 0.3
    return 0.1


class NetworkIntelligence:
    def __init__(
        self,
        airports: Optional[Sequence[Airport]] = None,
        radius_km: float = 500.0,
        max_neighbors: int = 100,
    ) -> None:
        if airports is None:
            airports = get_all_airports()
        self.airports = list(airports)
        self.radius_km = radius_km
        self.max_neighbors = max_neighbors
        self._index = build_spatial_index(self.airports)

    def _connectivity_score(self, airport: Airport) -> float:
        neighbors = self._index.within_radius(
            airport.latitude_deg,
            airport.longitude_deg,
            self.radius_km,
        )
        count = max(len(neighbors) - 1, 0)
        normalized = min(count / float(self.max_neighbors), 1.0)
        return normalized

    def score_airport(self, airport: Airport) -> HubScore:
        type_score = _airport_type_score(airport)
        connectivity_score = self._connectivity_score(airport)
        hub_score = (0.6 * connectivity_score) + (0.4 * type_score)
        if airport.scheduled_service:
            hub_score = min(hub_score + 0.05, 1.0)

        return HubScore(
            airport=airport,
            hub_score=hub_score,
            connectivity_score=connectivity_score,
            type_score=type_score,
        )

    def rank_airports(self, airports: Optional[Iterable[Airport]] = None) -> list[HubScore]:
        if airports is None:
            airports = self.airports
        scored = [self.score_airport(a) for a in airports]
        return sorted(scored, key=lambda s: s.hub_score, reverse=True)


def identify_global_hubs(
    top_n: int = 10,
    airports: Optional[Sequence[Airport]] = None,
    scheduled_service_only: bool = True,
) -> list[HubScore]:
    if airports is None:
        airports = get_all_airports()

    filtered = [
        a
        for a in airports
        if a.type in ("large_airport", "medium_airport")
        and (a.scheduled_service or not scheduled_service_only)
    ]

    intelligence = NetworkIntelligence(filtered)
    return intelligence.rank_airports(filtered)[:top_n]


def hub_intelligence_score(code: str) -> HubScore:
    airport = get_airport(code, code_type="auto")
    if airport is None:
        raise ValueError(f"Airport not found: {code}")

    intelligence = NetworkIntelligence()
    return intelligence.score_airport(airport)
