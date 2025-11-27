# AeroNavX

A production-grade Python library for airport data and flight geometry calculations.

## Features

- 🛫 **Airport Database**: Global airport data with efficient IATA/ICAO indexing
- 📏 **Distance Calculations**: Haversine, Vincenty, and Spherical Law of Cosines
- 🌍 **Geodesy**: Bearings, midpoints, great circle paths
- 🔍 **Search**: Fuzzy name search, nearest neighbor queries, radius search
- 🛤️ **Routing**: Multi-segment routes, flight time estimation, shortest paths
- 📊 **Analytics**: Statistics by country, continent, type, and elevation
- ⏰ **Timezone Support**: Automatic timezone detection and local time
- 🌱 **Emissions**: CO2 emissions estimation per passenger
- 🌤️ **Weather**: METAR and TAF data fetching
- 💻 **CLI**: Command-line interface for quick queries
- 🌐 **REST API**: FastAPI-based web service

## Installation

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

## Data

Place your `airports.csv` file in the `data/` directory. The CSV should contain:
- Basic info: id, ident, type, name
- Coordinates: latitude_deg, longitude_deg, elevation_ft
- Location: continent, iso_country, iso_region, municipality
- Codes: gps_code (ICAO), iata_code, local_code
- Optional: scheduled_service, home_link, wikipedia_link, keywords

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

## Dependencies

**Required**: Python >= 3.10

**Optional**:
- `pandas`: DataFrame support
- `scipy`: Faster spatial indexing
- `rapidfuzz`: Better fuzzy search
- `timezonefinder`: Timezone support
- `fastapi`, `uvicorn`: API server
- `requests`: Weather data

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.
