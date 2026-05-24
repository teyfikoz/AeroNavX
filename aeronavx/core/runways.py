"""Runway loading and management for AeroNavX."""

import csv
from pathlib import Path
from typing import Optional, Union

from ..exceptions import DataLoadError
from ..models.runway import Runway
from ..utils.logging import get_logger

logger = get_logger()

_runways: list[Runway] = []
_airport_index: dict[str, list[Runway]] = {}  # airport_ident -> runways
_loaded = False


def _find_runway_file() -> Path:
    """Find the runways CSV file."""
    possible_paths = [
        Path(__file__).parent.parent / "data" / "runways.csv",
        Path(__file__).parent.parent.parent / "data" / "ourairports_runways.csv",
        Path.cwd() / "data" / "runways.csv",
        Path.cwd() / "data" / "ourairports_runways.csv",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    raise DataLoadError(
        f"Could not find runways.csv. Searched in: {', '.join(str(p) for p in possible_paths)}"
    )


def _parse_bool(value: str) -> Optional[bool]:
    """Parse boolean value from CSV."""
    if not value or value.lower() in ("", "no", "0", "false"):
        return False
    if value.lower() in ("yes", "1", "true"):
        return True
    return None


def _parse_int(value: str) -> Optional[int]:
    """Parse integer value from CSV."""
    try:
        return int(value) if value else None
    except ValueError:
        return None


def _parse_float(value: str) -> Optional[float]:
    """Parse float value from CSV."""
    try:
        return float(value) if value else None
    except ValueError:
        return None


def load_runways(
    data_path: Optional[Union[Path, str]] = None,
    force_reload: bool = False,
) -> list[Runway]:
    """
    Load runways from CSV file.

    Args:
        data_path: Path to runways CSV file (default: auto-detect)
        force_reload: Force reload even if already loaded

    Returns:
        List of Runway objects

    Example:
        >>> runways = load_runways()
        >>> print(f"Loaded {len(runways):,} runways")
        Loaded 47,373 runways
    """
    global _runways, _airport_index, _loaded

    if _loaded and not force_reload:
        return _runways

    if data_path is None:
        data_path = _find_runway_file()
    else:
        data_path = Path(data_path)
        if not data_path.exists():
            raise DataLoadError(f"Runway file not found: {data_path}")

    logger.info(f"Loading runways from {data_path}")

    runways = []
    skipped = 0

    try:
        with open(data_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    airport_ident = row.get("airport_ident", "").strip()
                    if not airport_ident:
                        skipped += 1
                        continue

                    runway = Runway(
                        id=_parse_int(row.get("id", "")) or 0,
                        airport_ref=_parse_int(row.get("airport_ref", "")) or 0,
                        airport_ident=airport_ident,
                        length_ft=_parse_float(row.get("length_ft", "")),
                        width_ft=_parse_float(row.get("width_ft", "")),
                        surface=row.get("surface", "").strip() or None,
                        lighted=_parse_bool(row.get("lighted", "")),
                        closed=_parse_bool(row.get("closed", "")),
                        le_ident=row.get("le_ident", "").strip() or None,
                        le_latitude_deg=_parse_float(row.get("le_latitude_deg", "")),
                        le_longitude_deg=_parse_float(row.get("le_longitude_deg", "")),
                        le_elevation_ft=_parse_float(row.get("le_elevation_ft", "")),
                        le_heading_degT=_parse_float(row.get("le_heading_degT", "")),
                        le_displaced_threshold_ft=_parse_float(
                            row.get("le_displaced_threshold_ft", "")
                        ),
                        he_ident=row.get("he_ident", "").strip() or None,
                        he_latitude_deg=_parse_float(row.get("he_latitude_deg", "")),
                        he_longitude_deg=_parse_float(row.get("he_longitude_deg", "")),
                        he_elevation_ft=_parse_float(row.get("he_elevation_ft", "")),
                        he_heading_degT=_parse_float(row.get("he_heading_degT", "")),
                        he_displaced_threshold_ft=_parse_float(
                            row.get("he_displaced_threshold_ft", "")
                        ),
                    )

                    runways.append(runway)

                except Exception as e:
                    logger.debug(f"Skipping runway due to error: {e}")
                    skipped += 1
                    continue

    except Exception as e:
        raise DataLoadError(f"Failed to load runways: {e}")

    _runways = runways
    _build_indices()
    _loaded = True

    logger.info(f"Loaded {len(_runways):,} runways (skipped {skipped})")

    return _runways


def _build_indices() -> None:
    """Build indices for fast runway lookups."""
    global _airport_index

    _airport_index.clear()

    for runway in _runways:
        if runway.airport_ident not in _airport_index:
            _airport_index[runway.airport_ident] = []
        _airport_index[runway.airport_ident].append(runway)


def get_runways_by_airport(airport_ident: str) -> list[Runway]:
    """
    Get all runways for a specific airport.

    Args:
        airport_ident: Airport identifier (IATA, ICAO, or ident code)

    Returns:
        List of Runway objects for the airport

    Example:
        >>> runways = get_runways_by_airport("KJFK")
        >>> for rwy in runways:
        ...     print(f"{rwy.designation}: {rwy.length_ft:.0f}ft")
        04L/22R: 14511ft
        04R/22L: 11351ft
        13L/31R: 10000ft
        13R/31L: 12079ft
    """
    if not _loaded:
        load_runways()

    # Try exact match first
    if airport_ident in _airport_index:
        return _airport_index[airport_ident]

    # Try uppercase
    airport_ident_upper = airport_ident.upper()
    if airport_ident_upper in _airport_index:
        return _airport_index[airport_ident_upper]

    return []


def get_longest_runway(airport_ident: str) -> Optional[Runway]:
    """
    Get the longest runway for an airport.

    Args:
        airport_ident: Airport identifier

    Returns:
        Longest Runway object, or None if no runways found

    Example:
        >>> runway = get_longest_runway("KJFK")
        >>> print(f"{runway.designation}: {runway.length_ft:.0f}ft")
        04L/22R: 14511ft
    """
    runways = get_runways_by_airport(airport_ident)
    if not runways:
        return None

    return max(
        (r for r in runways if r.length_ft is not None),
        key=lambda r: r.length_ft or 0,
        default=None,
    )


def get_paved_runways(airport_ident: str) -> list[Runway]:
    """
    Get all paved runways for an airport.

    Args:
        airport_ident: Airport identifier

    Returns:
        List of paved Runway objects

    Example:
        >>> runways = get_paved_runways("KJFK")
        >>> print(f"{len(runways)} paved runways")
        4 paved runways
    """
    runways = get_runways_by_airport(airport_ident)
    return [r for r in runways if r.is_paved]


def clear_cache() -> None:
    """Clear runway data cache."""
    global _runways, _airport_index, _loaded

    _runways.clear()
    _airport_index.clear()
    _loaded = False

    logger.info("Cleared runway data cache")
