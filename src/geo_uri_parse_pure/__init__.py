"""geo-uri-parse-pure: Zero-dependency pure-Python RFC 5870 geo: URI parser.

Usage:
    from geo_uri_parse_pure import parse_geo_uri, GeoURI

    uri = parse_geo_uri("geo:51.5008,-0.1247;crs=wgs84;u=10")
    print(uri.lat, uri.lon, uri.alt, uri.crs, uri.uncertainty)
"""

from __future__ import annotations

__version__ = "0.1.0"

from ._parser import GeoURI, parse_geo_uri

__all__ = ["parse_geo_uri", "GeoURI", "__version__"]
