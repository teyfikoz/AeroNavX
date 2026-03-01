"""Tests for AeroNavX REST API — auth, rate limiting, and core endpoints."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_api_state():
    """Reset module-level state between tests."""
    import importlib

    import aeronavx.api.server as srv_module

    # Clear rate limit store
    srv_module._rate_limit_store.clear()
    yield


def _make_client(api_key=None, rate_limit=None):
    """Create a fresh TestClient with optional env overrides."""
    env = {}
    if api_key is not None:
        env["AERONAVX_API_KEY"] = api_key
    if rate_limit is not None:
        env["AERONAVX_RATE_LIMIT"] = str(rate_limit)

    with patch.dict(os.environ, env, clear=False):
        import importlib

        import aeronavx.api.server as srv_module

        # Re-read env vars
        srv_module._API_KEY = os.environ.get("AERONAVX_API_KEY")
        srv_module._RATE_LIMIT = int(os.environ.get("AERONAVX_RATE_LIMIT", "60"))
        srv_module._rate_limit_store.clear()

        return TestClient(srv_module.app)


class TestHealthEndpoint:
    def test_health_no_auth(self):
        """Health endpoint is always open, even with API key set."""
        client = _make_client(api_key="secret123")
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_no_key_configured(self):
        client = _make_client()
        resp = client.get("/health")
        assert resp.status_code == 200


class TestApiKeyAuth:
    def test_open_access_without_key(self):
        """When no API key is configured, endpoints are open."""
        client = _make_client()
        resp = client.get("/airport/IST")
        assert resp.status_code == 200

    def test_valid_key_allows_access(self):
        """Correct API key grants access."""
        client = _make_client(api_key="mysecret")
        resp = client.get("/airport/IST", headers={"X-API-Key": "mysecret"})
        assert resp.status_code == 200

    def test_invalid_key_returns_401(self):
        """Wrong API key returns 401."""
        client = _make_client(api_key="mysecret")
        resp = client.get("/airport/IST", headers={"X-API-Key": "wrong"})
        assert resp.status_code == 401

    def test_missing_key_returns_401(self):
        """Missing API key returns 401 when key is configured."""
        client = _make_client(api_key="mysecret")
        resp = client.get("/airport/IST")
        assert resp.status_code == 401


class TestRateLimiting:
    def test_rate_limit_enforced(self):
        """Exceeding rate limit returns 429."""
        client = _make_client(rate_limit=5)
        for i in range(5):
            resp = client.get("/airport/IST")
            assert resp.status_code == 200, f"Request {i + 1} should succeed"
        resp = client.get("/airport/IST")
        assert resp.status_code == 429

    def test_health_exempt_from_rate_limit(self):
        """Health endpoint is exempt from rate limiting."""
        client = _make_client(rate_limit=2)
        for _ in range(5):
            resp = client.get("/health")
            assert resp.status_code == 200


class TestCoreEndpoints:
    def test_airport_found(self):
        client = _make_client()
        resp = client.get("/airport/JFK")
        assert resp.status_code == 200
        assert "iata_code" in resp.json()

    def test_airport_not_found(self):
        client = _make_client()
        resp = client.get("/airport/ZZZZ99")
        assert resp.status_code in (400, 404)

    def test_distance(self):
        client = _make_client()
        resp = client.get("/distance", params={"from": "IST", "to": "JFK"})
        assert resp.status_code == 200
        assert "distance" in resp.json()

    def test_nearest(self):
        client = _make_client()
        resp = client.get("/nearest", params={"lat": 41.0, "lon": 29.0, "n": 3})
        assert resp.status_code == 200
        assert "airports" in resp.json()

    def test_search(self):
        client = _make_client()
        resp = client.get("/search", params={"q": "Istanbul"})
        assert resp.status_code == 200
