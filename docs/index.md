# AeroNavX Documentation

AeroNavX is a production-grade Python library for airport data and flight geometry calculations.

## Features

- **Airport Database**: Load and query global airport data with efficient indexing
- **Distance Calculations**: Multiple geodesic models (Haversine, Vincenty, Spherical Law of Cosines)
- **Geodesy Functions**: Bearings, midpoints, intermediate points, great circle paths
- **Search & Discovery**: Fuzzy name search, nearest neighbor queries, radius search
- **Routing**: Multi-segment routes, flight time estimation, shortest path finding
- **Analytics**: Statistics by country/continent/type, elevation analysis
- **Timezone Support**: Automatic timezone detection and local time conversion
- **Emissions**: CO2 emissions estimation for flights
- **Weather**: METAR and TAF data fetching
- **CLI Tool**: Command-line interface for common operations
- **REST API**: FastAPI-based web service

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import aeronavx

# Get airport by code
ist = aeronavx.get_airport("IST")
jfk = aeronavx.get_airport("JFK")

# Calculate distance
dist_km = ist.distance_to(jfk)
print(f"Distance: {dist_km:.2f} km")

# Find nearest airports
nearest = aeronavx.nearest_airport(41.0, 29.0, n=5)

# Estimate emissions
co2_kg = aeronavx.estimate_co2_kg_for_segment("IST", "JFK")
print(f"CO2: {co2_kg:.2f} kg per passenger")
```

## CLI Usage

```bash
aeronavx distance --from IST --to JFK --unit km
aeronavx nearest --lat 41.0 --lon 29.0 --n 5
aeronavx search --name "Heathrow"
aeronavx emissions --from IST --to LHR
```

## API Server

```bash
python -m aeronavx.api.server
```

Access at http://localhost:8000

## Data Requirements

Place your `airports.csv` file in the `data/` directory. The CSV should contain columns:

- id, ident, type, name
- latitude_deg, longitude_deg, elevation_ft
- continent, iso_country, iso_region, municipality
- scheduled_service, gps_code, iata_code, local_code
- home_link, wikipedia_link, keywords

## Dependencies

**Core**:
- Python >= 3.10

**Optional**:
- pandas: DataFrame support
- scipy: Faster spatial indexing
- rapidfuzz: Better fuzzy search
- timezonefinder: Timezone support
- fastapi, uvicorn: API server
- requests: Weather data

## License

MIT License
