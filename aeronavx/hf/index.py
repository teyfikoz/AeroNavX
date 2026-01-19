from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

from .cache import CACHE_VERSION, embeddings_cache_path, load_embeddings, save_embeddings
from .utils import TEXT_VERSION, airport_to_record, airport_to_text, coerce_airports


def _normalize_embeddings(embeddings):
    import numpy as np

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return embeddings / norms


def _encode(model: Any, texts: list[str]):
    try:
        embeddings = model.encode(texts, normalize_embeddings=True)
    except TypeError:
        embeddings = model.encode(texts)
    return embeddings


def _fingerprint(texts: list[str], model_id: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(CACHE_VERSION.encode("utf-8"))
    hasher.update(TEXT_VERSION.encode("utf-8"))
    hasher.update(model_id.encode("utf-8"))
    for text in texts:
        hasher.update(text.encode("utf-8"))
        hasher.update(b"\0")
    return hasher.hexdigest()


class AirportIndex:
    def __init__(
        self,
        airports: Any,
        model: Any,
        model_id: str,
        cache_dir: Optional[Path] = None,
        use_faiss: bool = True,
    ) -> None:
        self.model = model
        self.model_id = model_id
        self.cache_dir = cache_dir
        self.use_faiss = use_faiss

        airports_list = coerce_airports(airports)
        self.records = [airport_to_record(a) for a in airports_list]
        self.texts = [airport_to_text(a) for a in airports_list]

        self.embeddings = self._load_or_build_embeddings()
        self._faiss_index = self._build_faiss_index()

    def _load_or_build_embeddings(self):
        import numpy as np

        if not self.texts:
            return np.zeros((0, 0), dtype=float)

        signature = _fingerprint(self.texts, self.model_id)
        cached = None
        if self.cache_dir is not None:
            cache_path = embeddings_cache_path(self.cache_dir, self.model_id, signature)
            cached = load_embeddings(cache_path)

        if cached:
            embeddings, sig, count, version = cached
            if (
                sig == signature
                and count == len(self.texts)
                and embeddings.shape[0] == len(self.texts)
                and version == CACHE_VERSION
            ):
                return embeddings

        embeddings = _encode(self.model, self.texts)
        embeddings = np.asarray(embeddings)
        embeddings = _normalize_embeddings(embeddings)

        if self.cache_dir is not None:
            cache_path = embeddings_cache_path(self.cache_dir, self.model_id, signature)
            save_embeddings(cache_path, embeddings, signature)

        return embeddings

    def _build_faiss_index(self):
        if not self.use_faiss:
            return None

        try:
            import faiss
        except Exception:
            return None

        if self.embeddings is None or len(self.embeddings) == 0:
            return None

        dims = int(self.embeddings.shape[1])
        if dims == 0:
            return None
        index = faiss.IndexFlatIP(dims)
        index.add(self.embeddings.astype("float32"))
        return index

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        import numpy as np

        if top_k <= 0 or len(self.embeddings) == 0:
            return []

        query_embeddings = _encode(self.model, [query])
        query_embeddings = np.asarray(query_embeddings)
        if query_embeddings.ndim == 2:
            query_embeddings = query_embeddings[0]
        query_embeddings = query_embeddings.reshape(1, -1)
        query_embeddings = _normalize_embeddings(query_embeddings)[0]

        if self._faiss_index is not None:
            top_k = min(top_k, len(self.records))
            scores, indices = self._faiss_index.search(
                query_embeddings.astype("float32"),
                top_k,
            )
            scores = scores[0]
            indices = indices[0]
        else:
            scores = np.dot(self.embeddings, query_embeddings)
            top_k = min(top_k, len(scores))
            if top_k == 0:
                return []
            if top_k == len(scores):
                indices = np.argsort(scores)[::-1]
            else:
                indices = np.argpartition(-scores, top_k - 1)[:top_k]
                indices = indices[np.argsort(scores[indices])[::-1]]

        results = []
        for idx in indices:
            if idx < 0:
                continue
            record = dict(self.records[idx])
            record["score"] = float(scores[idx])
            results.append(record)

        return results
