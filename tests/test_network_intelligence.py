from aeronavx.core.network_intelligence import NetworkIntelligence
from aeronavx.models.airport import Airport


def _airport(code, airport_type, lat=0.0, lon=0.0):
    return Airport(
        id=None,
        ident=code,
        type=airport_type,
        name=f"{code} Airport",
        latitude_deg=lat,
        longitude_deg=lon,
        elevation_ft=None,
        continent=None,
        iso_country=None,
        iso_region=None,
        municipality=None,
        scheduled_service=True,
        gps_code=code,
        iata_code=code,
        local_code=None,
        home_link=None,
        wikipedia_link=None,
        keywords=None,
    )


def test_network_intelligence_ranking():
    airports = [
        _airport("AAA", "large_airport", 0.0, 0.0),
        _airport("BBB", "medium_airport", 0.1, 0.1),
        _airport("CCC", "small_airport", -0.1, -0.1),
    ]

    intelligence = NetworkIntelligence(airports, radius_km=500)
    ranked = intelligence.rank_airports()

    assert ranked[0].airport.iata_code == "AAA"
    assert ranked[0].hub_score >= ranked[1].hub_score >= ranked[2].hub_score
