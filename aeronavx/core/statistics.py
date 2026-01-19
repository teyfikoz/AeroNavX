"""Statistical analysis for airports and runways."""

from collections import Counter
from dataclasses import dataclass
from typing import Optional

from . import loader
from . import runways as runway_loader


@dataclass
class CountryStats:
    """Statistics for a specific country."""

    iso_country: str
    total_airports: int
    large_airports: int
    medium_airports: int
    small_airports: int
    heliports: int
    airports_with_iata: int
    scheduled_service_count: int
    total_runways: int
    longest_runway_ft: Optional[float]
    avg_runway_length_ft: Optional[float]

    def as_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "iso_country": self.iso_country,
            "total_airports": self.total_airports,
            "large_airports": self.large_airports,
            "medium_airports": self.medium_airports,
            "small_airports": self.small_airports,
            "heliports": self.heliports,
            "airports_with_iata": self.airports_with_iata,
            "scheduled_service_count": self.scheduled_service_count,
            "total_runways": self.total_runways,
            "longest_runway_ft": self.longest_runway_ft,
            "avg_runway_length_ft": self.avg_runway_length_ft,
        }


@dataclass
class ContinentStats:
    """Statistics for a continent."""

    continent: str
    total_airports: int
    countries_count: int
    large_airports: int
    medium_airports: int
    small_airports: int
    total_runways: int
    airports_with_scheduled_service: int

    def as_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "continent": self.continent,
            "total_airports": self.total_airports,
            "countries_count": self.countries_count,
            "large_airports": self.large_airports,
            "medium_airports": self.medium_airports,
            "small_airports": self.small_airports,
            "total_runways": self.total_runways,
            "airports_with_scheduled_service": self.airports_with_scheduled_service,
        }


@dataclass
class GlobalStats:
    """Global aviation statistics."""

    total_airports: int
    total_runways: int
    countries_count: int
    continents_count: int
    large_airports: int
    medium_airports: int
    small_airports: int
    heliports: int
    seaplane_bases: int
    closed_airports: int
    airports_with_iata: int
    airports_with_scheduled_service: int
    total_runway_length_miles: float
    avg_runway_length_ft: float
    longest_runway_ft: float
    shortest_runway_ft: float

    def as_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_airports": self.total_airports,
            "total_runways": self.total_runways,
            "countries_count": self.countries_count,
            "continents_count": self.continents_count,
            "large_airports": self.large_airports,
            "medium_airports": self.medium_airports,
            "small_airports": self.small_airports,
            "heliports": self.heliports,
            "seaplane_bases": self.seaplane_bases,
            "closed_airports": self.closed_airports,
            "airports_with_iata": self.airports_with_iata,
            "airports_with_scheduled_service": self.airports_with_scheduled_service,
            "total_runway_length_miles": self.total_runway_length_miles,
            "avg_runway_length_ft": self.avg_runway_length_ft,
            "longest_runway_ft": self.longest_runway_ft,
            "shortest_runway_ft": self.shortest_runway_ft,
        }


def get_country_stats(iso_country: str) -> Optional[CountryStats]:
    """
    Get statistics for a specific country.

    Args:
        iso_country: ISO country code (e.g., 'US', 'GB', 'TR')

    Returns:
        CountryStats object or None if country not found

    Example:
        >>> stats = get_country_stats('US')
        >>> print(f"US has {stats.total_airports:,} airports")
        US has 20,345 airports
        >>> print(f"Large airports: {stats.large_airports}")
        Large airports: 543
    """
    airports = loader.load_airports()
    runways = runway_loader.load_runways()

    country_airports = [a for a in airports if a.iso_country == iso_country.upper()]
    if not country_airports:
        return None

    # Count by type
    type_counter = Counter(a.type for a in country_airports)

    # Count IATA codes
    iata_count = sum(1 for a in country_airports if a.iata_code)

    # Count scheduled service
    scheduled_count = sum(1 for a in country_airports if a.scheduled_service)

    # Get country's runways
    country_idents = {a.ident for a in country_airports}
    country_runways = [r for r in runways if r.airport_ident in country_idents]

    # Runway statistics
    runway_lengths = [r.length_ft for r in country_runways if r.length_ft]
    longest_runway = max(runway_lengths) if runway_lengths else None
    avg_runway = sum(runway_lengths) / len(runway_lengths) if runway_lengths else None

    return CountryStats(
        iso_country=iso_country.upper(),
        total_airports=len(country_airports),
        large_airports=type_counter.get("large_airport", 0),
        medium_airports=type_counter.get("medium_airport", 0),
        small_airports=type_counter.get("small_airport", 0),
        heliports=type_counter.get("heliport", 0),
        airports_with_iata=iata_count,
        scheduled_service_count=scheduled_count,
        total_runways=len(country_runways),
        longest_runway_ft=longest_runway,
        avg_runway_length_ft=avg_runway,
    )


def get_continent_stats(continent: str) -> Optional[ContinentStats]:
    """
    Get statistics for a continent.

    Args:
        continent: Continent code (e.g., 'NA', 'EU', 'AS', 'AF', 'OC', 'SA', 'AN')

    Returns:
        ContinentStats object or None if continent not found

    Example:
        >>> stats = get_continent_stats('EU')
        >>> print(f"Europe has {stats.total_airports:,} airports")
        Europe has 15,234 airports
    """
    airports = loader.load_airports()
    runways = runway_loader.load_runways()

    continent_airports = [a for a in airports if a.continent == continent.upper()]
    if not continent_airports:
        return None

    # Count countries
    countries = {a.iso_country for a in continent_airports if a.iso_country}

    # Count by type
    type_counter = Counter(a.type for a in continent_airports)

    # Count scheduled service
    scheduled_count = sum(1 for a in continent_airports if a.scheduled_service)

    # Get continent's runways
    continent_idents = {a.ident for a in continent_airports}
    continent_runways = [r for r in runways if r.airport_ident in continent_idents]

    return ContinentStats(
        continent=continent.upper(),
        total_airports=len(continent_airports),
        countries_count=len(countries),
        large_airports=type_counter.get("large_airport", 0),
        medium_airports=type_counter.get("medium_airport", 0),
        small_airports=type_counter.get("small_airport", 0),
        total_runways=len(continent_runways),
        airports_with_scheduled_service=scheduled_count,
    )


def get_global_stats() -> GlobalStats:
    """
    Get global aviation statistics.

    Returns:
        GlobalStats object with worldwide statistics

    Example:
        >>> stats = get_global_stats()
        >>> print(f"Total airports: {stats.total_airports:,}")
        Total airports: 84,225
        >>> print(f"Total runways: {stats.total_runways:,}")
        Total runways: 47,372
    """
    airports = loader.load_airports()
    runways = runway_loader.load_runways()

    # Count by type
    type_counter = Counter(a.type for a in airports)

    # Count countries and continents
    countries = {a.iso_country for a in airports if a.iso_country}
    continents = {a.continent for a in airports if a.continent}

    # Count closed airports
    closed_count = sum(1 for a in airports if a.type == "closed")

    # Count IATA codes
    iata_count = sum(1 for a in airports if a.iata_code)

    # Count scheduled service
    scheduled_count = sum(1 for a in airports if a.scheduled_service)

    # Runway statistics
    runway_lengths = [r.length_ft for r in runways if r.length_ft]
    total_length_miles = sum(runway_lengths) / 5280 if runway_lengths else 0
    avg_runway = sum(runway_lengths) / len(runway_lengths) if runway_lengths else 0
    longest_runway = max(runway_lengths) if runway_lengths else 0
    shortest_runway = min(runway_lengths) if runway_lengths else 0

    return GlobalStats(
        total_airports=len(airports),
        total_runways=len(runways),
        countries_count=len(countries),
        continents_count=len(continents),
        large_airports=type_counter.get("large_airport", 0),
        medium_airports=type_counter.get("medium_airport", 0),
        small_airports=type_counter.get("small_airport", 0),
        heliports=type_counter.get("heliport", 0),
        seaplane_bases=type_counter.get("seaplane_base", 0),
        closed_airports=closed_count,
        airports_with_iata=iata_count,
        airports_with_scheduled_service=scheduled_count,
        total_runway_length_miles=total_length_miles,
        avg_runway_length_ft=avg_runway,
        longest_runway_ft=longest_runway,
        shortest_runway_ft=shortest_runway,
    )


def get_top_countries_by_airports(n: int = 10) -> list[tuple[str, int]]:
    """
    Get top N countries by number of airports.

    Args:
        n: Number of countries to return (default: 10)

    Returns:
        List of (country_code, airport_count) tuples

    Example:
        >>> top = get_top_countries_by_airports(5)
        >>> for country, count in top:
        ...     print(f"{country}: {count:,} airports")
        US: 20,345 airports
        BR: 4,093 airports
        CA: 1,853 airports
    """
    airports = loader.load_airports()
    country_counter = Counter(a.iso_country for a in airports if a.iso_country)
    return country_counter.most_common(n)


def get_top_countries_by_large_airports(n: int = 10) -> list[tuple[str, int]]:
    """
    Get top N countries by number of large airports.

    Args:
        n: Number of countries to return (default: 10)

    Returns:
        List of (country_code, large_airport_count) tuples

    Example:
        >>> top = get_top_countries_by_large_airports(5)
        >>> for country, count in top:
        ...     print(f"{country}: {count} large airports")
        US: 543 large airports
        CN: 234 large airports
    """
    airports = loader.load_airports()
    large_airports = [a for a in airports if a.type == "large_airport"]
    country_counter = Counter(a.iso_country for a in large_airports if a.iso_country)
    return country_counter.most_common(n)
