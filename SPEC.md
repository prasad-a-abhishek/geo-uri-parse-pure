# geo-uri-parse-pure — Specification (cycle 142)

## Problem & Scientific Friction Point

HTTP APIs, QR codes, QRPC specifications, and geospatial web services frequently encode WGS-84 coordinates in the `geo:` URI scheme (RFC 5870). Python's standard library (`urllib.parse`) recognizes the `geo` scheme but produces a raw `SplitResult` with no structured parsing — it does **not** validate coordinate bounds, resolve the optional `crs` (coordinate reference system) parameter, parse the optional `u` (uncertainty) parameter, or extract individual latitude/longitude/altitude components. This forces developers to write brittle manual string-splitting code that is easily upset by real-world `geo:` URIs found in BIP 21 QR codes, KML files, and QRPC `latlon` annotations. A zero-dependency pure-Python RFC 5870 `geo:` URI parser is not available on PyPI.

## Novelty Proof & Non-Existence Evidence

- **Python Stdlib Audit**: Verified NOT in standard library (`urllib.parse` only returns a `SplitResult` — it does not validate latitude/longitude bounds, parse parameters, or resolve WGS-84 semantics).
- **PyPI Functional Search**: Checked `geo-uri`, `geo-parse`, `geo-parser`, `rfc5870`; verified no existing pure-Python package implements RFC 5870 parsing.
- **GitHub Topic Search**: `gh search repos "geo-uri-parser language:python"` returned no high-star pure-Python implementations.
- **Primary Scientific Need Citation**: RFC 5870 (IETF Standards Track, June 2010) — the canonical `geo:` URI specification used in BIP 21 QR codes, QRPC, and W3C GeoURI.
- **Automated Gate Output**:
```
============================================================
NOVELTY & NON-EXISTENCE AUDIT: geo-uri-parse-pure (RFC 5870 geo URI parser)
============================================================
1. Python Stdlib Check:   [PASS] No Python standard library collision.
2. Local Repo Check:       [PASS] No local project collision.
3. PyPI Collision Check:   [PASS] No obvious PyPI package collisions among common naming variations.
4. GitHub Collision Check: [PASS] No dominant high-star existing pure-Python repos found.
------------------------------------------------------------
FINAL VERDICT: APPROVED
============================================================
```

## Core Mathematics & Canonical Reference

**RFC 5870 `geo:` URI Grammar (ABNF, RFC 5234)**:
```
geo-URI       = geo-scheme ":" geo-path
geo-scheme    = "geo"
geo-path      = coordinates p
coordinates   = coord-a "," coord-b [ "," coord-c ]
coord-a       = num          ; latitude
coord-b       = num          ; longitude
coord-c       = num          ; altitude (optional)
p             = [ crsp ] [ uncp ] *parameter
crsp          = ";crs=" crslabel
crslabel      = "wgs84" / labeltext
uncp          = ";u=" uval
uval          = pnum
parameter     = ";" pname [ "=" pvalue ]
labeltext     = 1*( alphanum / "-" )
pnum          = 1*DIGIT [ "." 1*DIGIT ]
num           = [ "-" ] pnum
```

**Coordinate Bounds (WGS-84, RFC 5870 §3.4.2)**:
- Latitude (`coord-a`): −90.0 ≤ lat ≤ +90.0
- Longitude (`coord-b`): −180.0 ≤ lon ≤ +180.0
- Altitude (`coord-c`): unrestricted (real number, metres above WGS-84 ellipsoid)

**Reference**: Mayrhofer & Spanring, *"A Uniform Resource Identifier for Geographic Locations ('geo' URI)"*, RFC 5870, IETF, June 2010.

## Public API & Test Plan

```python
# Core API
from geo_uri_parse_pure import parse, GeoURI

# Basic parse — returns structured GeoURI namedtuple
uri = parse("geo:51.5008,-0.1247;crs=wgs84;u=10")
assert uri.lat == 51.5008
assert uri.lon == -0.1247
assert uri.alt is None
assert uri.crs == "wgs84"
assert uri.uncertainty == 10.0

# 3D with altitude
uri3d = parse("geo:37.38605,-122.08385,10.5")
assert uri3d.lat == 37.38605
assert uri3d.lon == -122.08385
assert uri3d.alt == 10.5

# Invalid bounds — raises ValueError
try:
    parse("geo:91.0,0.0")   # lat > 90 → ValueError
except ValueError as e:
    assert "latitude" in str(e)

# CLI smoke
# $ geo-uri-parse "geo:51.5008,-0.1247;u=2"
# lat=51.5008 lon=-0.1247 alt=None crs=wgs84 uncertainty=2.0
```

**Acceptance Criteria (numbered)**:
1. `parse("geo:0,0")` returns `GeoURI(lat=0.0, lon=0.0, alt=None, crs="wgs84", uncertainty=None, params={})`
2. `parse("geo:90,-180")` returns valid bounds, `parse("geo:90.1,0")` raises `ValueError`
3. `parse("geo:-90,180)")` returns valid bounds, `parse("geo:0,180.1)")` raises `ValueError`
4. `parse("geo:0,0,0")` returns `alt=0.0`
5. `parse("geo:0,0;crs=unknown-crs")` returns `crs="unknown-crs"` (unknown CRS preserved)
6. `parse("geo:0,0;u=5.5")` returns `uncertainty=5.5`
7. `parse("geo:0,0;foo=bar;baz=qux")` returns `params={"foo":"bar","baz":"qux"}`
8. `parse("not-geo:0,0")` raises `ValueError`
9. `parse("")` raises `ValueError`
10. CLI `geo-uri-parse "geo:1,2"` exits 0 and prints lat/lon
11. `format()` round-trips `parse(format(parse(x))) == parse(x)` for all valid inputs
12. `parse` is total — `None`, empty string, malformed input never raises uncaught `TypeError`/`AttributeError`

## Mandatory Rule
MUST be 100% zero-dependency in Python standard library (`dependencies = []`).

## Why Not Existing Solutions

- `urllib.parse.urlparse("geo:...")` returns a bare `SplitResult` with zero coordinate validation, no WGS-84 bound checking, and no parameter extraction (`crs`, `u`, custom params).
- No package on PyPI implements RFC 5870 ABNF grammar validation, coordinate bound checking, and structured field extraction in pure Python.

## Target User
Python developers building geospatial HTTP APIs, QR-code processors, QRPC clients, and BIP 21 QR-code parsers who need zero-compile zero-dependency `geo:` URI parsing in serverless (AWS Lambda), WebAssembly (Pyodide), or air-gapped environments.
