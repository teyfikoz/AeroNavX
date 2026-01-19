import importlib
import sys
from pathlib import Path


def _reload_config(monkeypatch, env):
    keys = [
        "HF_TOKEN",
        "HF_API_TOKEN",
        "HUGGINGFACE_HUB_TOKEN",
        "AERONAVX_CACHE",
        "AERONAVX_EMBED_MODEL",
        "AERONAVX_OFFLINE",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    if "aeronavx.hf.config" in sys.modules:
        del sys.modules["aeronavx.hf.config"]

    import aeronavx.hf.config as config

    return importlib.reload(config)


def test_token_precedence(monkeypatch):
    config = _reload_config(
        monkeypatch,
        {
            "HF_API_TOKEN": "api-token",
            "HUGGINGFACE_HUB_TOKEN": "hub-token",
        },
    )
    assert config.HF_TOKEN == "api-token"

    config = _reload_config(
        monkeypatch,
        {
            "HF_TOKEN": "primary-token",
            "HF_API_TOKEN": "api-token",
            "HUGGINGFACE_HUB_TOKEN": "hub-token",
        },
    )
    assert config.HF_TOKEN == "primary-token"


def test_cache_dir_override(monkeypatch, tmp_path):
    config = _reload_config(monkeypatch, {"AERONAVX_CACHE": str(tmp_path)})
    assert config.CACHE_DIR == Path(tmp_path)


def test_embed_model_override(monkeypatch):
    config = _reload_config(monkeypatch, {"AERONAVX_EMBED_MODEL": "custom/model"})
    assert config.EMBED_MODEL == "custom/model"


def test_offline_flag(monkeypatch):
    config = _reload_config(monkeypatch, {"AERONAVX_OFFLINE": "1"})
    assert config.USE_LOCAL_ONLY is True

    config = _reload_config(monkeypatch, {"AERONAVX_OFFLINE": "0"})
    assert config.USE_LOCAL_ONLY is False
