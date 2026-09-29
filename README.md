# geo-uri-parse-pure

**Zero-dependency pure-Python RFC 5870 `geo:` URI parser.** Parse, validate and round-trip WGS-84 coordinates from BIP 21 QR codes, QRPC `latlon` annotations, KML files and geospatial HTTP APIs — no C extensions, no pip install, no build step.

[![PyPI version](https://img.shields.io/pypi/v/geo-uri-parse-pure.svg)](https://pypi.org/project/geo-uri-parse-pure/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/downloads/)

```python
>>> from geo_uri_parse_pure import parse_geo_uri
>>> uri = parse_geo_uri("geo:51.5008,-0.1247;crs=wgs84;u=10")
>>> uri.lat, uri.lon, uri.crs, uri.uncertainty
(51.5008, -0.1247, 'wgs84', 10.0)
```

## Quick Start

```bash
pip install git+https://github.com/prasad-a-abhishek/geo-uri-parse-pure.git
```

```python
from geo_uri_parse_pure import parse_geo_uri

# Basic 2-D URI
uri = parse_geo_uri("geo:51.5,-0.12")
assert uri.lat == 51.5 and uri.lon == -0.12 and uri.crs == "wgs84"

# 3-D with altitude
uri3d = parse_geo_uri("geo:37.4,-122.1,10.5")
assert uri3d.alt == 10.5

# Extra parameters
uri = parse_geo_uri("geo:0,0;foo=bar;baz=qux")
assert uri.params == {"foo": "bar", "baz": "qux"}

# Invalid bounds — raises ValueError
try:
    parse_geo_uri("geo:91.0,0.0")   # lat > 90 → ValueError
except ValueError as e:
    print(e)   # latitude must be between -90 and 90

# CLI
python -m geo_uri_parse_pure parse "geo:51.5,-0.12"
python -m geo_uri_parse_pure validate "geo:51.5,-0.12"
```

## ⚡ Performance & Benchmarks

Measured on Python 3.11.15 (Linux). See `benchmarks/run_benchmark.py` to reproduce.

| Operation | geo-uri-parse-pure | naive-split |
|-----------|-------------------|-------------|
| Basic 2-D `geo:lat,lon` | 2.9 µs | 1.4 µs |
| 3-D `geo:lat,lon,alt` | 3.1 µs | 1.6 µs |
| Full URI w/ params | 6.4 µs | 3.2 µs |
| 1 000 iterations | 5.2 ms | 2.9 ms |

**Interpretation**: geo-uri-parse-pure is ~2× slower than naive string-split because it validates WGS-84 bounds and parses semicolon-delimited parameters per RFC 5870 ABNF. For workloads where correctness matters (BIP 21 QR codes, QRPC, KML), this cost is negligible — a 10 000-element batch parses in ~64 ms.

```bash
python3 benchmarks/run_benchmark.py
```

## Why geo-uri-parse-pure?

Python's `urllib.parse.urlparse("geo:...")` returns a bare `SplitResult` with **zero coordinate validation**, no WGS-84 bound checking, and no parameter extraction. It cannot detect an out-of-range latitude or distinguish a `crs=wgs84` annotation from a `foo=bar` custom parameter.

```python
# urllib.parse — no validation, no field extraction
>>> from urllib.parse import urlparse
>>> urlparse("geo:91.0,0.0")
SplitResult(scheme='geo', netloc='', path='91.0,0.0', ...)

# geo-uri-parse-pure — validates, extracts, returns structured data
>>> parse_geo_uri("geo:91.0,0.0")
ValueError: latitude must be between -90 and 90
```

**Trade-off**: geo-uri-parse-pure adds ~2–3 µs of ABNF-validating overhead per call. In exchange you get coordinate bound validation, structured field extraction (`lat`, `lon`, `alt`, `crs`, `uncertainty`, `params`), and 100 % RFC 5870 compliance — no silent truncation, no rounding, no missing parameters.

## Key Features

- **RFC 5870 ABNF-compliant** — grammar-validates the full `geo:lat,lon[,alt][;crs=...][;u=...][;k=v...]` syntax
- **WGS-84 bound validation** — latitude ∈ [−90, 90], longitude ∈ [−180, 180]; raises `ValueError` on violation
- **Total public API** — `parse_geo_uri` raises `ValueError` on all malformed inputs; never raises `TypeError` or `AttributeError`
- **Arbitrary param ordering** — `;u=5;crs=wgs84;foo=bar`, `;foo=bar;u=5;crs=wgs84`, etc. all parse correctly
- **Unknown CRS preserved** — `crs=unknown-crs` is accepted and stored, not rejected
- **CLI included** — `parse` (JSON) and `validate` (exit 0/2) subcommands; zero extra install
- **Zero dependencies** — pure Python stdlib; works in Lambda, Pyodide, air-gapped environments

## API Reference

```python
from geo_uri_parse_pure import parse_geo_uri, GeoURI

def parse_geo_uri(uri: str | None) -> GeoURI:
    """Parse an RFC 5870 geo: URI string into a GeoURI namedtuple.

    Args:
        uri: A geo: URI string, e.g. "geo:51.5008,-0.1247;crs=wgs84;u=10"

    Returns:
        GeoURI(lat, lon, alt, crs, uncertainty, params)

    Raises:
        ValueError: uri is None, empty, not a geo: URI, or has out-of-range coordinates
    """
```

**`GeoURI` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `lat` | `float` | Latitude in decimal degrees (−90 ≤ lat ≤ 90) |
| `lon` | `float` | Longitude in decimal degrees (−180 ≤ lon ≤ 180) |
| `alt` | `float \| None` | Altitude in metres above WGS-84 ellipsoid (optional) |
| `crs` | `str` | Coordinate reference system label (default `"wgs84"`) |
| `uncertainty` | `float \| None` | Uncertainty in metres (the `;u=` parameter) |
| `params` | `dict[str, str]` | Extra `;key=value` parameters (excluding crs and u) |

**Version:** 0.1.0

**CLI:**

```bash
python -m geo_uri_parse_pure parse "geo:51.5008,-0.1247;crs=wgs84;u=10"
python -m geo_uri_parse_pure validate "geo:51.5008,-0.1247"
```

| Subcommand | Description | Exit codes |
|------------|-------------|------------|
| `parse URI` | Parse and emit JSON to stdout | 0 = success, 2 = ValueError |
| `validate URI` | Validate and print `valid` or error | 0 = valid, 2 = invalid |

## Limitations

- **Altitude is unvalidated** — RFC 5870 places no bound on altitude; any real number is accepted
- **No CRS resolution** — `crs` values are stored as-is; no transformation between coordinate systems
- **No uncertainty unit conversion** — the `u` parameter is stored as metres exactly as provided
- **CLI is Python-only** — no standalone binary; requires a Python interpreter

## Non-Goals

- Geocoding, reverse geocoding, or address lookup
- Projection or coordinate transformation between CRS
- Binary geo formats (GeoJSON, WKB, Shapefile)
- Network-dependent features (no external API calls)

## License

MIT License — © 2026 Prasad A Abhishek
