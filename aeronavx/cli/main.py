import argparse
import sys

from .. import __version__
from ..core.airports import get
from ..core.distance import distance
from ..core.search import nearest_airports, search_airports_by_name
from ..core.emissions import estimate_co2_kg_by_codes
from ..core.emissions_advanced import calculate_flight_emissions, compare_saf_savings, AircraftType, FuelType
from ..core.passenger_experience import calculate_jet_lag
from ..core.network_intelligence import identify_global_hubs
from ..core.synthetic_routes import generate_route
from ..core.routing import estimate_flight_time_hours
from ..exceptions import AeroNavXError


def cmd_distance(args):
    try:
        from_airport = get(args.from_code, code_type="auto")
        to_airport = get(args.to_code, code_type="auto")

        if from_airport is None:
            print(f"Error: Airport not found: {args.from_code}", file=sys.stderr)
            return 1

        if to_airport is None:
            print(f"Error: Airport not found: {args.to_code}", file=sys.stderr)
            return 1

        dist = distance(
            from_airport.latitude_deg,
            from_airport.longitude_deg,
            to_airport.latitude_deg,
            to_airport.longitude_deg,
            model=args.model,
            unit=args.unit
        )

        print(f"{from_airport.name} ({args.from_code}) to {to_airport.name} ({args.to_code})")
        print(f"Distance: {dist:.2f} {args.unit}")

        return 0

    except AeroNavXError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_nearest(args):
    try:
        airports = nearest_airports(args.lat, args.lon, n=args.n)

        if not airports:
            print("No airports found")
            return 0

        print(f"Nearest {len(airports)} airport(s) to ({args.lat}, {args.lon}):\n")

        for i, airport in enumerate(airports, 1):
            codes = []
            if airport.iata_code:
                codes.append(f"IATA: {airport.iata_code}")
            if airport.gps_code:
                codes.append(f"ICAO: {airport.gps_code}")

            code_str = f" ({', '.join(codes)})" if codes else ""

            dist_km = distance(
                args.lat, args.lon,
                airport.latitude_deg, airport.longitude_deg,
                unit="km"
            )

            print(f"{i}. {airport.name}{code_str}")
            print(f"   Distance: {dist_km:.2f} km")
            print(f"   Location: {airport.municipality}, {airport.iso_country}")
            print()

        return 0

    except AeroNavXError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_search(args):
    try:
        airports = search_airports_by_name(args.name, limit=args.limit)

        if not airports:
            print(f"No airports found matching '{args.name}'")
            return 0

        print(f"Found {len(airports)} airport(s) matching '{args.name}':\n")

        for i, airport in enumerate(airports, 1):
            codes = []
            if airport.iata_code:
                codes.append(f"IATA: {airport.iata_code}")
            if airport.gps_code:
                codes.append(f"ICAO: {airport.gps_code}")

            code_str = f" ({', '.join(codes)})" if codes else ""

            print(f"{i}. {airport.name}{code_str}")
            print(f"   Type: {airport.type}")
            print(f"   Location: {airport.municipality}, {airport.iso_country}")
            print()

        return 0

    except AeroNavXError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_emissions(args):
    try:
        co2_kg = estimate_co2_kg_by_codes(
            args.from_code,
            args.to_code,
            code_type="auto",
            model=args.model
        )

        from_airport = get(args.from_code, code_type="auto")
        to_airport = get(args.to_code, code_type="auto")

        print(f"{from_airport.name} ({args.from_code}) to {to_airport.name} ({args.to_code})")
        print(f"Estimated CO2 emissions: {co2_kg:.2f} kg per passenger")

        return 0

    except AeroNavXError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_flight_time(args):
    try:
        from_airport = get(args.from_code, code_type="auto")
        to_airport = get(args.to_code, code_type="auto")

        if from_airport is None:
            print(f"Error: Airport not found: {args.from_code}", file=sys.stderr)
            return 1

        if to_airport is None:
            print(f"Error: Airport not found: {args.to_code}", file=sys.stderr)
            return 1

        time_hours = estimate_flight_time_hours(
            from_airport,
            to_airport,
            speed_kts=args.speed_kts
        )

        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)

        print(f"{from_airport.name} ({args.from_code}) to {to_airport.name} ({args.to_code})")
        print(f"Estimated flight time: {hours}h {minutes}m (at {args.speed_kts} knots)")

        return 0

    except AeroNavXError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_semantic_search(args):
    try:
        from .. import semantic_search

        results = semantic_search(args.query, top_k=args.top_k, return_format="list")

        if not results:
            print("No results found")
            return 0

        print(f"Semantic search results for '{args.query}':\n")
        for idx, row in enumerate(results, 1):
            code = row.get("iata") or row.get("icao") or "---"
            name = row.get("name") or "Unknown"
            score = row.get("score", 0.0)
            print(f"{idx}. {code} - {name} (score={score:.3f})")

        return 0
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_jet_lag(args):
    try:
        origin = get(args.from_code, code_type="auto")
        destination = get(args.to_code, code_type="auto")

        if origin is None or destination is None:
            print("Error: Airport not found", file=sys.stderr)
            return 1

        result = calculate_jet_lag(origin, destination, age=args.age)

        print(f"{origin.name} ({args.from_code}) -> {destination.name} ({args.to_code})")
        print(f"Timezone difference: {result.timezone_difference_hours:.1f} hours")
        print(f"Direction: {result.direction.value}")
        print(f"Severity: {result.severity.value}")
        print(f"Estimated recovery: {result.estimated_recovery_days:.1f} days")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_hubs(args):
    try:
        hubs = identify_global_hubs(
            top_n=args.top_n,
            scheduled_service_only=not args.include_unscheduled
        )

        print(f"Top {len(hubs)} hubs:")
        for hub in hubs:
            print(f"{hub.airport.iata_code or '---'} - {hub.airport.name}")
            print(f"  Hub Score: {hub.hub_score:.2f}")
            print(f"  Connectivity: {hub.connectivity_score:.2f}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_emissions_advanced(args):
    try:
        aircraft = AircraftType(args.aircraft_type)
        fuel = FuelType(args.fuel_type)

        emissions = calculate_flight_emissions(
            args.from_code,
            args.to_code,
            aircraft_type=aircraft,
            fuel_type=fuel,
            load_factor=args.load_factor,
            code_type="auto",
        )

        print(f"Route: {args.from_code} -> {args.to_code}")
        print(f"Distance: {emissions.distance_km:.1f} km")
        print(f"Fuel: {emissions.fuel_kg:.1f} kg")
        print(f"Total CO2: {emissions.total_co2_kg:.1f} kg")
        print(f"Per passenger: {emissions.co2_per_passenger_kg:.2f} kg")

        if args.saf_percent > 0:
            savings = compare_saf_savings(
                args.from_code,
                args.to_code,
                saf_percentage=args.saf_percent,
                aircraft_type=aircraft,
                load_factor=args.load_factor,
                code_type="auto",
            )
            print(
                f"SAF {args.saf_percent:.0f}% reduction: "
                f"{savings.co2_reduction_kg:.1f} kg ({savings.reduction_percentage:.1f}%)"
            )

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_synthetic_route(args):
    try:
        route = generate_route(
            args.from_code,
            args.to_code,
            num_waypoints=args.waypoints,
            speed_kts=args.speed_kts,
        )

        print(f"Route: {route.origin.name} -> {route.destination.name}")
        print(f"Total distance: {route.total_distance_km:.1f} km")
        print(f"Estimated time: {route.total_time_hours:.2f} hours")
        print(f"Waypoints: {len(route.waypoints)}")

        preview = route.waypoints[: min(5, len(route.waypoints))]
        for wp in preview:
            print(f"  {wp.name}: ({wp.latitude:.2f}, {wp.longitude:.2f})")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        prog="aeronavx",
        description="AeroNavX - AI aviation SDK CLI"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"aeronavx {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    distance_parser = subparsers.add_parser("distance", help="Calculate distance between airports")
    distance_parser.add_argument("--from", dest="from_code", required=True, help="Origin airport code")
    distance_parser.add_argument("--to", dest="to_code", required=True, help="Destination airport code")
    distance_parser.add_argument("--unit", choices=["km", "mi", "nmi"], default="km", help="Distance unit")
    distance_parser.add_argument("--model", choices=["haversine", "slc", "vincenty"], default="haversine", help="Distance model")

    nearest_parser = subparsers.add_parser("nearest", help="Find nearest airports to coordinates")
    nearest_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    nearest_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    nearest_parser.add_argument("--n", type=int, default=5, help="Number of airports to return")

    search_parser = subparsers.add_parser("search", help="Search airports by name")
    search_parser.add_argument("--name", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum results")

    emissions_parser = subparsers.add_parser("emissions", help="Estimate CO2 emissions")
    emissions_parser.add_argument("--from", dest="from_code", required=True, help="Origin airport code")
    emissions_parser.add_argument("--to", dest="to_code", required=True, help="Destination airport code")
    emissions_parser.add_argument("--model", choices=["haversine", "slc", "vincenty"], default="haversine", help="Distance model")

    emissions_adv_parser = subparsers.add_parser("emissions-advanced", help="Advanced emissions model")
    emissions_adv_parser.add_argument("--from", dest="from_code", required=True, help="Origin airport code")
    emissions_adv_parser.add_argument("--to", dest="to_code", required=True, help="Destination airport code")
    emissions_adv_parser.add_argument(
        "--aircraft-type",
        default="narrow_body",
        choices=[t.value for t in AircraftType],
        help="Aircraft category",
    )
    emissions_adv_parser.add_argument(
        "--fuel-type",
        default="jet_a1",
        choices=[t.value for t in FuelType],
        help="Fuel type",
    )
    emissions_adv_parser.add_argument("--load-factor", type=float, default=0.85, help="Load factor (0-1)")
    emissions_adv_parser.add_argument("--saf-percent", type=float, default=0.0, help="SAF blend percentage")

    time_parser = subparsers.add_parser("flight-time", help="Estimate flight time")
    time_parser.add_argument("--from", dest="from_code", required=True, help="Origin airport code")
    time_parser.add_argument("--to", dest="to_code", required=True, help="Destination airport code")
    time_parser.add_argument("--speed-kts", type=float, default=450.0, help="Cruise speed in knots")

    semantic_parser = subparsers.add_parser("semantic-search", help="AI semantic airport search")
    semantic_parser.add_argument("--query", required=True, help="Search query")
    semantic_parser.add_argument("--top-k", type=int, default=5, help="Number of results")

    jet_lag_parser = subparsers.add_parser("jet-lag", help="Jet lag analysis")
    jet_lag_parser.add_argument("--from", dest="from_code", required=True, help="Origin airport code")
    jet_lag_parser.add_argument("--to", dest="to_code", required=True, help="Destination airport code")
    jet_lag_parser.add_argument("--age", type=int, default=30, help="Passenger age")

    hubs_parser = subparsers.add_parser("hubs", help="Identify global hubs")
    hubs_parser.add_argument("--top-n", type=int, default=10, help="Number of hubs")
    hubs_parser.add_argument(
        "--include-unscheduled",
        action="store_true",
        help="Include airports without scheduled service",
    )

    route_parser = subparsers.add_parser("synthetic-route", help="Generate synthetic route")
    route_parser.add_argument("--from", dest="from_code", required=True, help="Origin airport code")
    route_parser.add_argument("--to", dest="to_code", required=True, help="Destination airport code")
    route_parser.add_argument("--waypoints", type=int, default=12, help="Number of waypoints")
    route_parser.add_argument("--speed-kts", type=float, default=450.0, help="Cruise speed in knots")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "distance":
        return cmd_distance(args)
    elif args.command == "nearest":
        return cmd_nearest(args)
    elif args.command == "search":
        return cmd_search(args)
    elif args.command == "emissions":
        return cmd_emissions(args)
    elif args.command == "emissions-advanced":
        return cmd_emissions_advanced(args)
    elif args.command == "flight-time":
        return cmd_flight_time(args)
    elif args.command == "semantic-search":
        return cmd_semantic_search(args)
    elif args.command == "jet-lag":
        return cmd_jet_lag(args)
    elif args.command == "hubs":
        return cmd_hubs(args)
    elif args.command == "synthetic-route":
        return cmd_synthetic_route(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
