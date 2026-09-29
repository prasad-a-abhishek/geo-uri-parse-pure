"""Validation helpers for geo: URI components (RFC 5870).

All functions raise ValueError with descriptive messages.
Per Invariant 21: all public APIs are TOTAL — None, empty string,
NaN, Inf, and out-of-range values raise ValueError, never
uncaught TypeError/AttributeError.
"""

from __future__ import annotations

__all__ = [
    "validate_latitude",
    "validate_longitude",
    "validate_altitude",
    "validate_uncertainty",
    "validate_num",
]


def validate_num(value: str | None, name: str) -> float:
    """Parse and validate a numeric string as a finite float.

    Raises ValueError for None, empty, NaN, Inf, or non-numeric.
    """
    if value is None:
        raise ValueError(f"{name} must not be None")
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string, got {type(value).__name__}")
    if not value:
        raise ValueError(f"{name} must not be empty")
    value = value.strip()
    try:
        num = float(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"{name} is not a valid number: {value}") from e
    if num != num:  # NaN check
        raise ValueError(f"{name} must not be NaN: {value}")
    if num == float("inf") or num == float("-inf"):
        raise ValueError(f"{name} must not be infinite: {value}")
    return num


def validate_latitude(lat: str | None) -> float:
    """Parse and validate a latitude string.

    RFC 5870 §3.4.2: −90.0 ≤ lat ≤ +90.0
    Raises ValueError for None, empty, NaN, Inf, or out-of-bounds.
    """
    num = validate_num(lat, "latitude")
    if num < -90.0 or num > 90.0:
        raise ValueError(
            f"latitude out of WGS-84 bounds: {num!r} (must be between -90 and +90)"
        )
    return num


def validate_longitude(lon: str | None) -> float:
    """Parse and validate a longitude string.

    RFC 5870 §3.4.2: −180.0 ≤ lon ≤ +180.0
    Raises ValueError for None, empty, NaN, Inf, or out-of-bounds.
    """
    num = validate_num(lon, "longitude")
    if num < -180.0 or num > 180.0:
        raise ValueError(
            f"longitude out of WGS-84 bounds: {num!r} (must be between -180 and +180)"
        )
    return num


def validate_altitude(alt: str | None) -> float | None:
    """Parse and validate an optional altitude string.

    RFC 5870 §3.4.2: altitude is unrestricted (real number, metres above
    WGS-84 ellipsoid). Returns None for empty/None input.
    Raises ValueError for NaN or Inf.
    """
    if alt is None or alt == "":
        return None
    num = validate_num(alt, "altitude")
    # altitude has no WGS-84 bound restriction per RFC 5870
    return num


def validate_uncertainty(uval: str | None) -> float | None:
    """Parse and validate an optional uncertainty (u) string.

    RFC 5870 §3.4.2: uncertainty is a positive real number.
    Returns None for empty/None input.
    Raises ValueError for NaN, Inf, or negative values.
    """
    if uval is None or uval == "":
        return None
    num = validate_num(uval, "uncertainty")
    if num < 0.0:
        raise ValueError(
            f"uncertainty must be non-negative: {num!r}"
        )
    return num
