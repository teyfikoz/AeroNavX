from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class Airport:
    id: Optional[int]
    ident: Optional[str]
    type: Optional[str]
    name: str
    latitude_deg: float
    longitude_deg: float
    elevation_ft: Optional[float]
    continent: Optional[str]
    iso_country: Optional[str]
    iso_region: Optional[str]
    municipality: Optional[str]
    scheduled_service: Optional[bool]
    gps_code: Optional[str]
    iata_code: Optional[str]
    local_code: Optional[str]
    home_link: Optional[str]
    wikipedia_link: Optional[str]
    keywords: Optional[str]

    def coords(self) -> tuple[float, float]:
        return (self.latitude_deg, self.longitude_deg)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def distance_to(self, other: "Airport", model: str = "haversine") -> float:
        from ..core.distance import distance as calc_distance

        return calc_distance(
            self.latitude_deg,
            self.longitude_deg,
            other.latitude_deg,
            other.longitude_deg,
            model=model,
            unit="km",
        )

    def bearing_to(self, other: "Airport") -> float:
        from ..core.geodesy import initial_bearing

        return initial_bearing(
            self.latitude_deg, self.longitude_deg, other.latitude_deg, other.longitude_deg
        )

    def __str__(self) -> str:
        codes = []
        if self.iata_code:
            codes.append(f"IATA:{self.iata_code}")
        if self.gps_code:
            codes.append(f"ICAO:{self.gps_code}")

        code_str = f" ({', '.join(codes)})" if codes else ""
        return f"{self.name}{code_str}"

    def __repr__(self) -> str:
        return f"Airport(name='{self.name}', iata='{self.iata_code}', icao='{self.gps_code}')"
