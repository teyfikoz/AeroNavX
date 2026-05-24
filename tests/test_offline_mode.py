import importlib
import sys
from types import SimpleNamespace

import pytest


def test_offline_mode_missing_cache_raises(monkeypatch, tmp_path):
    class DummySentenceTransformer:
        def __init__(self, model_name, **kwargs):
            assert kwargs.get("local_files_only") is True
            raise OSError("Model not found in cache")

    dummy_module = SimpleNamespace(SentenceTransformer=DummySentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", dummy_module)
    if "aeronavx.hf.semantic_search" in sys.modules:
        del sys.modules["aeronavx.hf.semantic_search"]

    import aeronavx.hf.semantic_search as semantic_search

    importlib.reload(semantic_search)

    with pytest.raises(RuntimeError, match="Offline mode enabled"):
        semantic_search.SemanticAirportSearch([], cache_dir=tmp_path, local_only=True)


def test_invalid_token_error(monkeypatch, tmp_path):
    class DummySentenceTransformer:
        def __init__(self, model_name, **kwargs):
            raise RuntimeError("401 Unauthorized")

    dummy_module = SimpleNamespace(SentenceTransformer=DummySentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", dummy_module)

    if "aeronavx.hf.semantic_search" in sys.modules:
        del sys.modules["aeronavx.hf.semantic_search"]

    import aeronavx.hf.semantic_search as semantic_search

    importlib.reload(semantic_search)

    with pytest.raises(RuntimeError, match="token is invalid"):
        semantic_search.SemanticAirportSearch([], cache_dir=tmp_path, token="invalid-token")


def test_network_error(monkeypatch, tmp_path):
    class DummySentenceTransformer:
        def __init__(self, model_name, **kwargs):
            raise RuntimeError("Connection timed out")

    dummy_module = SimpleNamespace(SentenceTransformer=DummySentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", dummy_module)

    if "aeronavx.hf.semantic_search" in sys.modules:
        del sys.modules["aeronavx.hf.semantic_search"]

    import aeronavx.hf.semantic_search as semantic_search

    importlib.reload(semantic_search)

    with pytest.raises(RuntimeError, match="Unable to download model"):
        semantic_search.SemanticAirportSearch([], cache_dir=tmp_path)
