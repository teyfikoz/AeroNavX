import os
from pathlib import Path
from typing import Optional


def _first_env(*names: str) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


HF_TOKEN = _first_env("HF_TOKEN", "HF_API_TOKEN", "HUGGINGFACE_HUB_TOKEN")
CACHE_DIR = Path(os.getenv("AERONAVX_CACHE", "~/.aeronavx")).expanduser()
EMBED_MODEL = os.getenv(
    "AERONAVX_EMBED_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
USE_LOCAL_ONLY = os.getenv("AERONAVX_OFFLINE", "0") == "1"
