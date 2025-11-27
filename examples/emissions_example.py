import aeronavx
from aeronavx.core.emissions import estimate_co2_kg_for_segment

ist = aeronavx.get_airport("IST")
lhr = aeronavx.get_airport("LHR")

if ist and lhr:
    print(f"Route: {ist.name} ({ist.iata_code}) → {lhr.name} ({lhr.iata_code})\n")

    dist_km = ist.distance_to(lhr)
    print(f"Distance: {dist_km:.2f} km")

    co2_kg = estimate_co2_kg_for_segment(ist, lhr)
    print(f"Estimated CO2 emissions: {co2_kg:.2f} kg per passenger")

    print("\nComparison:")
    print(f"  Short-haul factor (0.15 kg/km): {dist_km * 0.15:.2f} kg")
    print(f"  Default factor (0.115 kg/km): {co2_kg:.2f} kg")
    print(f"  Long-haul factor (0.09 kg/km): {dist_km * 0.09:.2f} kg")
else:
    print("Airports not found")
