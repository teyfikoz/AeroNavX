# AeroNavX

![PyPI](https://img.shields.io/pypi/v/aeronavx)
![Python](https://img.shields.io/pypi/pyversions/aeronavx)
![License](https://img.shields.io/badge/license-MIT-blue)
![CI](https://github.com/teyfikoz/AeroNavX/actions/workflows/test.yml/badge.svg)

A production-grade **AI Aviation SDK** for airport data, flight geometry, network intelligence, emissions, and passenger experience.

## Features

- 🛫 **Airport Database**: 84,000+ global airports with IATA/ICAO indexing
- 🛬 **Runway Information**: 47,000+ runways with dimensions and surfaces
- 📊 **Aviation Statistics**: Country, continent, and global analytics
- 📏 **Distance Calculations**: Haversine, Vincenty, SLC
- 🌍 **Geodesy**: Bearings, midpoints, great circle paths
- 🔍 **Search**: Fuzzy name search + nearest neighbor queries
- 🤖 **AI Semantic Search** (HF): Embedding-based airport search
- 🧠 **Jet Lag Intelligence**: Severity, direction, recovery estimation
- 🌐 **Network & Hub Intelligence**: Connectivity-based hub scoring
- 🛤️ **Synthetic Routing**: Great-circle routes + waypoint generation
- 🌱 **Emissions**: Baseline + advanced emissions with SAF comparisons
- ⏰ **Timezone Support**: Local time conversion + fallback offset
- 🌤️ **Weather**: METAR/TAF fetching
- 💻 **CLI**: Command-line interface
- 🌐 **REST API**: FastAPI-based endpoints

## Architecture

- **Core (`aeronavx/core`)**: data loaders, geodesy, routing, emissions, statistics
- **AI Layer (`aeronavx/hf`)**: semantic search, cache, offline inference
- **Interfaces**: CLI (`aeronavx/cli`) + FastAPI server (`aeronavx/api`)
- **Data (`aeronavx/data`)**: bundled OurAirports datasets for offline-first use

## Installation

```bash
pip install aeronavx
```

### Extras matrix

```bash
# Full data features (pandas, scipy, timezonefinder, rapidfuzz, requests)
pip install aeronavx[full]

# AI semantic search (HF)
pip install aeronavx[hf]

# API server
pip install aeronavx[api]

# Everything
pip install aeronavx[all]
```

**Or from source:**
```bash
git clone https://github.com/teyfikoz/AeroNavX.git
cd AeroNavX
pip install -e .
```

## Quick Start

```python
import aeronavx

# Get airports
ist = aeronavx.get_airport("IST")
jfk = aeronavx.get_airport("JFK")

# Calculate distance
dist_km = ist.distance_to(jfk)
print(f"Distance: {dist_km:.2f} km")

# Find nearest airports
nearest = aeronavx.nearest_airport(41.0, 29.0, n=5)

# Estimate emissions
co2 = aeronavx.estimate_co2_kg_for_segment("IST", "JFK")
print(f"CO2: {co2:.2f} kg per passenger")
```

### AI Semantic Search (HF)

```python
import aeronavx as anx

results = anx.semantic_search("New York international", top_k=5)

# If pandas is installed, results is a DataFrame
print(results[["iata", "name", "municipality", "score"]])
```

### Jet Lag Intelligence

```python
import aeronavx as anx

ist = anx.get_airport("IST")
jfk = anx.get_airport("JFK")

jet_lag = anx.calculate_jet_lag(ist, jfk, age=35)
print(jet_lag.direction.value, jet_lag.severity.value, jet_lag.estimated_recovery_days)
```

### Network & Hub Intelligence

```python
import aeronavx as anx

hubs = anx.identify_global_hubs(top_n=5)
for hub in hubs:
    print(hub.airport.iata_code, hub.hub_score)
```

### Advanced Emissions + SAF

```python
import aeronavx as anx

emissions = anx.calculate_flight_emissions(
    "IST", "JFK",
    aircraft_type=anx.AircraftType.WIDE_BODY,
    fuel_type=anx.FuelType.JET_A1,
    load_factor=0.85,
)
print(emissions.total_co2_kg, emissions.co2_per_passenger_kg)

savings = anx.compare_saf_savings("IST", "JFK", saf_percentage=50)
print(savings.reduction_percentage)
```

### Synthetic Routing

```python
import aeronavx as anx

route = anx.generate_route("IST", "JFK", num_waypoints=8)
print(route.total_distance_km, route.total_time_hours)
```

### Offline Mode & Cache

Set environment variables before import:

```bash
export HF_TOKEN="your_token"
export AERONAVX_CACHE="~/.aeronavx"
export AERONAVX_OFFLINE=1
export AERONAVX_EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

Offline mode uses cached models only; if the model is not cached, a clear error is raised.

Supported tokens:
- `HF_TOKEN`
- `HF_API_TOKEN`
- `HUGGINGFACE_HUB_TOKEN`

### Advanced: Filtering Airports

```python
from aeronavx.core import loader

# Load only major airports (large + medium with scheduled service)
major_airports = loader.load_airports(
    include_types=['large_airport', 'medium_airport'],
    scheduled_service_only=True
)
print(f"Major airports: {len(major_airports):,}")  # ~3,200

# Load specific countries
us_airports = loader.load_airports(countries=['US'])
print(f"US airports: {len(us_airports):,}")  # ~20,000

# Load airports with IATA codes only
iata_airports = loader.load_airports(has_iata_only=True)
print(f"IATA airports: {len(iata_airports):,}")  # ~9,000
```

### Runway Information

```python
import aeronavx

# Get all runways for an airport
runways = aeronavx.get_runways_by_airport("KJFK")
for rwy in runways:
    print(f"{rwy.designation}: {rwy.length_ft:.0f}ft, {rwy.surface}")

# Get the longest runway
longest = aeronavx.get_longest_runway("KJFK")
print(f"Longest: {longest.designation} - {longest.length_ft:.0f}ft")

# Get only paved runways
paved = aeronavx.get_paved_runways("KJFK")
print(f"Paved runways: {len(paved)}")
```

### Aviation Statistics

```python
import aeronavx

# Global statistics
stats = aeronavx.get_global_stats()
print(f"Total airports: {stats.total_airports:,}")
print(f"Total runways: {stats.total_runways:,}")
print(f"Countries: {stats.countries_count}")
print(f"Longest runway: {stats.longest_runway_ft:,.0f} ft")

# Country statistics
us_stats = aeronavx.get_country_stats("US")
print(f"US has {us_stats.total_airports:,} airports")
print(f"Large airports: {us_stats.large_airports}")
print(f"Total runways: {us_stats.total_runways:,}")

# Continent statistics
eu_stats = aeronavx.get_continent_stats("EU")
print(f"Europe: {eu_stats.total_airports:,} airports")
print(f"Countries: {eu_stats.countries_count}")

# Top countries
top = aeronavx.get_top_countries_by_airports(5)
for country, count in top:
    print(f"{country}: {count:,} airports")
```

## CLI Usage

```bash
# Calculate distance
aeronavx distance --from IST --to JFK --unit nmi

# Find nearest airports
aeronavx nearest --lat 41.0 --lon 29.0 --n 5

# Search by name
aeronavx search --name "Heathrow"

# Estimate emissions
aeronavx emissions --from IST --to LHR

# Flight time
aeronavx flight-time --from IST --to JFK

# Semantic search (HF)
aeronavx semantic-search --query "London Heathrow"

# Jet lag analysis
aeronavx jet-lag --from IST --to JFK --age 35

# Global hubs
aeronavx hubs --top-n 5

# Advanced emissions
aeronavx emissions-advanced --from IST --to JFK --aircraft-type wide_body --saf-percent 50

# Synthetic route
aeronavx synthetic-route --from IST --to JFK --waypoints 8
```

## API Server

```bash
python -m aeronavx.api.server
```

Then access:
- http://localhost:8000/health
- http://localhost:8000/airport/IST
- http://localhost:8000/distance?from=IST&to=JFK
- http://localhost:8000/nearest?lat=41.0&lon=29.0&n=5
- http://localhost:8000/semantic-search?q=London%20Heathrow
- http://localhost:8000/jet-lag?from=IST&to=JFK
- http://localhost:8000/hubs?top_n=5
- http://localhost:8000/emissions-advanced?from=IST&to=JFK&aircraft_type=wide_body
- http://localhost:8000/synthetic-route?from=IST&to=JFK

### API Authentication

Set `AERONAVX_API_KEY` to enable API key authentication:

```bash
export AERONAVX_API_KEY="your-secret-key"
python -m aeronavx.api.server
```

Then include the key in requests:

```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8000/airport/IST
```

The `/health` endpoint is always open. If `AERONAVX_API_KEY` is not set, all endpoints are open (backward compatible).

### Rate Limiting

Built-in rate limiting defaults to **60 requests/minute per IP**. Configure with:

```bash
export AERONAVX_RATE_LIMIT=120  # 120 req/min
```

The `/health` endpoint is exempt from rate limiting.

## Docker Deployment

```bash
# Build and run
docker compose up -d

# With API key
AERONAVX_API_KEY=your-secret docker compose up -d

# Or build manually
docker build -t aeronavx .
docker run -p 8000:8000 -e AERONAVX_API_KEY=your-secret aeronavx
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AERONAVX_API_KEY` | *(unset = open)* | API key for endpoint authentication |
| `AERONAVX_RATE_LIMIT` | `60` | Max requests per minute per IP |
| `AERONAVX_CACHE` | `~/.aeronavx` | Cache directory for HF models/embeddings |
| `AERONAVX_OFFLINE` | `0` | Set to `1` for cache-only inference |
| `HF_TOKEN` | — | Hugging Face API token |
| `AERONAVX_EMBED_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |

## Data

AeroNavX includes **84,000+ airports** and **47,000+ runways** from [OurAirports](https://ourairports.com/data/), which provides:
- ✅ **Global Coverage**: Airports, heliports, seaplane bases, and runways worldwide
- ✅ **MIT License**: Free to use commercially
- ✅ **Regular Updates**: Community-maintained and updated
- ✅ **Comprehensive Data**: IATA/ICAO codes, coordinates, types, runway dimensions, surfaces, and more

**Data Attribution:**
Airport and runway data from [OurAirports](https://ourairports.com) (David Megginson et al.) - Licensed under [MIT License](https://github.com/davidmegginson/ourairports-data)

## Examples

See `examples/` directory for:
- `basic_distance.py`: Distance calculations
- `nearest_airports.py`: Finding nearby airports
- `routing_example.py`: Multi-segment routes
- `emissions_example.py`: CO2 estimation

## Testing

```bash
pytest
```

Run real-model semantic search tests (optional):

```bash
AERONAVX_RUN_REAL_MODEL_TESTS=1 pytest tests/test_semantic_search_real_model.py
```

## Benchmarks

Run the semantic search benchmark locally:

```bash
python benchmark_semantic_search.py --sample-size 2000
```

Latest benchmark outputs are included in `PRODUCTION_READINESS_REPORT.md`.

## Dependencies

**Required**: Python >= 3.9

**Optional**:
- `pandas`: DataFrame support
- `scipy`: Faster spatial indexing
- `rapidfuzz`: Better fuzzy search
- `timezonefinder`: Timezone support
- `fastapi`, `uvicorn`: API server
- `requests`: Weather data
- `sentence-transformers`, `transformers`, `torch`, `datasets`, `huggingface_hub`, `accelerate`: HF semantic search
- `faiss-cpu` (optional): ANN acceleration for semantic search

## Roadmap

- **v4.0**: demand forecasting, delay prediction, airline ops dashboards
- **v4.1**: carbon optimization + lifecycle emissions modeling
- **v4.2**: hosted inference endpoints and enterprise deployments

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.
