import pytest

from aeronavx.hf.semantic_search import SemanticAirportSearch
from aeronavx.models.airport import Airport

np = pytest.importorskip("numpy")


class DummyEmbedder:
    def encode(self, texts, normalize_embeddings=False):
        if isinstance(texts, str):
            texts = [texts]

        vectors = []
        for text in texts:
            text_lower = text.lower()
            vec = np.array(
                [
                    float(text_lower.count("istanbul")),
                    float(text_lower.count("new")),
                    float(len(text_lower)),
                ],
                dtype=float,
            )
            vectors.append(vec)

        embeddings = np.vstack(vectors)

        if normalize_embeddings:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1.0, norms)
            embeddings = embeddings / norms

        return embeddings


def test_semantic_search_ranks_expected_airport():
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
            keywords=None,
        ),
        Airport(
            id=2,
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
            keywords=None,
        ),
        Airport(
            id=3,
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
            keywords=None,
        ),
    ]

    searcher = SemanticAirportSearch(
        airports,
        model_name="dummy",
        model=DummyEmbedder(),
        cache_dir=None,
    )

    results = searcher.search("Istanbul main airport", top_k=2, return_format="list")

    assert len(results) == 2
    assert results[0]["iata"] == "IST"


def test_return_format_auto_list_dataframe():
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
            keywords=None,
        )
    ]

    searcher = SemanticAirportSearch(
        airports,
        model_name="dummy",
        model=DummyEmbedder(),
        cache_dir=None,
    )

    auto_result = searcher.search("Istanbul airport", return_format="auto")
    list_result = searcher.search("Istanbul airport", return_format="list")

    assert isinstance(list_result, list)

    pandas = None
    try:
        import pandas as pd
        pandas = pd
    except ImportError:
        pass

    if pandas is None:
        assert isinstance(auto_result, list)
    else:
        df_result = searcher.search("Istanbul airport", return_format="dataframe")
        assert isinstance(auto_result, pandas.DataFrame)
        assert isinstance(df_result, pandas.DataFrame)
