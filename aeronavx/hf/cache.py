from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .utils import sanitize_model_id

CACHE_VERSION = "v1"


def embeddings_cache_path(cache_dir: Path, model_id: str, signature: str) -> Path:
    safe_model = sanitize_model_id(model_id)
    return cache_dir / "hf" / "semantic_search" / safe_model / f"{signature}.npz"


def load_embeddings(path: Path) -> Optional[tuple[Any, str, int, str]]:
    if not path.exists():
        return None

    import numpy as np

    try:
        data = np.load(path, allow_pickle=False)
        embeddings = data["embeddings"]
        signature = str(data["signature"].item())
        count = int(data["count"].item())
        version = str(data["version"].item())
    except Exception:
        return None

    if getattr(embeddings, "shape", None) is None:
        return None
    if embeddings.shape[0] != count:
        return None

    return embeddings, signature, count, version


def save_embeddings(path: Path, embeddings: Any, signature: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    import numpy as np

    np.savez_compressed(
        path,
        embeddings=embeddings,
        signature=signature,
        count=embeddings.shape[0],
        version=CACHE_VERSION,
    )
