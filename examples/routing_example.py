import aeronavx
from aeronavx.core.routing import route_distance, estimate_flight_time_h_m

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

        print(f"{from_airport.iata_code} → {to_airport.iata_code}: {dist_km:.2f} km, ~{hours}h {minutes}m")
else:
    print("One or more airports not found")
