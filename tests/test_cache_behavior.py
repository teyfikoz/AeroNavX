import pytest

from aeronavx.hf.semantic_search import SemanticAirportSearch
from aeronavx.models.airport import Airport

np = pytest.importorskip("numpy")


class CountingEmbedder:
    def __init__(self, fail_on_bulk=False):
        self.bulk_calls = 0
        self.query_calls = 0
        self.fail_on_bulk = fail_on_bulk

    def encode(self, texts, normalize_embeddings=False):
        if isinstance(texts, str):
            texts = [texts]

        if len(texts) > 1:
            if self.fail_on_bulk:
                raise AssertionError("Bulk encode should be cached, but was called again.")
            self.bulk_calls += 1
        else:
            self.query_calls += 1

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


def _sample_airports():
    return [
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
    ]


def test_embedding_cache_reuse(tmp_path):
    airports = _sample_airports()

    embedder = CountingEmbedder()
    searcher = SemanticAirportSearch(
        airports,
        model_name="dummy-model",
        model=embedder,
        cache_dir=tmp_path,
    )

    results = searcher.search("Istanbul", top_k=1, return_format="list")
    assert results[0]["iata"] == "IST"
    assert embedder.bulk_calls == 1

    cached_files = list((tmp_path / "hf" / "semantic_search" / "dummy-model").glob("*.npz"))
    assert len(cached_files) == 1

    embedder_cached = CountingEmbedder(fail_on_bulk=True)
    searcher_cached = SemanticAirportSearch(
        airports,
        model_name="dummy-model",
        model=embedder_cached,
        cache_dir=tmp_path,
    )
    searcher_cached.search("Istanbul", top_k=1, return_format="list")


def test_clear_semantic_search_cache():
    import aeronavx

    aeronavx._semantic_engine = object()
    aeronavx.clear_semantic_search_cache()

    assert aeronavx._semantic_engine is None


def test_corrupted_cache_fallback(tmp_path):
    from aeronavx.hf.cache import embeddings_cache_path
    from aeronavx.hf.index import _fingerprint
    from aeronavx.hf.utils import airport_to_text

    airports = _sample_airports()
    texts = [airport_to_text(a) for a in airports]
    signature = _fingerprint(texts, "dummy-model")
    cache_path = embeddings_cache_path(tmp_path, "dummy-model", signature)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(b"not-a-valid-npz")

    embedder = CountingEmbedder()
    searcher = SemanticAirportSearch(
        airports,
        model_name="dummy-model",
        model=embedder,
        cache_dir=tmp_path,
    )

    searcher.search("Istanbul", top_k=1, return_format="list")
    assert embedder.bulk_calls == 1


def test_partial_embeddings_fallback(tmp_path):
    from aeronavx.hf.cache import embeddings_cache_path
    from aeronavx.hf.index import _fingerprint
    from aeronavx.hf.utils import airport_to_text

    airports = _sample_airports()
    texts = [airport_to_text(a) for a in airports]
    signature = _fingerprint(texts, "dummy-model")
    cache_path = embeddings_cache_path(tmp_path, "dummy-model", signature)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    embeddings = np.zeros((1, 3), dtype=float)
    np.savez_compressed(
        cache_path,
        embeddings=embeddings,
        signature=signature,
        count=2,
        version="v1",
    )

    embedder = CountingEmbedder()
    searcher = SemanticAirportSearch(
        airports,
        model_name="dummy-model",
        model=embedder,
        cache_dir=tmp_path,
    )

    searcher.search("Istanbul", top_k=1, return_format="list")
    assert embedder.bulk_calls == 1
