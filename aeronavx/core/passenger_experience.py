from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from ..core.airports import get as get_airport
from ..core.timezone import get_timezone_offset
from ..exceptions import AirportNotFoundError
from ..models.airport import Airport


class TravelDirection(Enum):
    EASTWARD = "eastward"
    WESTWARD = "westward"
    NONE = "none"


class JetLagSeverity(Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass(frozen=True)
class JetLagResult:
    timezone_difference_hours: float
    direction: TravelDirection
    severity: JetLagSeverity
    estimated_recovery_days: float


def _direction(diff_hours: float) -> TravelDirection:
    if diff_hours > 0:
        return TravelDirection.EASTWARD
    if diff_hours < 0:
        return TravelDirection.WESTWARD
    return TravelDirection.NONE


def _severity(diff_hours: float) -> JetLagSeverity:
    abs_diff = abs(diff_hours)
    if abs_diff <= 2:
        return JetLagSeverity.MILD
    if abs_diff <= 5:
        return JetLagSeverity.MODERATE
    return JetLagSeverity.SEVERE


def _recovery_days(diff_hours: float, age: int) -> float:
    base_days = abs(diff_hours) / 2.0
    if age >= 50:
        base_days *= 1.2
    elif age <= 18:
        base_days *= 0.8
    return max(base_days, 0.0)


def _resolve_airport(value: Union[Airport, str], label: str) -> Airport:
    if isinstance(value, Airport):
        return value
    if isinstance(value, str):
        airport = get_airport(value, code_type="auto")
        if airport is None:
            raise AirportNotFoundError(f"{label} airport not found: {value}")
        return airport
    raise TypeError(f"{label} must be an Airport instance or airport code string.")


def calculate_jet_lag(
    origin: Union[Airport, str],
    destination: Union[Airport, str],
    age: int = 30,
    origin_offset: Optional[float] = None,
    destination_offset: Optional[float] = None,
) -> JetLagResult:
    if age <= 0:
        raise ValueError("age must be positive")

    origin_airport = _resolve_airport(origin, "origin")
    destination_airport = _resolve_airport(destination, "destination")

    if origin_offset is None:
        origin_offset = get_timezone_offset(origin_airport)
    if destination_offset is None:
        destination_offset = get_timezone_offset(destination_airport)

    if origin_offset is None or destination_offset is None:
        raise ValueError("Could not determine timezone offsets for jet lag calculation.")

    diff_hours = destination_offset - origin_offset
    direction = _direction(diff_hours)
    severity = _severity(diff_hours)
    recovery = _recovery_days(diff_hours, age)

    return JetLagResult(
        timezone_difference_hours=diff_hours,
        direction=direction,
        severity=severity,
        estimated_recovery_days=recovery,
    )
