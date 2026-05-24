from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

TEXT_VERSION = "v1"


def sanitize_model_id(model_id: str) -> str:
    return model_id.replace("/", "__").replace(":", "_")


def _get_field(obj: Any, names: Iterable[str]) -> Any:
    if isinstance(obj, Mapping):
        for name in names:
            if name in obj and obj[name] not in (None, ""):
                return obj[name]
        return None

    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return value
    return None


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def airport_to_text(airport: Any) -> str:
    parts = [
        _as_text(_get_field(airport, ["name"])),
        _as_text(_get_field(airport, ["municipality", "city"])),
        _as_text(_get_field(airport, ["iso_country", "country"])),
        _as_text(_get_field(airport, ["iso_region", "region"])),
        _as_text(_get_field(airport, ["iata_code", "iata"])),
        _as_text(_get_field(airport, ["gps_code", "icao_code", "icao"])),
        _as_text(_get_field(airport, ["ident"])),
        _as_text(_get_field(airport, ["local_code"])),
        _as_text(_get_field(airport, ["keywords"])),
    ]
    return " ".join(part for part in parts if part)


def airport_to_record(airport: Any) -> dict[str, Any]:
    return {
        "id": _get_field(airport, ["id"]),
        "ident": _get_field(airport, ["ident"]),
        "name": _get_field(airport, ["name"]),
        "iata": _get_field(airport, ["iata_code", "iata"]),
        "icao": _get_field(airport, ["gps_code", "icao_code", "icao"]),
        "country": _get_field(airport, ["iso_country", "country"]),
        "region": _get_field(airport, ["iso_region", "region"]),
        "municipality": _get_field(airport, ["municipality", "city"]),
        "latitude": _get_field(airport, ["latitude_deg", "lat", "latitude"]),
        "longitude": _get_field(airport, ["longitude_deg", "lon", "longitude"]),
        "type": _get_field(airport, ["type"]),
    }


def coerce_airports(airports: Any) -> list[Any]:
    if airports is None:
        return []

    if hasattr(airports, "iterrows"):
        return [row for _, row in airports.iterrows()]

    if isinstance(airports, Mapping):
        return [airports]

    if isinstance(airports, (str, bytes)):
        return [airports]

    if isinstance(airports, Iterable):
        return list(airports)

    return [airports]


def try_import_pandas():
    try:
        import pandas as pd
    except ImportError:
        return None
    return pd
