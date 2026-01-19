import aeronavx
from aeronavx.core.routing import estimate_flight_time_h_m, route_distance

codes = ["IST", "AMS", "JFK"]

airports = []
for code in codes:
    airport = aeronavx.get_airport(code)
    if airport:
        airports.append(airport)

if len(airports) == len(codes):
    print("Multi-segment route:")
    for airport in airports:
        print(f"  → {airport.name} ({airport.iata_code})")

    print()

    total_dist = route_distance(airports, model="haversine", unit="km")
    print(f"Total distance: {total_dist:.2f} km")

    print("\nSegment details:")
    for i in range(len(airports) - 1):
        from_airport = airports[i]
        to_airport = airports[i + 1]

        dist_km = from_airport.distance_to(to_airport)
        hours, minutes = estimate_flight_time_h_m(from_airport, to_airport)

        message = (
            f"{from_airport.iata_code} → {to_airport.iata_code}: "
            f"{dist_km:.2f} km, ~{hours}h {minutes}m"
        )
        print(message)
else:
    print("One or more airports not found")
