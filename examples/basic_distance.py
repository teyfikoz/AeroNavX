import aeronavx

ist = aeronavx.get_airport("IST")
jfk = aeronavx.get_airport("JFK")

if ist and jfk:
    print(f"Origin: {ist.name} ({ist.iata_code})")
    print(f"Destination: {jfk.name} ({jfk.iata_code})")
    print()

    dist_km = ist.distance_to(jfk, model="haversine")
    dist_mi = aeronavx.distance_mi(
        ist.latitude_deg, ist.longitude_deg,
        jfk.latitude_deg, jfk.longitude_deg
    )
    dist_nmi = aeronavx.distance(
        ist.latitude_deg, ist.longitude_deg,
        jfk.latitude_deg, jfk.longitude_deg,
        unit="nmi"
    )

    print(f"Distance (km): {dist_km:.2f}")
    print(f"Distance (mi): {dist_mi:.2f}")
    print(f"Distance (nmi): {dist_nmi:.2f}")

    bearing = ist.bearing_to(jfk)
    print(f"\nInitial bearing: {bearing:.2f}°")
else:
    print("Airports not found")
