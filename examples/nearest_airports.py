import aeronavx

lat, lon = 41.0, 29.0

print(f"Finding nearest airports to ({lat}, {lon})\n")

nearest = aeronavx.nearest_airport(lat, lon, n=5)

for i, airport in enumerate(nearest, 1):
    dist_km = aeronavx.distance_km(lat, lon, airport.latitude_deg, airport.longitude_deg)

    codes = []
    if airport.iata_code:
        codes.append(f"IATA: {airport.iata_code}")
    if airport.gps_code:
        codes.append(f"ICAO: {airport.gps_code}")

    print(f"{i}. {airport.name}")
    print(f"   Codes: {', '.join(codes)}")
    print(f"   Distance: {dist_km:.2f} km")
    print(f"   Location: {airport.municipality}, {airport.iso_country}")
    print()
