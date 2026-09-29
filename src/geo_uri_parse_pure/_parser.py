"""RFC 5870 geo: URI parser — grammar implementation."""

from __future__ import annotations

import re
from typing import NamedTuple

from ._validate import (
    validate_altitude,
    validate_latitude,
    validate_longitude,
    validate_uncertainty,
)

__all__ = ["parse_geo_uri", "GeoURI"]


class GeoURI(NamedTuple):
    """Parsed geo: URI components.

    Attributes:
        lat:        WGS-84 latitude (−90 to +90)
        lon:        WGS-84 longitude (−180 to +180)
        alt:        altitude in metres above WGS-84 ellipsoid, or None
        crs:        coordinate reference system label (default "wgs84")
        uncertainty: uncertainty in metres, or None
        params:     extra query-style parameters as dict
    """

    lat: float
    lon: float
    alt: float | None
    crs: str
    uncertainty: float | None
    params: dict[str, str]


# RFC 5870 §3.4.2: coordinate reference systems
_SUPPORTED_CRS = frozenset({"wgs84", "wgs84-alt"})

# Regex components
_PNUM = r"[0-9]+(?:[.][0-9]+)?"           # pnum: digits, optional decimal
_NUM = r"[+-]?[0-9]+(?:[.][0-9]+)?"        # num: optional sign + pnum

# geo-URI pattern (after stripping "geo:" prefix):
#   lat,lon[,alt] | rest-of-string
# The rest is parsed iteratively to handle arbitrary param ordering.
_GEO_RE = re.compile(
    r"^"
    r"(?P<lat>" + _NUM + r")"
    r","
    r"(?P<lon>" + _NUM + r")"
    r"(?:,(?P<alt>" + _NUM + r"))?"
    r"(?P<rest>.*)"
    r"$"
)


def parse_geo_uri(uri: str | None) -> GeoURI:
    """Parse an RFC 5870 geo: URI string into a GeoURI namedtuple.

    Args:
        uri: A geo: URI string, e.g. "geo:51.5008,-0.1247;crs=wgs84;u=10"

    Returns:
        GeoURI(lat, lon, alt, crs, uncertainty, params)

    Raises:
        ValueError: if uri is None/empty, has wrong scheme, or contains
            out-of-bounds coordinates / invalid numeric values.

    This function is TOTAL: it never raises uncaught TypeError or
    AttributeError — malformed inputs raise ValueError instead.
    """
    if uri is None or uri == "":
        raise ValueError("geo: URI must not be empty or None")

    if not isinstance(uri, str):
        raise ValueError(
            f"geo: URI must be a string, got {type(uri).__name__}"
        )

    # Strip surrounding whitespace
    uri = uri.strip()

    # Enforce geo: scheme
    if not uri.lower().startswith("geo:"):
        raise ValueError(
            f"not a geo: URI (only 'geo:' scheme is supported): {uri!r}"
        )

    # Remove the "geo:" prefix for parsing
    raw = uri[4:]  # len("geo:") == 4
    if not raw:
        raise ValueError("geo: URI has no coordinate data")

    # Run the main regex
    m = _GEO_RE.match(raw)
    if m is None:
        raise ValueError(f"geo: URI does not conform to RFC 5870 ABNF: {uri!r}")

    # Extract lat, lon, optional altitude (captured by regex), and remaining string
    lat_str = m.group("lat")
    lon_str = m.group("lon")
    alt_str = m.group("alt")  # may be None — regex already extracted it
    rest = m.group("rest")  # everything after lat,lon[,alt] — params start here

    # Validate lat/lon (these raise ValueError on bad input)
    lat = validate_latitude(lat_str)
    lon = validate_longitude(lon_str)

    # Altitude: regex already extracted it; validate if present
    alt = validate_altitude(alt_str)

    # Parse remaining semicolon-delimited params in any order:
    #   ;crs=... | ;u=... | ;key[=value]
    crs: str = "wgs84"
    uncertainty: float | None = None
    params: dict[str, str] = {}

    if rest:
        for param_match in re.finditer(
            r";(?P<key>[a-zA-Z][a-zA-Z0-9_-]*)(?:=(?P<val>[^;]*))?", rest
        ):
            key = param_match.group("key")
            val = param_match.group("val") or ""
            if key == "crs" and val:
                crs = val
            elif key == "u":
                uncertainty = validate_uncertainty(val)
            else:
                if key not in params:
                    params[key] = val

    return GeoURI(
        lat=lat,
        lon=lon,
        alt=alt,
        crs=crs,
        uncertainty=uncertainty,
        params=params,
    )
