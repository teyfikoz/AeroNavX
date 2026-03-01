# Changelog

All notable changes to AeroNavX are documented here.

## [3.1.0] - 2026-02-28

### Added
- REST API authentication via `AERONAVX_API_KEY` environment variable (X-API-Key header).
- In-memory sliding-window rate limiting (default 60 req/min, configurable via `AERONAVX_RATE_LIMIT`).
- CORS middleware for cross-origin browser access.
- Request logging middleware (method, path, status, duration).
- Dockerfile, docker-compose.yml, and .dockerignore for containerized deployment.
- API test suite (`tests/test_api.py`).

### Fixed
- Author email updated from placeholder to real address.
- Documentation URL now points to working README anchor instead of 404 path.

### Changed
- `/health` endpoint now includes version field.
- All protected endpoints use FastAPI `Depends()` for API key verification.

## [3.0.1] - 2026-01-19

### Fixed
- CI lint failures via formatting + import cleanup.
- Python 3.9 lint compatibility (ruff config + typing guardrails).
- Release workflow switched to Trusted Publisher (OIDC).

## [3.0.0] - 2026-01-19

### Added
- AI semantic search layer with offline cache, HF token support, and optional FAISS acceleration.
- Network intelligence, jet-lag analysis, synthetic routing, and advanced emissions modeling.
- Runway loading + statistics modules with bundled OurAirports runway data.
- CLI commands and FastAPI endpoints for new AI and analytics features.
- CI matrix for Python 3.9–3.13 and release automation workflows.
- Production readiness report, deployment guide, and benchmark script.

### Changed
- Updated package metadata for Python 3.9–3.13 compatibility.
- Expanded README with AI, offline, API, CLI, and benchmark guidance.

## [2.0.5] - 2024-12-01

### Fixed
- Critical great_circle_path TypeError and synthetic route regression.
- Airport model normalization and import cleanups.
