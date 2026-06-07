"""Coverage boost tests for aeronavx: analytics, emissions, runways, search, statistics, units."""
import pytest

# ── Airport model helpers ─────────────────────────────────────────────────────

def _make_airport(iata="IST", name="Istanbul Airport", lat=41.275, lon=28.752,
                   icao="LTFM", country="TR", region="TR-34", municipality="Istanbul",
                   elev=163.0, scheduled=True, airport_type="large_airport", ident="LTFM"):
    from aeronavx.models.airport import Airport
    return Airport(
        id=1, ident=ident, type=airport_type, name=name,
        latitude_deg=lat, longitude_deg=lon, elevation_ft=elev,
        continent="EU", iso_country=country, iso_region=region,
        municipality=municipality, scheduled_service=scheduled,
        gps_code=icao, iata_code=iata, local_code=iata,
        home_link=None, wikipedia_link=None, keywords=None,
    )


# ── models/airport.py ─────────────────────────────────────────────────────────

def test_airport_coords():
    ap = _make_airport()
    assert ap.coords() == (41.275, 28.752)


def test_airport_as_dict():
    ap = _make_airport()
    d = ap.as_dict()
    assert isinstance(d, dict)
    assert d["iata_code"] == "IST"


def test_airport_distance_to():
    ap1 = _make_airport(iata="IST", lat=41.275, lon=28.752)
    ap2 = _make_airport(iata="LHR", lat=51.477, lon=-0.461)
    dist = ap1.distance_to(ap2)
    assert 2000 < dist < 3000  # ~2500 km


def test_airport_bearing_to():
    ap1 = _make_airport(iata="IST", lat=41.275, lon=28.752)
    ap2 = _make_airport(iata="LHR", lat=51.477, lon=-0.461)
    bearing = ap1.bearing_to(ap2)
    assert 0 <= bearing <= 360


def test_airport_str_with_codes():
    ap = _make_airport(iata="IST", icao="LTFM")
    s = str(ap)
    assert "IST" in s


def test_airport_str_no_iata():
    from aeronavx.models.airport import Airport
    ap = Airport(id=1, ident="XYZ", type="small_airport", name="Small Airport",
                 latitude_deg=10.0, longitude_deg=20.0, elevation_ft=100.0,
                 continent="AF", iso_country="ZZ", iso_region="ZZ-01",
                 municipality="Smalltown", scheduled_service=False,
                 gps_code="LXYZ", iata_code=None, local_code=None,
                 home_link=None, wikipedia_link=None, keywords=None)
    s = str(ap)
    assert "Small Airport" in s


# ── utils/units.py ────────────────────────────────────────────────────────────

def test_km_to_mi():
    from aeronavx.utils.units import km_to_mi
    assert abs(km_to_mi(1.0) - 0.6214) < 0.001


def test_km_to_nmi():
    from aeronavx.utils.units import km_to_nmi
    assert abs(km_to_nmi(1.0) - 0.5400) < 0.01


def test_km_to_m():
    from aeronavx.utils.units import km_to_m
    assert km_to_m(1.0) == 1000.0


def test_mi_to_km():
    from aeronavx.utils.units import mi_to_km
    assert abs(mi_to_km(1.0) - 1.6093) < 0.001


def test_nmi_to_km():
    from aeronavx.utils.units import nmi_to_km
    assert abs(nmi_to_km(1.0) - 1.852) < 0.01


def test_m_to_km():
    from aeronavx.utils.units import m_to_km
    assert m_to_km(1000.0) == 1.0


def test_ft_to_m():
    from aeronavx.utils.units import ft_to_m
    assert abs(ft_to_m(3.281) - 1.0) < 0.01


def test_m_to_ft():
    from aeronavx.utils.units import m_to_ft
    assert abs(m_to_ft(1.0) - 3.28084) < 0.001


def test_convert_distance_same_unit():
    from aeronavx.utils.units import convert_distance
    assert convert_distance(100.0, "km", "km") == 100.0


def test_convert_distance_km_to_mi():
    from aeronavx.utils.units import convert_distance
    result = convert_distance(100.0, "km", "mi")
    assert abs(result - 62.137) < 1.0


def test_convert_distance_mi_to_km():
    from aeronavx.utils.units import convert_distance
    result = convert_distance(100.0, "mi", "km")
    assert abs(result - 160.934) < 1.0


def test_convert_distance_nmi_to_km():
    from aeronavx.utils.units import convert_distance
    result = convert_distance(100.0, "nmi", "km")
    assert abs(result - 185.2) < 1.0


def test_convert_distance_km_to_nmi():
    from aeronavx.utils.units import convert_distance
    result = convert_distance(185.2, "km", "nmi")
    assert abs(result - 100.0) < 1.0


def test_convert_distance_m_to_km():
    from aeronavx.utils.units import convert_distance
    result = convert_distance(1000.0, "m", "km")
    assert result == 1.0


def test_convert_distance_km_to_m():
    from aeronavx.utils.units import convert_distance
    result = convert_distance(1.0, "km", "m")
    assert result == 1000.0


def test_convert_elevation_ft_to_m():
    from aeronavx.utils.units import convert_elevation
    result = convert_elevation(3281.0, "ft", "m")
    assert abs(result - 1000.0) < 10.0


def test_convert_elevation_m_to_ft():
    from aeronavx.utils.units import convert_elevation
    result = convert_elevation(1000.0, "m", "ft")
    assert abs(result - 3280.84) < 10.0


def test_convert_elevation_same_unit():
    from aeronavx.utils.units import convert_elevation
    assert convert_elevation(100.0, "ft", "ft") == 100.0


# ── core/analytics.py ────────────────────────────────────────────────────────

def test_airports_per_country():
    from aeronavx.core.analytics import airports_per_country
    result = airports_per_country()
    assert isinstance(result, dict)
    assert len(result) > 0
    assert "US" in result


def test_airports_per_continent():
    from aeronavx.core.analytics import airports_per_continent
    result = airports_per_continent()
    assert isinstance(result, dict)
    assert len(result) > 0


def test_airports_per_type():
    from aeronavx.core.analytics import airports_per_type
    result = airports_per_type()
    assert isinstance(result, dict)
    assert "large_airport" in result


def test_highest_elevation_airports():
    from aeronavx.core.analytics import highest_elevation_airports
    result = highest_elevation_airports(5)
    assert len(result) <= 5
    assert all(a.elevation_ft is not None for a in result)
    if len(result) > 1:
        assert result[0].elevation_ft >= result[-1].elevation_ft


def test_lowest_elevation_airports():
    from aeronavx.core.analytics import lowest_elevation_airports
    result = lowest_elevation_airports(5)
    assert len(result) <= 5
    assert all(a.elevation_ft is not None for a in result)


def test_country_centroids():
    from aeronavx.core.analytics import country_centroids
    result = country_centroids()
    assert isinstance(result, dict)
    assert "US" in result
    lat, lon = result["US"]
    assert -90 <= lat <= 90
    assert -180 <= lon <= 180


def test_total_airports():
    from aeronavx.core.analytics import total_airports
    count = total_airports()
    assert count > 0


def test_airports_with_scheduled_service():
    from aeronavx.core.analytics import airports_with_scheduled_service
    count = airports_with_scheduled_service()
    assert count > 0


def test_airports_by_type_and_country():
    from aeronavx.core.analytics import airports_by_type_and_country
    result = airports_by_type_and_country()
    assert isinstance(result, dict)
    assert "large_airport" in result


def test_get_precomputed_neighbors_none():
    from aeronavx.core.analytics import get_precomputed_neighbors
    # Not precomputed → None
    result = get_precomputed_neighbors("IST")
    assert result is None or isinstance(result, list)


# ── core/emissions.py ────────────────────────────────────────────────────────

def test_estimate_co2_segment():
    from aeronavx.core.emissions import estimate_co2_kg_for_segment
    ap1 = _make_airport(iata="IST", lat=41.275, lon=28.752)
    ap2 = _make_airport(iata="LHR", lat=51.477, lon=-0.461)
    co2 = estimate_co2_kg_for_segment(ap1, ap2)
    assert co2 > 0


def test_estimate_co2_route_empty():
    from aeronavx.core.emissions import estimate_co2_kg_for_route
    assert estimate_co2_kg_for_route([]) == 0.0


def test_estimate_co2_route_single():
    from aeronavx.core.emissions import estimate_co2_kg_for_route
    ap = _make_airport()
    assert estimate_co2_kg_for_route([ap]) == 0.0


def test_estimate_co2_route_multi():
    from aeronavx.core.emissions import estimate_co2_kg_for_route
    ap1 = _make_airport(iata="IST", lat=41.275, lon=28.752)
    ap2 = _make_airport(iata="LHR", lat=51.477, lon=-0.461)
    ap3 = _make_airport(iata="JFK", lat=40.641, lon=-73.778)
    co2 = estimate_co2_kg_for_route([ap1, ap2, ap3])
    assert co2 > 0


def test_estimate_co2_by_iata_codes():
    from aeronavx.core.emissions import estimate_co2_kg_by_codes
    co2 = estimate_co2_kg_by_codes("IST", "LHR", code_type="iata")
    assert co2 > 0


def test_estimate_co2_by_icao_codes():
    from aeronavx.core.emissions import estimate_co2_kg_by_codes
    co2 = estimate_co2_kg_by_codes("LTFM", "EGLL", code_type="icao")
    assert co2 > 0


def test_estimate_co2_by_auto_codes():
    from aeronavx.core.emissions import estimate_co2_kg_by_codes
    co2 = estimate_co2_kg_by_codes("IST", "LHR", code_type="auto")
    assert co2 > 0


def test_estimate_co2_by_codes_invalid():
    from aeronavx.core.emissions import estimate_co2_kg_by_codes
    from aeronavx.exceptions import RoutingError
    with pytest.raises(RoutingError):
        estimate_co2_kg_by_codes("ZZZ999", "LHR")


def test_estimate_co2_route_by_codes():
    from aeronavx.core.emissions import estimate_co2_kg_route_by_codes
    co2 = estimate_co2_kg_route_by_codes(["IST", "LHR", "JFK"])
    assert co2 > 0


def test_estimate_co2_route_by_icao_codes():
    from aeronavx.core.emissions import estimate_co2_kg_route_by_codes
    co2 = estimate_co2_kg_route_by_codes(["LTFM", "EGLL"], code_type="icao")
    assert co2 > 0


def test_estimate_co2_route_by_codes_invalid():
    from aeronavx.core.emissions import estimate_co2_kg_route_by_codes
    from aeronavx.exceptions import RoutingError
    with pytest.raises(RoutingError):
        estimate_co2_kg_route_by_codes(["ZZZ999", "LHR"])


# ── core/runways.py ──────────────────────────────────────────────────────────

def test_load_runways():
    from aeronavx.core.runways import load_runways
    runways = load_runways()
    assert len(runways) > 0


def test_get_runways_by_airport():
    from aeronavx.core.runways import get_runways_by_airport
    runways = get_runways_by_airport("KJFK")
    assert isinstance(runways, list)


def test_get_runways_by_airport_lowercase():
    from aeronavx.core.runways import get_runways_by_airport
    runways = get_runways_by_airport("kjfk")
    assert isinstance(runways, list)


def test_get_runways_by_airport_not_found():
    from aeronavx.core.runways import get_runways_by_airport
    runways = get_runways_by_airport("ZZZ999NOTFOUND")
    assert runways == []


def test_get_longest_runway():
    from aeronavx.core.runways import get_longest_runway
    runway = get_longest_runway("KJFK")
    assert runway is None or runway.length_ft is not None


def test_get_longest_runway_not_found():
    from aeronavx.core.runways import get_longest_runway
    runway = get_longest_runway("ZZZ999NOTFOUND")
    assert runway is None


def test_get_paved_runways():
    from aeronavx.core.runways import get_paved_runways
    runways = get_paved_runways("KJFK")
    assert isinstance(runways, list)


def test_runways_clear_cache():
    from aeronavx.core.runways import clear_cache, load_runways
    load_runways()
    clear_cache()
    # After clearing, reload works
    runways = load_runways()
    assert len(runways) > 0


# ── core/search.py ───────────────────────────────────────────────────────────

def test_search_airports_empty_query():
    from aeronavx.core.search import search_airports_by_name
    results = search_airports_by_name("", limit=5)
    assert len(results) <= 5


def test_search_airports_by_name():
    from aeronavx.core.search import search_airports_by_name
    results = search_airports_by_name("Istanbul", limit=10)
    assert isinstance(results, list)


def test_filter_airports_by_country():
    from aeronavx.core.search import filter_airports
    results = filter_airports(country="TR")
    assert len(results) > 0
    assert all(a.iso_country == "TR" for a in results)


def test_filter_airports_by_region():
    from aeronavx.core.search import filter_airports
    results = filter_airports(region="TR-34")
    assert isinstance(results, list)


def test_filter_airports_by_municipality():
    from aeronavx.core.search import filter_airports
    results = filter_airports(municipality="Istanbul")
    assert isinstance(results, list)


def test_filter_airports_by_types():
    from aeronavx.core.search import filter_airports
    results = filter_airports(types=["large_airport"])
    assert all(a.type == "large_airport" for a in results)


def test_filter_airports_scheduled_only():
    from aeronavx.core.search import filter_airports
    results = filter_airports(scheduled_only=True)
    assert all(a.scheduled_service is True for a in results)


def test_airports_in_country():
    from aeronavx.core.search import airports_in_country
    results = airports_in_country("US")
    assert len(results) > 0


def test_airports_in_region():
    from aeronavx.core.search import airports_in_region
    results = airports_in_region("TR-34")
    assert isinstance(results, list)


def test_nearest_airports():
    from aeronavx.core.search import nearest_airports
    results = nearest_airports(41.275, 28.752, n=3)
    assert len(results) <= 3


def test_nearest_airports_with_max_distance():
    from aeronavx.core.search import nearest_airports
    results = nearest_airports(41.275, 28.752, n=5, max_distance_km=100.0)
    assert isinstance(results, list)


def test_airports_within_radius():
    from aeronavx.core.search import airports_within_radius
    results = airports_within_radius(41.275, 28.752, radius_km=50.0)
    assert isinstance(results, list)


def test_nearest_airport():
    from aeronavx.core.search import nearest_airport
    result = nearest_airport(41.275, 28.752)
    assert result is not None


def test_nearest_airport_to_point():
    from aeronavx.core.search import nearest_airport_to_point
    results = nearest_airport_to_point(41.275, 28.752, n=2)
    assert isinstance(results, list)


def test_nearest_airport_to_airport_iata():
    from aeronavx.core.search import nearest_airport_to_airport
    results = nearest_airport_to_airport("IST", n=3, code_type="iata")
    assert isinstance(results, list)


def test_nearest_airport_to_airport_icao():
    from aeronavx.core.search import nearest_airport_to_airport
    results = nearest_airport_to_airport("LTFM", n=2, code_type="icao")
    assert isinstance(results, list)


def test_nearest_airport_to_airport_auto():
    from aeronavx.core.search import nearest_airport_to_airport
    results = nearest_airport_to_airport("IST", n=2, code_type="auto")
    assert isinstance(results, list)


def test_nearest_airport_to_airport_not_found():
    from aeronavx.core.search import nearest_airport_to_airport
    results = nearest_airport_to_airport("ZZZ999NOTFOUND")
    assert results == []


def test_clear_spatial_index():
    from aeronavx.core.search import clear_spatial_index, nearest_airports
    nearest_airports(41.275, 28.752, n=1)  # build index
    clear_spatial_index()
    # Can still search after clearing
    results = nearest_airports(41.275, 28.752, n=1)
    assert isinstance(results, list)


# ── core/statistics.py ───────────────────────────────────────────────────────

def test_get_country_stats():
    from aeronavx.core.statistics import get_country_stats
    stats = get_country_stats("US")
    assert stats is not None
    assert stats.total_airports > 0
    assert stats.iso_country == "US"


def test_get_country_stats_as_dict():
    from aeronavx.core.statistics import get_country_stats
    stats = get_country_stats("TR")
    assert stats is not None
    d = stats.as_dict()
    assert isinstance(d, dict)
    assert "total_airports" in d


def test_get_country_stats_not_found():
    from aeronavx.core.statistics import get_country_stats
    stats = get_country_stats("QQ")
    assert stats is None


def test_get_continent_stats():
    from aeronavx.core.statistics import get_continent_stats
    stats = get_continent_stats("EU")
    assert stats is not None
    assert stats.total_airports > 0
    assert stats.continent == "EU"


def test_get_continent_stats_as_dict():
    from aeronavx.core.statistics import get_continent_stats
    stats = get_continent_stats("NA")
    assert stats is not None
    d = stats.as_dict()
    assert isinstance(d, dict)


def test_get_continent_stats_not_found():
    from aeronavx.core.statistics import get_continent_stats
    stats = get_continent_stats("ZZ")
    assert stats is None


def test_get_global_stats():
    from aeronavx.core.statistics import get_global_stats
    stats = get_global_stats()
    assert stats.total_airports > 0
    assert stats.total_runways > 0


def test_get_global_stats_as_dict():
    from aeronavx.core.statistics import get_global_stats
    stats = get_global_stats()
    d = stats.as_dict()
    assert isinstance(d, dict)
    assert "total_airports" in d


def test_get_top_countries_by_airports():
    from aeronavx.core.statistics import get_top_countries_by_airports
    top = get_top_countries_by_airports(5)
    assert len(top) <= 5
    assert top[0][0] == "US"


def test_get_top_countries_by_large_airports():
    from aeronavx.core.statistics import get_top_countries_by_large_airports
    top = get_top_countries_by_large_airports(5)
    assert len(top) <= 5
    assert isinstance(top[0], tuple)


# ── core/airports.py ─────────────────────────────────────────────────────────

def test_airports_get_by_iata():
    from aeronavx.core import airports
    ap = airports.get("IST", code_type="iata")
    assert ap is not None


def test_airports_get_by_icao():
    from aeronavx.core import airports
    ap = airports.get("LTFM", code_type="icao")
    assert ap is not None


def test_airports_get_auto():
    from aeronavx.core import airports
    ap = airports.get("IST", code_type="auto")
    assert ap is not None


def test_airports_get_auto_fallback_icao():
    from aeronavx.core import airports
    # ICAO code lookup via auto
    ap = airports.get("LTFM", code_type="auto")
    assert ap is not None


def test_airports_get_by_iata_func():
    from aeronavx.core.airports import get_by_iata
    ap = get_by_iata("LHR")
    assert ap is not None


def test_airports_get_by_icao_func():
    from aeronavx.core.airports import get_by_icao
    ap = get_by_icao("EGLL")
    assert ap is not None


def test_airports_all():
    from aeronavx.core.airports import all
    result = all()
    assert len(result) > 0


def test_airports_search_by_name():
    from aeronavx.core.airports import search_by_name
    result = search_by_name("London", limit=5)
    assert isinstance(result, list)


def test_airports_nearby():
    from aeronavx.core.airports import nearby
    result = nearby(51.5, -0.1, 50.0)
    assert isinstance(result, list)


# ── core/routing.py ───────────────────────────────────────────────────────────

def test_estimate_flight_time_hours():
    from aeronavx.core.routing import estimate_flight_time_hours
    ap1 = _make_airport(iata="IST", lat=41.275, lon=28.752)
    ap2 = _make_airport(iata="LHR", lat=51.477, lon=-0.461)
    hours = estimate_flight_time_hours(ap1, ap2)
    assert hours > 0


def test_estimate_flight_time_h_m():
    from aeronavx.core.routing import estimate_flight_time_h_m
    ap1 = _make_airport(iata="IST", lat=41.275, lon=28.752)
    ap2 = _make_airport(iata="LHR", lat=51.477, lon=-0.461)
    h, m = estimate_flight_time_h_m(ap1, ap2)
    assert h > 0
    assert 0 <= m < 60


def test_route_distance_by_iata():
    from aeronavx.core.routing import route_distance_by_codes
    dist = route_distance_by_codes(["IST", "LHR"])
    assert dist > 0


def test_route_distance_by_icao():
    from aeronavx.core.routing import route_distance_by_codes
    dist = route_distance_by_codes(["LTFM", "EGLL"], code_type="icao")
    assert dist > 0


def test_route_distance_by_auto():
    from aeronavx.core.routing import route_distance_by_codes
    dist = route_distance_by_codes(["IST", "LHR"], code_type="auto")
    assert dist > 0


def test_route_distance_by_codes_invalid():
    from aeronavx.core.routing import route_distance_by_codes
    from aeronavx.exceptions import RoutingError
    with pytest.raises(RoutingError):
        route_distance_by_codes(["ZZZ999", "LHR"])


# ── models/runway.py ─────────────────────────────────────────────────────────

def test_runway_designation():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK",
               le_ident="04L", he_ident="22R", length_ft=14511.0, surface="ASPH")
    assert r.designation == "04L/22R"


def test_runway_designation_no_idents():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK")
    assert r.designation == "Unknown"


def test_runway_length_m():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", length_ft=3281.0)
    assert abs(r.length_m - 1000.0) < 10.0


def test_runway_length_m_none():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK")
    assert r.length_m is None


def test_runway_width_m():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", width_ft=200.0)
    assert r.width_m is not None


def test_runway_is_operational_true():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", closed=False)
    assert r.is_operational is True


def test_runway_is_operational_closed():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", closed=True)
    assert r.is_operational is False


def test_runway_is_paved_asph():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", surface="ASPH")
    assert r.is_paved is True


def test_runway_is_paved_grass():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", surface="GRASS")
    assert r.is_paved is False


def test_runway_as_dict():
    from aeronavx.models.runway import Runway
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", length_ft=10000.0,
               le_ident="09L", he_ident="27R", surface="CONC")
    d = r.as_dict()
    assert isinstance(d, dict)
    assert d["airport_ident"] == "KJFK"


# ── utils/validators.py ──────────────────────────────────────────────────────

def test_is_valid_iata_non_str():
    from aeronavx.utils.validators import is_valid_iata
    assert is_valid_iata(123) is False


def test_is_valid_icao_non_str():
    from aeronavx.utils.validators import is_valid_icao
    assert is_valid_icao(None) is False


def test_validate_coordinates_invalid_lat_type():
    from aeronavx.utils.validators import validate_coordinates
    with pytest.raises(ValueError):
        validate_coordinates("not_a_float", 0.0)


def test_validate_coordinates_invalid_lon_type():
    from aeronavx.utils.validators import validate_coordinates
    with pytest.raises(ValueError):
        validate_coordinates(0.0, "bad")


def test_normalize_airport_code_non_str():
    from aeronavx.utils.validators import normalize_airport_code
    with pytest.raises(ValueError):
        normalize_airport_code(123)


# ── utils/logging.py ─────────────────────────────────────────────────────────

def test_set_log_level():
    import logging

    from aeronavx.utils.logging import set_log_level
    set_log_level(logging.DEBUG)
    set_log_level(logging.INFO)  # Reset


# ── utils/cache.py ────────────────────────────────────────────────────────────

def test_simple_cache():
    from aeronavx.utils.cache import simple_cache
    @simple_cache(maxsize=10)
    def my_func(x):
        return x * 2
    assert my_func(5) == 10
    assert my_func(5) == 10  # cached


def test_memoize():
    from aeronavx.utils.cache import memoize
    call_count = [0]
    @memoize
    def my_func(x, y=1):
        call_count[0] += 1
        return x + y
    assert my_func(3) == 4
    assert my_func(3) == 4  # cached
    assert call_count[0] == 1
    info = my_func.cache_info()
    assert "1" in info
    my_func.cache_clear()
    assert my_func(3) == 4  # recomputed
    assert call_count[0] == 2


# ── core/network_intelligence.py ─────────────────────────────────────────────

def test_network_intelligence_unknown_type():
    from aeronavx.core.network_intelligence import _airport_type_score
    # Lines 28: unknown type → 0.1
    ap = _make_airport(airport_type="unknown_type")
    score = _airport_type_score(ap)
    assert score == 0.1


def test_network_intelligence_init_no_airports():
    from aeronavx.core.network_intelligence import NetworkIntelligence
    # Lines 39: airports=None → loads all airports
    ni = NetworkIntelligence(airports=None, max_neighbors=10)
    assert len(ni.airports) > 0


def test_identify_global_hubs():
    from aeronavx.core.network_intelligence import identify_global_hubs
    hubs = identify_global_hubs(top_n=3)
    assert len(hubs) <= 3
    assert all(h.hub_score > 0 for h in hubs)


def test_hub_intelligence_score():
    from aeronavx.core.network_intelligence import hub_intelligence_score
    score = hub_intelligence_score("IST")
    assert score.hub_score >= 0


def test_hub_intelligence_score_not_found():
    from aeronavx.core.network_intelligence import hub_intelligence_score
    with pytest.raises(ValueError):
        hub_intelligence_score("ZZZ999NOTFOUND")


# ── core/passenger_experience.py ─────────────────────────────────────────────

def test_direction_none():
    from aeronavx.core.passenger_experience import TravelDirection, _direction
    # Line 38: diff_hours == 0 → NONE
    result = _direction(0.0)
    assert result == TravelDirection.NONE


def test_severity_mild():
    from aeronavx.core.passenger_experience import JetLagSeverity, _severity
    # Line 44: abs_diff <= 2 → MILD
    result = _severity(1.5)
    assert result == JetLagSeverity.MILD


def test_resolve_airport_from_string():
    from aeronavx.core.passenger_experience import _resolve_airport
    ap = _resolve_airport("IST", "origin")
    assert ap is not None


def test_resolve_airport_from_airport():
    from aeronavx.core.passenger_experience import _resolve_airport
    ap = _make_airport()
    result = _resolve_airport(ap, "origin")
    assert result is ap


def test_resolve_airport_not_found():
    from aeronavx.core.passenger_experience import AirportNotFoundError, _resolve_airport
    with pytest.raises(AirportNotFoundError):
        _resolve_airport("ZZZ999NOTFOUND", "origin")


# ── core/synthetic_routes.py ─────────────────────────────────────────────────

def test_synthetic_route_resolve_by_string():
    from aeronavx.core.synthetic_routes import generate_route
    # Lines 36-39: resolve from string
    route = generate_route("IST", "LHR")
    assert route is not None


def test_synthetic_route_resolve_invalid():
    from aeronavx.core.synthetic_routes import generate_route
    from aeronavx.exceptions import RoutingError
    with pytest.raises(RoutingError):
        generate_route("ZZZ999NOTFOUND", "LHR")


def test_generate_route_by_codes():
    from aeronavx.core.synthetic_routes import generate_route_by_codes
    # Lines 111-117: generate_route_by_codes
    route = generate_route_by_codes(["IST", "LHR"])
    assert route is not None


def test_generate_route_by_codes_too_few():
    from aeronavx.core.synthetic_routes import generate_route_by_codes
    from aeronavx.exceptions import RoutingError
    with pytest.raises(RoutingError):
        generate_route_by_codes(["IST"])


# ── utils/units.py ValueError cases ──────────────────────────────────────────

def test_convert_distance_invalid_from():
    from aeronavx.utils.units import convert_distance
    with pytest.raises(ValueError):
        convert_distance(100.0, "invalid_unit", "km")


def test_convert_distance_invalid_to():
    from aeronavx.utils.units import convert_distance
    with pytest.raises(ValueError):
        convert_distance(100.0, "km", "invalid_unit")


def test_convert_elevation_invalid():
    from aeronavx.utils.units import convert_elevation
    with pytest.raises(ValueError):
        convert_elevation(100.0, "ft", "invalid_unit")
# ── emissions.py destination not found ────────────────────────────────────────

def test_estimate_co2_destination_not_found():
    from aeronavx.core.emissions import estimate_co2_kg_by_codes
    from aeronavx.exceptions import RoutingError
    with pytest.raises(RoutingError):
        estimate_co2_kg_by_codes("IST", "ZZZ999NOTFOUND")


def test_estimate_co2_route_auto_codes():
    from aeronavx.core.emissions import estimate_co2_kg_route_by_codes
    # Lines 85-86: auto code type
    co2 = estimate_co2_kg_route_by_codes(["IST", "LHR"], code_type="auto")
    assert co2 > 0


# ── core/routing.py line 53 ──────────────────────────────────────────────────

def test_route_distance_empty():
    from aeronavx.core.routing import route_distance
    # Line 53: len < 2 → return 0.0
    ap = _make_airport()
    assert route_distance([ap]) == 0.0


# ── hf/utils.py ───────────────────────────────────────────────────────────────

def test_get_field_mapping():
    from aeronavx.hf.utils import _get_field
    # Lines 15-18: Mapping type
    d = {"name": "Istanbul Airport", "other": None}
    assert _get_field(d, ["name"]) == "Istanbul Airport"
    assert _get_field(d, ["missing"]) is None


def test_get_field_mapping_empty_str():
    from aeronavx.hf.utils import _get_field
    d = {"name": "", "backup": "found"}
    result = _get_field(d, ["name", "backup"])
    assert result == "found"


def test_coerce_airports_none():
    from aeronavx.hf.utils import coerce_airports
    assert coerce_airports(None) == []


def test_coerce_airports_mapping():
    from aeronavx.hf.utils import coerce_airports
    d = {"name": "test"}
    result = coerce_airports(d)
    assert result == [d]


def test_coerce_airports_string():
    from aeronavx.hf.utils import coerce_airports
    result = coerce_airports("IST")
    assert result == ["IST"]


def test_coerce_airports_non_iterable():
    from aeronavx.hf.utils import coerce_airports
    # Use an int — not iterable, not Mapping, not string
    result = coerce_airports(42)
    assert result == [42]


# ── models/runway.py line 103 ────────────────────────────────────────────────

def test_runway_is_paved_no_surface():
    from aeronavx.models.runway import Runway
    # Line 103: `if not self.surface: return False`
    r = Runway(id=1, airport_ref=1, airport_ident="KJFK", surface=None)
    assert r.is_paved is False


# ── core/passenger_experience.py ─────────────────────────────────────────────

def test_resolve_airport_type_error():
    from aeronavx.core.passenger_experience import _resolve_airport
    # Line 67: TypeError for non-string, non-Airport
    with pytest.raises(TypeError):
        _resolve_airport(12345, "origin")


def test_calculate_jet_lag_no_offsets():
    from aeronavx.core.passenger_experience import calculate_jet_lag
    # Lines 84, 86: no offsets → get_timezone_offset called
    result = calculate_jet_lag("IST", "LHR")
    assert result is not None


def test_calculate_jet_lag_tz_none(monkeypatch):
    from aeronavx.core import passenger_experience
    # Line 89: both offsets None → raises ValueError
    monkeypatch.setattr(passenger_experience, "get_timezone_offset", lambda a: None)
    from aeronavx.core.passenger_experience import calculate_jet_lag
    with pytest.raises(ValueError, match="timezone offsets"):
        calculate_jet_lag("IST", "LHR")


# ── hf/utils.py coerce_airports with pandas DataFrame ────────────────────────

def test_coerce_airports_dataframe():
    pytest.importorskip("pandas")
    import pandas as pd

    from aeronavx.hf.utils import coerce_airports
    # Line 69: hasattr iterrows
    df = pd.DataFrame({"name": ["A", "B"]})
    result = coerce_airports(df)
    assert len(result) == 2


def test_try_import_pandas():
    from aeronavx.hf.utils import try_import_pandas
    result = try_import_pandas()
    # Returns pandas module if available, None if not installed
    assert result is None or hasattr(result, "DataFrame")


# ── core/airports.py line 32 ──────────────────────────────────────────────────

def test_airports_get_invalid_code_type():
    from aeronavx.core import airports
    # Line 32: ValueError for invalid code_type
    with pytest.raises(ValueError):
        airports.get("IST", code_type="invalid_type")


# ── utils/spatial_index.py linear mode (≤100 airports) ───────────────────────

def test_spatial_index_linear_nearest():
    from aeronavx.utils.spatial_index import SpatialIndex
    # Use ≤100 airports to force linear path (lines 70-81)
    airports = [
        _make_airport(iata=f"X{i:02d}", lat=float(i), lon=float(i), ident=f"LX{i:02d}")
        for i in range(10)
    ]
    idx = SpatialIndex(airports)
    assert not idx._use_scipy  # ≤100 → linear
    result = idx.nearest(5.0, 5.0, n=3)
    assert len(result) <= 3


def test_spatial_index_linear_nearest_with_max_distance():
    from aeronavx.utils.spatial_index import SpatialIndex
    airports = [
        _make_airport(iata=f"Y{i:02d}", lat=float(i), lon=float(i), ident=f"LY{i:02d}")
        for i in range(10)
    ]
    idx = SpatialIndex(airports)
    result = idx.nearest(5.0, 5.0, n=3, max_distance_km=200.0)
    assert isinstance(result, list)


def test_spatial_index_within_radius_linear():
    from aeronavx.utils.spatial_index import SpatialIndex
    airports = [
        _make_airport(iata=f"Z{i:02d}", lat=float(i), lon=float(i), ident=f"LZ{i:02d}")
        for i in range(10)
    ]
    idx = SpatialIndex(airports)
    result = idx.within_radius(5.0, 5.0, radius_km=200.0)
    assert isinstance(result, list)
