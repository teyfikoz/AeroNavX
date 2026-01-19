# AeroNavX Deployment Guide

## 1. Introduction
AeroNavX is a production-grade AI Aviation SDK that combines geospatial analytics with AI-powered semantic search and advanced aviation intelligence modules. This guide covers deployment, configuration, and operational best practices.

## 2. Architecture Overview
- Core SDK: airport data, geodesy, routing, statistics, emissions
- AI Layer (HF): semantic search, offline cache, optional ANN acceleration
- Interfaces: CLI, FastAPI API server, Python SDK
- Data: bundled OurAirports data, optional external datasets

## 3. AI Platform Layer
The AI layer lives in `aeronavx/hf` and is optional. It provides:
- Lazy model loading
- Embedding cache
- Offline inference support
- Optional FAISS acceleration (if installed)

## 4. Semantic Search Engine
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Input text built from airport metadata (name, city, country, codes)
- Cosine similarity with cached embeddings

## 5. Offline Inference
Set offline mode to force cache-only inference:

```bash
export AERONAVX_OFFLINE=1
```

If the model is not cached, AeroNavX raises a clear error. Pre-download the model once to enable offline-only use.

## 6. Cache System
Defaults:
- Cache dir: `~/.aeronavx`

Override:

```bash
export AERONAVX_CACHE="/path/to/cache"
```

Embeddings are stored under `hf/semantic_search/<model>/` as compressed NumPy files.

## 7. Dataset Pipeline
- Built-in data: OurAirports (airports + runways)
- Optional: extend with your own sources
- For enterprise, mirror datasets in private object storage

## 8. Routing Engine
- Supports multi-leg routing and shortest-path heuristics
- Great-circle distance and flight time estimation
- Synthetic routing can generate waypoint sequences

## 9. Jet-Lag Engine
- Computes timezone difference, direction, severity, and recovery time
- Uses timezonefinder if installed; falls back to longitude-based offset

## 10. Emissions Engine
- Baseline CO2 estimation per passenger
- Advanced emissions model with aircraft type and SAF comparison

## 11. Network Intelligence
- Connectivity scoring via spatial neighborhood analysis
- Hub identification and ranking

## 12. Synthetic Routes
- Generates realistic route waypoints along great circles
- Returns distance and estimated time

## 13. CLI Usage
Example commands:

```bash
aeronavx distance --from IST --to JFK --unit nmi
aeronavx semantic-search --query "London Heathrow"
aeronavx jet-lag --from IST --to JFK --age 35
aeronavx hubs --top-n 5
aeronavx emissions-advanced --from IST --to JFK --aircraft-type wide_body --saf-percent 50
aeronavx synthetic-route --from IST --to JFK --waypoints 8
```

## 14. API Usage
Start server:

```bash
python -m aeronavx.api.server
```

Endpoints:
- `/health`
- `/airport/{code}`
- `/distance`
- `/nearest`
- `/search`
- `/semantic-search`
- `/jet-lag`
- `/hubs`
- `/emissions-advanced`
- `/synthetic-route`

## 15. SDK Usage
```python
import aeronavx as anx

# Semantic search
results = anx.semantic_search("New York airport", top_k=5)

# Jet lag
jet_lag = anx.calculate_jet_lag(anx.get_airport("IST"), anx.get_airport("JFK"))

# Advanced emissions
emissions = anx.calculate_flight_emissions("IST", "JFK")
```

## 16. Production Deployment
- Use pinned versions in `requirements.txt`
- Set `AERONAVX_CACHE` to a fast local volume
- Preload HF models in build or warmup steps
- Use `AERONAVX_OFFLINE=1` for air-gapped environments
- **GPU inference**: install CUDA-enabled `torch`, set `CUDA_VISIBLE_DEVICES`, and allow sentence-transformers to pick the GPU automatically.
- **Monitoring**: expose `/health`, ship logs to your observability stack, and add FastAPI metrics middleware (Prometheus/OpenTelemetry).

## 17. Docker Example
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install .[api,hf]
ENV AERONAVX_CACHE=/data/aeronavx
EXPOSE 8000
CMD ["python", "-m", "aeronavx.api.server"]
```

## 18. CI/CD
- GitHub Actions: tests across Python 3.9-3.13
- Release workflow builds sdist + wheel and publishes to PyPI

## 19. Versioning
- Current target: `3.0.0`
- Follow semver: MAJOR for API changes, MINOR for new features, PATCH for fixes

## 20. Roadmap v4.0
- Demand forecasting models
- Delay prediction
- Airline ops dashboards
- Carbon optimization
- Hosted inference endpoints
