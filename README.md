# AeroNavX

**Production-grade aviation data library** — 84,000+ airports, Haversine/Vincenty distances, great-circle routing, CO2 emissions, METAR/TAF weather, and runway analytics. No API key required.

[![Build](https://github.com/teyfikoz/aeronavx/actions/workflows/publish.yml/badge.svg)](https://github.com/teyfikoz/aeronavx/actions/workflows/publish.yml)
[![PyPI version](https://badge.fury.io/py/aeronavx.svg)](https://pypi.org/project/aeronavx/)
[![CI](https://github.com/teyfikoz/AeroNavX/actions/workflows/ci.yml/badge.svg)](https://github.com/teyfikoz/AeroNavX/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install aeronavx
```

Full extras (pandas, fuzzy search, timezone, weather):

```bash
pip install "aeronavx[full]"
```

## Quick Start

```python
import aeronavx

# Look up airports by IATA or ICAO code
ist = aeronavx.get_airport("IST")   # Istanbul Airport
jfk = aeronavx.get_airport("JFK")  # John F. Kennedy

print(ist.name)        # Istanbul Airport
print(ist.country)     # Turkey
print(ist.latitude)    # 41.275278
print(ist.longitude)   # 28.751944

# Distance between two airports
dist = aeronavx.distance_km("IST", "JFK")
print(f"{dist:.0f} km")  # 9,390 km

# Estimate flight time and CO2
hours = aeronavx.estimate_flight_time("IST", "JFK")
co2   = aeronavx.estimate_co2_kg_for_segment("IST", "JFK")
print(f"Flight time: {hours:.1f}h | CO2: {co2:.0f} kg/pax")
```

---

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **84,000+ Airports** | OurAirports dataset — IATA, ICAO, coordinates, type, country |
| **Distance** | Haversine, Vincenty, Spherical Law of Cosines — km, mi, nmi |
| **Geodesy** | Bearing, midpoint, great-circle waypoints |
| **Search** | Fuzzy name search, nearest N airports, radius search |
| **Routing** | Multi-segment routes, flight time estimation |
| **Emissions** | CO2 kg per passenger per segment |
| **Runways** | Runway database — length, surface, longest, paved |
| **Weather** | Live METAR and TAF data (no key needed) |
| **Statistics** | Country, continent, global airport analytics |
| **CLI** | `aeronavx IST JFK` command-line interface |

---

## Airport Lookup

```python
import aeronavx

# By IATA (3-letter)
ath = aeronavx.get_by_iata("ATH")   # Athens International

# By ICAO (4-letter)
ltba = aeronavx.get_by_icao("LTBA")  # Istanbul Ataturk (historical)

# Fuzzy name search
results = aeronavx.search_airports_by_name("heathrow")
for ap in results:
    print(f"{ap.iata_code:4s} {ap.name}")
# LHR  Heathrow Airport
# ...

# Airport object attributes
print(ist.iata_code)     # IST
print(ist.icao_code)     # LTFM
print(ist.elevation_ft)  # 325
print(ist.type)          # large_airport
print(ist.continent)     # EU
```

---

## Distance Calculations

```python
import aeronavx

# All distance units
km   = aeronavx.distance_km("IST", "SYD")
mi   = aeronavx.distance_mi("IST", "SYD")
nmi  = aeronavx.distance_nmi("IST", "SYD")

print(f"{km:.0f} km / {mi:.0f} mi / {nmi:.0f} nmi")
# 14,356 km / 8,922 mi / 7,751 nmi

# From Airport object
ist = aeronavx.get_airport("IST")
jfk = aeronavx.get_airport("JFK")
print(f"{ist.distance_to(jfk):.0f} km")  # 9,390 km

# Also: distance() returns km by default
d = aeronavx.distance("CDG", "NRT")
```

---

## Geodesy — Bearing, Midpoint, Path

```python
import aeronavx

# Initial bearing (true north = 0°)
bearing = aeronavx.initial_bearing("IST", "JFK")
print(f"Heading: {bearing:.1f}°")  # e.g. 318.4° (NNW)

# Geographic midpoint
mid = aeronavx.midpoint("IST", "JFK")
print(f"Midpoint: {mid[0]:.2f}°N {mid[1]:.2f}°W")

# Great-circle waypoints (n equally-spaced points)
waypoints = aeronavx.great_circle_path("IST", "JFK", n=5)
for lat, lon in waypoints:
    print(f"  {lat:.2f}, {lon:.2f}")
```

---

## Nearest Airport Search

```python
import aeronavx

# Single nearest airport to a coordinate
nearest = aeronavx.nearest_airport(lat=41.0, lon=29.0)
print(nearest.iata_code, nearest.name)

# N nearest airports
top5 = aeronavx.nearest_airports(lat=51.5, lon=-0.1, n=5)
for ap in top5:
    print(f"{ap.iata_code:4s}  {ap.name}")
# LHR   Heathrow Airport
# LGW   Gatwick Airport
# ...

# All airports within radius
nearby = aeronavx.airports_within_radius(lat=41.0, lon=29.0, radius_km=100)
print(f"Found {len(nearby)} airports within 100 km of Istanbul")
```

---

## Multi-Segment Routing

```python
import aeronavx

# Total route distance
legs = ["JFK", "LHR", "DXB", "SIN", "SYD"]
total_km = aeronavx.route_distance(legs)
print(f"Round-the-world: {total_km:.0f} km")  # ~19,000 km

# Estimate flight time (assumes ~850 km/h + 45 min overhead per stop)
hours = aeronavx.estimate_flight_time("IST", "NRT")
print(f"IST → NRT: ~{hours:.1f} hours")
```

---

## CO2 Emissions

```python
import aeronavx

# CO2 per passenger (economy class, ICAO methodology)
co2 = aeronavx.estimate_co2_kg_for_segment("LHR", "JFK")
print(f"LHR → JFK: {co2:.0f} kg CO2/pax")  # ~420 kg

# Compare routes
for dest in ["CDG", "DXB", "SIN", "NRT", "JFK"]:
    kg = aeronavx.estimate_co2_kg_for_segment("IST", dest)
    print(f"IST → {dest}: {kg:.0f} kg")
```

---

## Runway Data

```python
import aeronavx

# All runways for an airport
runways = aeronavx.get_runways_by_airport("LTFM")   # Istanbul Airport ICAO
for rwy in runways:
    print(f"Runway {rwy.le_ident}/{rwy.he_ident}: {rwy.length_ft:,} ft, {rwy.surface}")

# Longest runway
longest = aeronavx.get_longest_runway("LTFM")
print(f"Longest: {longest.length_ft:,} ft ({longest.length_ft * 0.3048:.0f} m)")

# Only paved runways
paved = aeronavx.get_paved_runways("KJFK")
print(f"JFK paved runways: {len(paved)}")
```

---

## Live Weather (METAR / TAF)

```python
import aeronavx

# Current METAR (no API key needed — Aviation Weather Center)
metar = aeronavx.get_metar("LTFM")
print(metar)
# LTFM 240550Z 32012KT 9999 FEW030 BKN080 14/06 Q1018 NOSIG

# TAF (terminal aerodrome forecast)
taf = aeronavx.get_taf("EGLL")
print(taf)
# TAF EGLL 240458Z 2406/2512 26010KT 9999 BKN020 ...
```

---

## Airport Statistics

```python
import aeronavx

# Country statistics
turkey = aeronavx.get_country_stats("TR")
print(f"Turkey: {turkey['total']} airports, {turkey['large']} large")

# Continent statistics
eu_stats = aeronavx.get_continent_stats("EU")
print(eu_stats)

# Global overview
global_stats = aeronavx.get_global_stats()
print(f"Total airports in database: {global_stats['total']:,}")  # 84,000+

# Top 10 countries by airport count
top_countries = aeronavx.get_top_countries_by_airports(n=10)
for country, count in top_countries:
    print(f"  {country}: {count:,}")

# Top countries by large airports only
top_large = aeronavx.get_top_countries_by_large_airports(n=5)
```

---

## Command-Line Interface

```bash
# Distance between two airports
aeronavx distance IST JFK

# Airport info
aeronavx info LHR

# Nearest airports to coordinates
aeronavx nearest 41.0 29.0 --n 5

# Current weather
aeronavx metar LTFM

# Route distance
aeronavx route JFK LHR DXB SIN SYD
```

---

## REST API (Optional)

```bash
pip install "aeronavx[api]"
uvicorn aeronavx.api.main:app --reload
```

```
GET /airports/{iata_or_icao}       → Airport details
GET /distance?from=IST&to=JFK      → Distance in km/mi/nmi
GET /nearest?lat=41.0&lon=29.0&n=5 → Nearest airports
GET /weather/metar/{icao}           → Live METAR
GET /stats/global                   → Global statistics
```

---

## Data Source

Airport data: [OurAirports](https://ourairports.com) — MIT License, 84,000+ airports worldwide updated regularly.

---

## License

MIT — [Teyfik Öz](https://github.com/teyfikoz)
