from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..core.loader import get_airport_by_iata, get_airport_by_icao
from ..models.airport import Airport
from ..utils.logging import get_logger

logger = get_logger()


try:
    from timezonefinder import TimezoneFinder

    _tz_finder = TimezoneFinder()
    HAS_TIMEZONEFINDER = True
except ImportError:
    _tz_finder = None
    HAS_TIMEZONEFINDER = False
    logger.warning("timezonefinder not installed, timezone functionality will be limited")


def get_timezone_for_airport(airport: Airport) -> Optional[str]:
    if not HAS_TIMEZONEFINDER:
        return None

    try:
        tz_name = _tz_finder.timezone_at(lat=airport.latitude_deg, lng=airport.longitude_deg)
        return tz_name
    except Exception as e:
        logger.debug(f"Could not determine timezone for {airport.name}: {e}")
        return None


def _approx_timezone_offset(lon: float) -> float:
    return lon / 15.0


def get_timezone_offset(
    airport: Airport,
    dt_utc: Optional[datetime] = None,
) -> Optional[float]:
    tz_name = get_timezone_for_airport(airport)

    if tz_name is None:
        return _approx_timezone_offset(airport.longitude_deg)

    if dt_utc is None:
        dt_utc = datetime.now(ZoneInfo("UTC"))

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))

    try:
        tz = ZoneInfo(tz_name)
        offset = tz.utcoffset(dt_utc)
        if offset is None:
            return None
        return offset.total_seconds() / 3600.0
    except ZoneInfoNotFoundError:
        logger.debug(f"Timezone {tz_name} not found")
        return None
    except Exception as e:
        logger.debug(f"Error computing timezone offset: {e}")
        return None


def get_timezone_for_code(code: str, code_type: str = "iata") -> Optional[str]:
    if code_type == "iata":
        airport = get_airport_by_iata(code)
    elif code_type == "icao":
        airport = get_airport_by_icao(code)
    else:
        airport = get_airport_by_iata(code) or get_airport_by_icao(code)

    if airport is None:
        return None

    return get_timezone_for_airport(airport)


def local_time_for_airport(
    airport: Airport, dt_utc: Optional[datetime] = None
) -> Optional[datetime]:
    tz_name = get_timezone_for_airport(airport)

    if tz_name is None:
        return None

    if dt_utc is None:
        dt_utc = datetime.now(ZoneInfo("UTC"))

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))

    try:
        tz = ZoneInfo(tz_name)
        local_dt = dt_utc.astimezone(tz)
        return local_dt
    except ZoneInfoNotFoundError:
        logger.debug(f"Timezone {tz_name} not found")
        return None
    except Exception as e:
        logger.debug(f"Error converting to local time: {e}")
        return None


def local_time_for_code(
    code: str, code_type: str = "iata", dt_utc: Optional[datetime] = None
) -> Optional[datetime]:
    if code_type == "iata":
        airport = get_airport_by_iata(code)
    elif code_type == "icao":
        airport = get_airport_by_icao(code)
    else:
        airport = get_airport_by_iata(code) or get_airport_by_icao(code)

    if airport is None:
        return None

    return local_time_for_airport(airport, dt_utc)
