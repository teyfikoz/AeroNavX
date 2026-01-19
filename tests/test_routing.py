import pytest

from aeronavx.core import loader
from aeronavx.core.routing import shortest_path
from aeronavx.exceptions import RoutingError


def test_shortest_path_handles_duplicate_names(tmp_path):
    csv_content = "\n".join([
        "id,ident,type,name,latitude_deg,longitude_deg,elevation_ft,continent,iso_country,iso_region,municipality,scheduled_service,gps_code,iata_code,local_code,home_link,wikipedia_link,keywords",
        "1,AAA1,small_airport,SameName,0.0,0.0,0,NA,XX,XX-1,Test City,no,AAA1,AAA,,,,",
        "2,AAA2,small_airport,SameName,0.0,10.0,0,NA,XX,XX-1,Test City,no,AAA2,AAB,,,,",
        "3,BBB1,small_airport,Destination,0.0,15.0,0,NA,XX,XX-1,Test City,no,BBB1,BBB,,,,",
    ])
    csv_path = tmp_path / "airports.csv"
    csv_path.write_text(csv_content)

    loader.load_airports(data_path=csv_path, force_reload=True)

    with pytest.raises(RoutingError):
        shortest_path("AAA", "BBB", code_type="iata", max_leg_km=800)

    loader.clear_cache()


def test_route_distance_by_codes():
    from aeronavx.core.routing import route_distance_by_codes

    dist = route_distance_by_codes(["IST", "JFK"], code_type="iata", unit="km")

    assert dist > 1000
