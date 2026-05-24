# AeroNavX v3.1.0 Deployment Guide

## 1. Introduction
AeroNavX is a production-grade AI Aviation SDK that combines geospatial analytics with AI-powered semantic search and advanced aviation intelligence modules. This guide covers deployment, configuration, and operational best practices.

## 2. Architecture Overview
- Core SDK: airport data, geodesy, routing, statistics, emissions
- AI Layer (HF): semantic search, offline cache, optional ANN acceleration
- Interfaces: CLI, FastAPI API server, Python SDK
- Data: bundled OurAirports data, optional external datasets

## 3. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AERONAVX_API_KEY` | *(unset = open)* | API key for endpoint authentication |
| `AERONAVX_RATE_LIMIT` | `60` | Max requests per minute per IP |
| `AERONAVX_CACHE` | `~/.aeronavx` | Cache directory for HF models/embeddings |
| `AERONAVX_OFFLINE` | `0` | Set to `1` for cache-only inference |
| `HF_TOKEN` | — | Hugging Face API token |
| `AERONAVX_EMBED_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |

## 4. API Authentication

AeroNavX API supports optional API key authentication:

- Set `AERONAVX_API_KEY` environment variable to enable authentication
- Clients must include `X-API-Key: <key>` header in all requests
- If `AERONAVX_API_KEY` is not set, all endpoints are open (backward compatible)
- The `/health` endpoint is always open, regardless of API key configuration

```bash
# Enable authentication
export AERONAVX_API_KEY="your-secret-key"
python -m aeronavx.api.server

# Client request
curl -H "X-API-Key: your-secret-key" http://localhost:8000/airport/IST
```

## 5. Rate Limiting

Built-in sliding-window rate limiting protects the API from abuse:

- Default: **60 requests per minute per IP**
- Configure via `AERONAVX_RATE_LIMIT` environment variable
- The `/health` endpoint is exempt from rate limiting
- Returns HTTP 429 when limit is exceeded

```bash
# Set custom rate limit
export AERONAVX_RATE_LIMIT=120
```

## 6. Docker Deployment

### Quick Start
```bash
# Build and run with Docker Compose
docker compose up -d

# With API key
AERONAVX_API_KEY=your-secret docker compose up -d

# Or build manually
docker build -t aeronavx .
docker run -p 8000:8000 -e AERONAVX_API_KEY=your-secret aeronavx
```

### docker-compose.yml Configuration
The included `docker-compose.yml` provides:
- Port mapping (8000:8000)
- Environment variable passthrough for API key, rate limit, cache
- Named volume for cache persistence
- Automatic restart policy

### Health Check
The Docker image includes a built-in health check that polls `/health` every 30 seconds.

## 7. AI Platform Layer
The AI layer lives in `aeronavx/hf` and is optional. It provides:
- Lazy model loading
- Embedding cache
- Offline inference support
- Optional FAISS acceleration (if installed)

## 8. Semantic Search Engine
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Input text built from airport metadata (name, city, country, codes)
- Cosine similarity with cached embeddings

## 9. Offline Inference
Set offline mode to force cache-only inference:

```bash
export AERONAVX_OFFLINE=1
```

If the model is not cached, AeroNavX raises a clear error. Pre-download the model once to enable offline-only use.

## 10. Cache System
Defaults:
- Cache dir: `~/.aeronavx`

Override:

```bash
export AERONAVX_CACHE="/path/to/cache"
```

Embeddings are stored under `hf/semantic_search/<model>/` as compressed NumPy files.

## 11. Dataset Pipeline
- Built-in data: OurAirports (airports + runways)
- Optional: extend with your own sources
- For enterprise, mirror datasets in private object storage

## 12. Routing Engine
- Supports multi-leg routing and shortest-path heuristics
- Great-circle distance and flight time estimation
- Synthetic routing can generate waypoint sequences

## 13. Jet-Lag Engine
- Computes timezone difference, direction, severity, and recovery time
- Uses timezonefinder if installed; falls back to longitude-based offset

## 14. Emissions Engine
- Baseline CO2 estimation per passenger
- Advanced emissions model with aircraft type and SAF comparison

## 15. Network Intelligence
- Connectivity scoring via spatial neighborhood analysis
- Hub identification and ranking

## 16. Synthetic Routes
- Generates realistic route waypoints along great circles
- Returns distance and estimated time

## 17. CLI Usage
Example commands:

```bash
aeronavx distance --from IST --to JFK --unit nmi
aeronavx semantic-search --query "London Heathrow"
aeronavx jet-lag --from IST --to JFK --age 35
aeronavx hubs --top-n 5
aeronavx emissions-advanced --from IST --to JFK --aircraft-type wide_body --saf-percent 50
aeronavx synthetic-route --from IST --to JFK --waypoints 8
```

## 18. API Usage
Start server:

```bash
python -m aeronavx.api.server
```

Endpoints:
- `/health` — always open
- `/airport/{code}`
- `/distance`
- `/nearest`
- `/search`
- `/semantic-search`
- `/jet-lag`
- `/hubs`
- `/emissions-advanced`
- `/synthetic-route`

## 19. SDK Usage
```python
import aeronavx as anx

# Semantic search
results = anx.semantic_search("New York airport", top_k=5)

# Jet lag
jet_lag = anx.calculate_jet_lag(anx.get_airport("IST"), anx.get_airport("JFK"))

# Advanced emissions
emissions = anx.calculate_flight_emissions("IST", "JFK")
```

## 20. Production Deployment
- Use pinned versions in `requirements.txt`
- Set `AERONAVX_CACHE` to a fast local volume
- Preload HF models in build or warmup steps
- Use `AERONAVX_OFFLINE=1` for air-gapped environments
- **GPU inference**: install CUDA-enabled `torch`, set `CUDA_VISIBLE_DEVICES`, and allow sentence-transformers to pick the GPU automatically.
- **Monitoring**: expose `/health`, ship logs to your observability stack, and add FastAPI metrics middleware (Prometheus/OpenTelemetry).

## 21. CI/CD
- GitHub Actions: tests across Python 3.9-3.13
- Release workflow builds sdist + wheel and publishes to PyPI

## 22. Versioning
- Current: `3.1.0`
- Follow semver: MAJOR for API changes, MINOR for new features, PATCH for fixes

## 23. Roadmap v4.0
- Demand forecasting models
- Delay prediction
- Airline ops dashboards
- Carbon optimization
- Hosted inference endpoints
