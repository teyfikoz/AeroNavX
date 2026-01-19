import os

import pytest

from aeronavx.hf.semantic_search import SemanticAirportSearch
from aeronavx.models.airport import Airport

pytest.importorskip("sentence_transformers")
pytest.importorskip("numpy")


RUN_REAL = os.getenv("AERONAVX_RUN_REAL_MODEL_TESTS") == "1"


@pytest.mark.skipif(not RUN_REAL, reason="Set AERONAVX_RUN_REAL_MODEL_TESTS=1 to run.")
def test_semantic_search_real_model_rankings(tmp_path):
    airports = [
        Airport(
            id=1,
            ident="LTFM",
            type="large_airport",
            name="Istanbul Airport",
            latitude_deg=41.275278,
            longitude_deg=28.751944,
            elevation_ft=163,
            continent="AS",
            iso_country="TR",
            iso_region="TR-34",
            municipality="Istanbul",
            scheduled_service=True,
            gps_code="LTFM",
            iata_code="IST",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="Istanbul international main airport",
        ),
        Airport(
            id=2,
            ident="LTSA",
            type="large_airport",
            name="Istanbul Sabiha Gokcen International Airport",
            latitude_deg=40.8986,
            longitude_deg=29.3092,
            elevation_ft=312,
            continent="AS",
            iso_country="TR",
            iso_region="TR-34",
            municipality="Istanbul",
            scheduled_service=True,
            gps_code="LTSA",
            iata_code="SAW",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="Sabiha Gokcen Istanbul airport",
        ),
        Airport(
            id=3,
            ident="KJFK",
            type="large_airport",
            name="John F Kennedy International Airport",
            latitude_deg=40.639801,
            longitude_deg=-73.7789,
            elevation_ft=13,
            continent="NA",
            iso_country="US",
            iso_region="US-NY",
            municipality="New York",
            scheduled_service=True,
            gps_code="KJFK",
            iata_code="JFK",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="New York international airport",
        ),
        Airport(
            id=4,
            ident="KLGA",
            type="large_airport",
            name="LaGuardia Airport",
            latitude_deg=40.7769,
            longitude_deg=-73.874,
            elevation_ft=21,
            continent="NA",
            iso_country="US",
            iso_region="US-NY",
            municipality="New York",
            scheduled_service=True,
            gps_code="KLGA",
            iata_code="LGA",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="New York domestic airport",
        ),
        Airport(
            id=5,
            ident="KEWR",
            type="large_airport",
            name="Newark Liberty International Airport",
            latitude_deg=40.6895,
            longitude_deg=-74.1745,
            elevation_ft=18,
            continent="NA",
            iso_country="US",
            iso_region="US-NJ",
            municipality="Newark",
            scheduled_service=True,
            gps_code="KEWR",
            iata_code="EWR",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="New York area Newark airport",
        ),
        Airport(
            id=6,
            ident="RJAA",
            type="large_airport",
            name="Narita International Airport",
            latitude_deg=35.7647,
            longitude_deg=140.3864,
            elevation_ft=141,
            continent="AS",
            iso_country="JP",
            iso_region="JP-12",
            municipality="Tokyo",
            scheduled_service=True,
            gps_code="RJAA",
            iata_code="NRT",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="Tokyo Narita international airport",
        ),
        Airport(
            id=7,
            ident="RJTT",
            type="large_airport",
            name="Tokyo Haneda Airport",
            latitude_deg=35.552258,
            longitude_deg=139.779694,
            elevation_ft=21,
            continent="AS",
            iso_country="JP",
            iso_region="JP-13",
            municipality="Tokyo",
            scheduled_service=True,
            gps_code="RJTT",
            iata_code="HND",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="Tokyo Haneda airport",
        ),
        Airport(
            id=8,
            ident="EGLL",
            type="large_airport",
            name="London Heathrow Airport",
            latitude_deg=51.4775,
            longitude_deg=-0.461389,
            elevation_ft=83,
            continent="EU",
            iso_country="GB",
            iso_region="GB-ENG",
            municipality="London",
            scheduled_service=True,
            gps_code="EGLL",
            iata_code="LHR",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="London Heathrow airport",
        ),
        Airport(
            id=9,
            ident="EGKK",
            type="large_airport",
            name="London Gatwick Airport",
            latitude_deg=51.1481,
            longitude_deg=-0.1903,
            elevation_ft=203,
            continent="EU",
            iso_country="GB",
            iso_region="GB-ENG",
            municipality="London",
            scheduled_service=True,
            gps_code="EGKK",
            iata_code="LGW",
            local_code=None,
            home_link=None,
            wikipedia_link=None,
            keywords="London Gatwick airport",
        ),
    ]

    searcher = SemanticAirportSearch(
        airports,
        cache_dir=tmp_path,
        token=os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN"),
    )

    queries = {
        "Istanbul international airport": "IST",
        "New York airport": "JFK",
        "Tokyo Narita": "NRT",
        "London Heathrow": "LHR",
    }

    for query, expected_iata in queries.items():
        results = searcher.search(query, top_k=3, return_format="list")
        iatas = [r["iata"] for r in results]
        scores = [r["score"] for r in results]

        assert iatas[0] == expected_iata
        assert expected_iata in iatas
        assert scores == sorted(scores, reverse=True)
        assert scores[0] - scores[-1] >= 0.01

        repeated = searcher.search(query, top_k=3, return_format="list")
        assert [r["iata"] for r in repeated] == iatas
