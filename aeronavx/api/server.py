from fastapi import FastAPI, HTTPException, Query
from ..core.airports import get
from ..core.distance import distance
from ..core.search import nearest_airports, search_airports_by_name
from ..core.routing import estimate_flight_time_hours
from ..core.emissions import estimate_co2_kg_by_codes
from ..core.passenger_experience import calculate_jet_lag
from ..core.network_intelligence import identify_global_hubs
from ..core.emissions_advanced import calculate_flight_emissions, compare_saf_savings, AircraftType, FuelType
from ..core.synthetic_routes import generate_route
from ..exceptions import AeroNavXError


app = FastAPI(
    title="AeroNavX API",
    description="AI aviation SDK API",
    version="3.0.0"
)


_semantic_engine = None


def _get_semantic_engine():
    global _semantic_engine
    if _semantic_engine is None:
        try:
            from ..hf.semantic_search import SemanticAirportSearch
        except ImportError as exc:
            raise HTTPException(
                status_code=501,
                detail="Semantic search requires the HF extra. Install with `pip install aeronavx[hf]`."
            ) from exc
        from ..core.loader import get_all_airports
        _semantic_engine = SemanticAirportSearch(get_all_airports())
    return _semantic_engine


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AeroNavX API"}


@app.get("/airport/{code}")
async def get_airport(
    code: str,
    code_type: str = Query("auto", regex="^(iata|icao|auto)$")
):
    try:
        airport = get(code, code_type=code_type)

        if airport is None:
            raise HTTPException(status_code=404, detail=f"Airport not found: {code}")

        return airport.as_dict()

    except AeroNavXError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/distance")
async def calculate_distance(
    from_code: str = Query(..., alias="from"),
    to_code: str = Query(..., alias="to"),
    code_type: str = Query("auto", regex="^(iata|icao|auto)$"),
    model: str = Query("haversine", regex="^(haversine|slc|vincenty)$"),
    unit: str = Query("km", regex="^(km|mi|nmi)$")
):
    try:
        from_airport = get(from_code, code_type=code_type)
        to_airport = get(to_code, code_type=code_type)

        if from_airport is None:
            raise HTTPException(status_code=404, detail=f"Origin airport not found: {from_code}")

        if to_airport is None:
            raise HTTPException(status_code=404, detail=f"Destination airport not found: {to_code}")

        dist = distance(
            from_airport.latitude_deg,
            from_airport.longitude_deg,
            to_airport.latitude_deg,
            to_airport.longitude_deg,
            model=model,
            unit=unit
        )

        return {
            "from": from_airport.as_dict(),
            "to": to_airport.as_dict(),
            "distance": dist,
            "unit": unit,
            "model": model
        }

    except AeroNavXError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/nearest")
async def find_nearest(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    n: int = Query(5, ge=1, le=100)
):
    try:
        airports = nearest_airports(lat, lon, n=n)

        return {
            "query": {"lat": lat, "lon": lon},
            "count": len(airports),
            "airports": [a.as_dict() for a in airports]
        }

    except AeroNavXError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        airports = search_airports_by_name(q, limit=limit)

        return {
            "query": q,
            "count": len(airports),
            "airports": [a.as_dict() for a in airports]
        }

    except AeroNavXError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/flight-time")
async def flight_time(
    from_code: str = Query(..., alias="from"),
    to_code: str = Query(..., alias="to"),
    speed_kts: float = Query(450.0, ge=100, le=1000)
):
    try:
        from_airport = get(from_code, code_type="auto")
        to_airport = get(to_code, code_type="auto")

        if from_airport is None:
            raise HTTPException(status_code=404, detail=f"Origin airport not found: {from_code}")

        if to_airport is None:
            raise HTTPException(status_code=404, detail=f"Destination airport not found: {to_code}")

        time_hours = estimate_flight_time_hours(from_airport, to_airport, speed_kts=speed_kts)

        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)

        return {
            "from": from_airport.as_dict(),
            "to": to_airport.as_dict(),
            "speed_kts": speed_kts,
            "time_hours": time_hours,
            "time_formatted": f"{hours}h {minutes}m"
        }

    except AeroNavXError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/emissions")
async def emissions(
    from_code: str = Query(..., alias="from"),
    to_code: str = Query(..., alias="to"),
    model: str = Query("haversine", regex="^(haversine|slc|vincenty)$")
):
    try:
        co2_kg = estimate_co2_kg_by_codes(from_code, to_code, code_type="auto", model=model)

        from_airport = get(from_code, code_type="auto")
        to_airport = get(to_code, code_type="auto")

        return {
            "from": from_airport.as_dict(),
            "to": to_airport.as_dict(),
            "co2_kg_per_passenger": co2_kg,
            "model": model
        }

    except AeroNavXError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/semantic-search")
async def semantic_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=50),
):
    try:
        engine = _get_semantic_engine()
        results = engine.search(q, top_k=top_k, return_format="list")
        return {"query": q, "count": len(results), "results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/jet-lag")
async def jet_lag(
    from_code: str = Query(..., alias="from"),
    to_code: str = Query(..., alias="to"),
    age: int = Query(30, ge=1, le=120),
):
    try:
        origin = get(from_code, code_type="auto")
        destination = get(to_code, code_type="auto")

        if origin is None or destination is None:
            raise HTTPException(status_code=404, detail="Airport not found")

        result = calculate_jet_lag(origin, destination, age=age)
        return {
            "from": origin.as_dict(),
            "to": destination.as_dict(),
            "timezone_difference_hours": result.timezone_difference_hours,
            "direction": result.direction.value,
            "severity": result.severity.value,
            "estimated_recovery_days": result.estimated_recovery_days,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/hubs")
async def hubs(
    top_n: int = Query(10, ge=1, le=50),
    include_unscheduled: bool = Query(False),
):
    try:
        results = identify_global_hubs(top_n=top_n, scheduled_service_only=not include_unscheduled)
        return {
            "count": len(results),
            "hubs": [
                {
                    "airport": hub.airport.as_dict(),
                    "hub_score": hub.hub_score,
                    "connectivity_score": hub.connectivity_score,
                    "type_score": hub.type_score,
                }
                for hub in results
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/emissions-advanced")
async def emissions_advanced(
    from_code: str = Query(..., alias="from"),
    to_code: str = Query(..., alias="to"),
    aircraft_type: str = Query("narrow_body"),
    fuel_type: str = Query("jet_a1"),
    load_factor: float = Query(0.85, ge=0.1, le=1.0),
    saf_percent: float = Query(0.0, ge=0.0, le=100.0),
):
    try:
        emissions = calculate_flight_emissions(
            from_code,
            to_code,
            aircraft_type=AircraftType(aircraft_type),
            fuel_type=FuelType(fuel_type),
            load_factor=load_factor,
            code_type="auto",
        )
        response = {
            "from": from_code,
            "to": to_code,
            "distance_km": emissions.distance_km,
            "fuel_kg": emissions.fuel_kg,
            "total_co2_kg": emissions.total_co2_kg,
            "co2_per_passenger_kg": emissions.co2_per_passenger_kg,
            "aircraft_type": emissions.aircraft_type.value,
            "fuel_type": emissions.fuel_type.value,
            "load_factor": emissions.load_factor,
        }
        if saf_percent > 0:
            savings = compare_saf_savings(
                from_code,
                to_code,
                saf_percentage=saf_percent,
                aircraft_type=AircraftType(aircraft_type),
                load_factor=load_factor,
                code_type="auto",
            )
            response["saf"] = {
                "base_co2_kg": savings.base_co2_kg,
                "saf_co2_kg": savings.saf_co2_kg,
                "co2_reduction_kg": savings.co2_reduction_kg,
                "reduction_percentage": savings.reduction_percentage,
            }
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/synthetic-route")
async def synthetic_route(
    from_code: str = Query(..., alias="from"),
    to_code: str = Query(..., alias="to"),
    waypoints: int = Query(12, ge=0, le=100),
    speed_kts: float = Query(450.0, ge=100, le=1000),
):
    try:
        route = generate_route(
            from_code,
            to_code,
            num_waypoints=waypoints,
            speed_kts=speed_kts,
        )
        return {
            "from": route.origin.as_dict(),
            "to": route.destination.as_dict(),
            "total_distance_km": route.total_distance_km,
            "total_time_hours": route.total_time_hours,
            "waypoints": [
                {
                    "name": wp.name,
                    "latitude": wp.latitude,
                    "longitude": wp.longitude,
                    "distance_from_origin_km": wp.distance_from_origin_km,
                }
                for wp in route.waypoints
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def run_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
