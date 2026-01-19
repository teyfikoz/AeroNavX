from aeronavx.core import loader


def test_load_airports_reapplies_filters(tmp_path):
    csv_content = "\n".join([
        "id,ident,type,name,latitude_deg,longitude_deg,elevation_ft,continent,iso_country,iso_region,municipality,scheduled_service,gps_code,iata_code,local_code,home_link,wikipedia_link,keywords",
        "1,AAA1,large_airport,Alpha Airport,0.0,0.0,0,NA,XX,XX-1,Alpha City,yes,AAA1,AAA,,,,",
        "2,BBB1,small_airport,Beta Airport,1.0,1.0,0,NA,XX,XX-1,Beta City,no,BBB1,BBB,,,,",
    ])
    csv_path = tmp_path / "airports.csv"
    csv_path.write_text(csv_content)

    loader.load_airports(data_path=csv_path, force_reload=True)

    filtered = loader.load_airports(data_path=csv_path, include_types=["large_airport"])

    assert len(filtered) == 1
    assert filtered[0].iata_code == "AAA"

    loader.clear_cache()
