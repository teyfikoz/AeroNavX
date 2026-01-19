# AeroNavX v3.0.1 Release Notes

## Patch Summary
- CI lint/formatting stabilized and import ordering standardized.
- Trusted Publisher (OIDC) enabled for GitHub Actions releases.
- Python 3.9 lint compatibility tightened without API changes.

## Platform Overview
AeroNavX v3.0.1 continues the **AI-powered Aviation Intelligence Platform** introduced in v3.0.0, with offline-first datasets, optional Hugging Face semantic search, and production-ready analytics for airlines, cargo, defense, and research organizations.

## Feature Table

| Capability | Module | CLI | API |
| --- | --- | --- | --- |
| Airport + runway data | `aeronavx.core.loader`, `aeronavx.core.runways` | ✅ | ✅ |
| Geodesy + routing | `aeronavx.core.geodesy`, `aeronavx.core.routing` | ✅ | ✅ |
| Jet-lag intelligence | `aeronavx.core.passenger_experience` | ✅ | ✅ |
| Network & hub scoring | `aeronavx.core.network_intelligence` | ✅ | ✅ |
| Advanced emissions | `aeronavx.core.emissions_advanced` | ✅ | ✅ |
| Synthetic routing | `aeronavx.core.synthetic_routes` | ✅ | ✅ |
| Semantic search (HF) | `aeronavx.hf.semantic_search` | ✅ | ✅ |

## AI Layer Highlights
- `aeronavx[hf]` optional install with **offline-first** inference.
- HF token support via `HF_TOKEN`, `HF_API_TOKEN`, or `HUGGINGFACE_HUB_TOKEN`.
- Deterministic cache behavior and optional FAISS acceleration.

## Offline-First Design
- OurAirports datasets are bundled in `aeronavx/data`.
- Semantic embeddings are cached under `~/.aeronavx` (override with `AERONAVX_CACHE`).
- Set `AERONAVX_OFFLINE=1` to enforce cache-only inference.

## Performance & Benchmarks
- Cold-start vs warm-start timing is captured in `PRODUCTION_READINESS_REPORT.md`.
- Run local benchmark with `python benchmark_semantic_search.py --sample-size 2000`.

## Use Cases
- **Airline planning**: demand research, network and hub scoring, emissions modeling.
- **Cargo operations**: routing analysis and performance optimization.
- **Defense & government**: offline-first geospatial analytics.
- **Research**: open data pipelines with AI-native semantic search.

## Migration Notes from v2.x
- Minimum Python version is now **3.9**.
- New AI layer is optional; base install remains lightweight.
- New APIs: `calculate_jet_lag`, `identify_global_hubs`, `generate_route`, `calculate_flight_emissions`.
- Optional HF dependencies are installed with `pip install aeronavx[hf]`.

## Release Summary
AeroNavX v3.0.1 is a maintenance release that preserves the full v3.0.0 feature set while hardening CI, linting, and publishing workflows.
