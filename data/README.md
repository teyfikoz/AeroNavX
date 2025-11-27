# Airport Data

This directory should contain the `airports.csv` file with global airport data.

## Required CSV Format

The CSV file should include the following columns:

- **id**: Numeric airport identifier
- **ident**: Airport identifier code
- **type**: Airport type (e.g., small_airport, medium_airport, large_airport, heliport)
- **name**: Airport name
- **latitude_deg**: Latitude in decimal degrees
- **longitude_deg**: Longitude in decimal degrees
- **elevation_ft**: Elevation in feet (optional)
- **continent**: Two-letter continent code
- **iso_country**: Two-letter ISO country code
- **iso_region**: ISO region code (country-region)
- **municipality**: City/municipality name
- **scheduled_service**: yes/no for scheduled airline service
- **gps_code**: ICAO code (4 letters)
- **iata_code**: IATA code (3 letters, if available)
- **local_code**: Local airport code (optional)
- **home_link**: Airport website URL (optional)
- **wikipedia_link**: Wikipedia URL (optional)
- **keywords**: Comma-separated keywords (optional)

## Data Sources

You can obtain airport data from:
- [OurAirports](https://ourairports.com/data/) - Open data with global coverage
- [OpenFlights](https://openflights.org/data.html) - Airport database

## Example

```csv
id,ident,type,name,latitude_deg,longitude_deg,elevation_ft,continent,iso_country,iso_region,municipality,scheduled_service,gps_code,iata_code,local_code,home_link,wikipedia_link,keywords
1,"AYPY","small_airport","Nadzab Airport",-6.569803,146.725977,239,"OC","PG","PG-MPM","Nadzab","yes","AYPY","LAE",,"","http://en.wikipedia.org/wiki/Nadzab_Airport",
```

## Setup

1. Download the airports.csv file from one of the sources above
2. Place it in this directory: `data/airports.csv`
3. The library will automatically load it when needed
