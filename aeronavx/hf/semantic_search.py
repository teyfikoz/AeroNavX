from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal, Optional

from .config import CACHE_DIR, EMBED_MODEL, HF_TOKEN, USE_LOCAL_ONLY
from .index import AirportIndex
from .utils import try_import_pandas

ReturnFormat = Literal["auto", "dataframe", "list"]


def _load_sentence_transformer(
    model_name: str,
    cache_dir: Optional[Path],
    token: Optional[str],
    local_only: bool,
):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "Semantic search requires sentence-transformers. Install with "
            "`pip install aeronavx[hf]`."
        ) from exc

    if local_only:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")

    if token and not os.getenv("HUGGINGFACE_HUB_TOKEN"):
        os.environ["HUGGINGFACE_HUB_TOKEN"] = token

    kwargs: dict[str, Any] = {}
    if cache_dir is not None:
        kwargs["cache_folder"] = str(cache_dir / "hf")
    if local_only:
        kwargs["local_files_only"] = True
    if token:
        kwargs["token"] = token

    try:
        return SentenceTransformer(model_name, **kwargs)
    except TypeError:
        kwargs.pop("token", None)
        kwargs.pop("local_files_only", None)
        return SentenceTransformer(model_name, **kwargs)
    except Exception as exc:
        message = str(exc).lower()
        if local_only:
            message = (
                f"Offline mode enabled and model '{model_name}' "
                "is not available in the local cache. "
                "Disable offline mode or pre-download the model."
            )
            raise RuntimeError(message) from exc
        if token and ("401" in message or "unauthorized" in message or "forbidden" in message):
            raise RuntimeError(
                "Hugging Face token is invalid or lacks access to the requested model."
            ) from exc
        if "404" in message or ("not found" in message and "model" in message):
            raise RuntimeError(f"Hugging Face model '{model_name}' was not found.") from exc
        if "connection" in message or "timed out" in message or "network" in message:
            raise RuntimeError(
                "Unable to download model. Check network access or enable offline mode "
                "with a cached model."
            ) from exc
        raise


class SemanticAirportSearch:
    def __init__(
        self,
        airports: Any,
        model_name: str = EMBED_MODEL,
        *,
        cache_dir: Optional[Path] = CACHE_DIR,
        token: Optional[str] = HF_TOKEN,
        local_only: bool = USE_LOCAL_ONLY,
        model: Optional[Any] = None,
        use_faiss: bool = True,
    ) -> None:
        if cache_dir is not None and not isinstance(cache_dir, Path):
            cache_dir = Path(cache_dir).expanduser()

        if model is None:
            model = _load_sentence_transformer(model_name, cache_dir, token, local_only)

        self.model = model
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.index = AirportIndex(
            airports,
            model,
            model_name,
            cache_dir=cache_dir,
            use_faiss=use_faiss,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        return_format: ReturnFormat = "auto",
    ):
        results = self.index.search(query, top_k=top_k)

        if return_format == "list":
            return results

        pandas = try_import_pandas()

        if return_format == "dataframe" and pandas is None:
            raise ImportError("pandas is required for return_format='dataframe'.")

        if return_format == "auto" and pandas is None:
            return results

        df = pandas.DataFrame(results)
        return df
