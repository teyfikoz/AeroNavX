# AeroNavX v3.1.0 Release Notes

## What's New

### API Security
- **API Key Authentication**: Set `AERONAVX_API_KEY` to require `X-API-Key` header on all endpoints (except `/health`). Backward compatible — unset means open access.
- **Rate Limiting**: In-memory sliding-window rate limiter, default 60 requests/minute per IP. Configure with `AERONAVX_RATE_LIMIT`. `/health` is exempt.
- **CORS**: Cross-origin requests enabled for browser-based clients.
- **Request Logging**: Every request is logged with method, path, status code, and duration.

### Docker Support
- Production-ready `Dockerfile` with python:3.11-slim base and health check.
- `docker-compose.yml` with environment variable configuration and cache volume persistence.
- `.dockerignore` for optimized image builds.

### Metadata Fixes
- Author email corrected from placeholder to real address.
- Documentation URL now resolves (points to README instead of non-existent /docs path).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AERONAVX_API_KEY` | *(unset = open)* | API key for endpoint authentication |
| `AERONAVX_RATE_LIMIT` | `60` | Max requests per minute per IP |
| `AERONAVX_CACHE` | `~/.aeronavx` | Cache directory for HF models |
| `AERONAVX_OFFLINE` | `0` | Set to `1` for cache-only inference |

## Quick Start (Docker)

```bash
# Build and run
docker compose up -d

# With API key
AERONAVX_API_KEY=your-secret docker compose up -d
```

## Platform Overview
AeroNavX v3.1.0 continues the **AI-powered Aviation Intelligence Platform** with offline-first datasets, optional Hugging Face semantic search, and production-ready analytics for airlines, cargo, defense, and research organizations.

## Feature Table

| Capability | Module | CLI | API |
| --- | --- | --- | --- |
| Airport + runway data | `aeronavx.core.loader`, `aeronavx.core.runways` | Yes | Yes |
| Geodesy + routing | `aeronavx.core.geodesy`, `aeronavx.core.routing` | Yes | Yes |
| Jet-lag intelligence | `aeronavx.core.passenger_experience` | Yes | Yes |
| Network & hub scoring | `aeronavx.core.network_intelligence` | Yes | Yes |
| Advanced emissions | `aeronavx.core.emissions_advanced` | Yes | Yes |
| Synthetic routing | `aeronavx.core.synthetic_routes` | Yes | Yes |
| Semantic search (HF) | `aeronavx.hf.semantic_search` | Yes | Yes |
| API authentication | `aeronavx.api.server` | — | Yes |
| Rate limiting | `aeronavx.api.server` | — | Yes |

## Migration from v3.0.x
- No breaking changes. All existing endpoints work as before.
- To enable authentication, set `AERONAVX_API_KEY` and pass `X-API-Key` header.
- Docker deployment is optional — pip install continues to work.
