"""Tests for geo-uri-parse-pure core parser (RFC 5870 ABNF)."""

import pytest
from geo_uri_parse_pure import parse_geo_uri, GeoURI


# ---------------------------------------------------------------------------
# AC1: parse("geo:0,0") returns correct GeoURI
# ---------------------------------------------------------------------------

def test_ac1_basic_origin():
    """AC1: geo:0,0 returns wgs84 default."""
    result = parse_geo_uri("geo:0,0")
    assert isinstance(result, GeoURI)
    assert result.lat == 0.0
    assert result.lon == 0.0
    assert result.alt is None
    assert result.crs == "wgs84"
    assert result.uncertainty is None
    assert result.params == {}


def test_ac1_various_zero_forms():
    """AC1: 0.0, -0.0, 0, -0 all valid zero."""
    for uri in ["geo:0,0", "geo:0.0,0.0", "geo:-0,-0", "geo:0.0,-0.0"]:
        result = parse_geo_uri(uri)
        assert result.lat == 0.0
        assert result.lon == 0.0


# ---------------------------------------------------------------------------
# AC2: latitude boundary
# ---------------------------------------------------------------------------

def test_ac2_lat_max_valid():
    """AC2: 90 is valid latitude."""
    result = parse_geo_uri("geo:90,0")
    assert result.lat == 90.0


def test_ac2_lat_min_valid():
    """AC2: -90 is valid latitude."""
    result = parse_geo_uri("geo:-90,0")
    assert result.lat == -90.0


def test_ac2_lat_just_over_raises():
    """AC2: 90.1 raises ValueError."""
    with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
        parse_geo_uri("geo:90.1,0")


def test_ac2_lat_way_over_raises():
    """AC2: 180 raises ValueError."""
    with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
        parse_geo_uri("geo:180,0")


def test_ac2_lat_just_under_raises():
    """AC2: -90.1 raises ValueError."""
    with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
        parse_geo_uri("geo:-90.1,0")


def test_ac2_lat_way_under_raises():
    """AC2: -180 raises ValueError."""
    with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
        parse_geo_uri("geo:-180,0")


# ---------------------------------------------------------------------------
# AC3: longitude boundary
# ---------------------------------------------------------------------------

def test_ac3_lon_max_valid():
    """AC3: 180 is valid longitude."""
    result = parse_geo_uri("geo:0,180")
    assert result.lon == 180.0


def test_ac3_lon_min_valid():
    """AC3: -180 is valid longitude."""
    result = parse_geo_uri("geo:0,-180")
    assert result.lon == -180.0


def test_ac3_lon_just_over_raises():
    """AC3: 180.1 raises ValueError."""
    with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
        parse_geo_uri("geo:0,180.1")


def test_ac3_lon_just_under_raises():
    """AC3: -180.1 raises ValueError."""
    with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
        parse_geo_uri("geo:0,-180.1")


def test_ac3_lon_way_over_raises():
    """AC3: 360 raises ValueError."""
    with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
        parse_geo_uri("geo:0,360")


# ---------------------------------------------------------------------------
# AC4: altitude
# ---------------------------------------------------------------------------

def test_ac4_altitude_zero():
    """AC4: geo:0,0,0 returns alt=0.0."""
    result = parse_geo_uri("geo:0,0,0")
    assert result.alt == 0.0


def test_ac4_altitude_positive():
    """AC4: positive altitude parsed."""
    result = parse_geo_uri("geo:37.38605,-122.08385,10.5")
    assert result.alt == 10.5


def test_ac4_altitude_negative():
    """AC4: negative altitude (below WGS-84 ellipsoid) is valid."""
    result = parse_geo_uri("geo:0,0,-500")
    assert result.alt == -500.0


def test_ac4_altitude_optional_absent():
    """AC4: no altitude returns None."""
    result = parse_geo_uri("geo:0,0")
    assert result.alt is None


# ---------------------------------------------------------------------------
# AC5: crs unknown preserved
# ---------------------------------------------------------------------------

def test_ac5_unknown_crs_preserved():
    """AC5: unknown crs is preserved as-is."""
    result = parse_geo_uri("geo:0,0;crs=unknown-crs")
    assert result.crs == "unknown-crs"


def test_ac5_wgs84_default():
    """AC5: default crs is wgs84."""
    result = parse_geo_uri("geo:0,0")
    assert result.crs == "wgs84"


def test_ac5_wgs84_explicit():
    """AC5: explicit crs=wgs84 is preserved."""
    result = parse_geo_uri("geo:0,0;crs=wgs84")
    assert result.crs == "wgs84"


def test_ac5_wgs84_alt():
    """AC5: crs=wgs84-alt is preserved."""
    result = parse_geo_uri("geo:0,0;crs=wgs84-alt")
    assert result.crs == "wgs84-alt"


# ---------------------------------------------------------------------------
# AC6: uncertainty
# ---------------------------------------------------------------------------

def test_ac6_uncertainty_positive():
    """AC6: positive uncertainty parsed."""
    result = parse_geo_uri("geo:0,0;u=5.5")
    assert result.uncertainty == 5.5


def test_ac6_uncertainty_zero():
    """AC6: zero uncertainty is valid."""
    result = parse_geo_uri("geo:0,0;u=0")
    assert result.uncertainty == 0.0


def test_ac6_uncertainty_integer():
    """AC6: integer uncertainty parsed."""
    result = parse_geo_uri("geo:0,0;u=100")
    assert result.uncertainty == 100.0


def test_ac6_uncertainty_optional_absent():
    """AC6: no u param returns None."""
    result = parse_geo_uri("geo:0,0")
    assert result.uncertainty is None


# ---------------------------------------------------------------------------
# AC7: custom params
# ---------------------------------------------------------------------------

def test_ac7_single_param():
    """AC7: single custom param parsed."""
    result = parse_geo_uri("geo:0,0;foo=bar")
    assert result.params == {"foo": "bar"}


def test_ac7_multiple_params():
    """AC7: multiple custom params parsed."""
    result = parse_geo_uri("geo:0,0;foo=bar;baz=qux")
    assert result.params == {"foo": "bar", "baz": "qux"}


def test_ac7_param_no_value():
    """AC7: param with no value = empty string."""
    result = parse_geo_uri("geo:0,0;foo")
    assert result.params == {"foo": ""}


def test_ac7_crs_and_params():
    """AC7: crs and params coexist."""
    result = parse_geo_uri("geo:0,0;crs=wgs84;foo=bar;u=5")
    assert result.crs == "wgs84"
    assert result.params == {"foo": "bar"}


def test_ac7_empty_params():
    """AC7: no params returns empty dict."""
    result = parse_geo_uri("geo:0,0")
    assert result.params == {}


# ---------------------------------------------------------------------------
# AC8: wrong scheme raises
# ---------------------------------------------------------------------------

def test_ac8_wrong_scheme_raises():
    """AC8: non-geo scheme raises ValueError."""
    with pytest.raises(ValueError, match="not a geo: URI"):
        parse_geo_uri("not-geo:0,0")


def test_ac8_http_raises():
    """AC8: http:// raises ValueError."""
    with pytest.raises(ValueError, match="not a geo: URI"):
        parse_geo_uri("http://example.com")


def test_ac8_geo_scheme_only():
    """AC8: geo: without coordinates raises ValueError."""
    with pytest.raises(ValueError):
        parse_geo_uri("geo:")


# ---------------------------------------------------------------------------
# AC9: empty string raises
# ---------------------------------------------------------------------------

def test_ac9_empty_string_raises():
    """AC9: empty string raises ValueError."""
    with pytest.raises(ValueError, match="must not be empty"):
        parse_geo_uri("")


def test_ac9_none_raises():
    """AC9: None raises ValueError (not TypeError)."""
    with pytest.raises(ValueError):
        parse_geo_uri(None)  # type: ignore


# ---------------------------------------------------------------------------
# AC12: total function (never raises TypeError/AttributeError)
# ---------------------------------------------------------------------------

def test_ac12_total_non_string_raises():
    """AC12: non-string raises ValueError not TypeError."""
    with pytest.raises(ValueError, match="must be a string"):
        parse_geo_uri(42)  # type: ignore

    with pytest.raises(ValueError, match="must be a string"):
        parse_geo_uri(b"geo:0,0")  # type: ignore


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------

def test_real_world_bip21_london():
    """BIP 21 geo: URI — London Eye."""
    result = parse_geo_uri("geo:51.5008,-0.1247;crs=wgs84;u=10")
    assert result.lat == 51.5008
    assert result.lon == -0.1247
    assert result.crs == "wgs84"
    assert result.uncertainty == 10.0


def test_whitespace_stripped():
    """Leading/trailing whitespace is stripped."""
    result = parse_geo_uri("  geo:0,0  ")
    assert result.lat == 0.0
    assert result.lon == 0.0


def test_case_insensitive_scheme():
    """Scheme is case-insensitive."""
    result = parse_geo_uri("GEO:0,0")
    assert result.lat == 0.0
    result = parse_geo_uri("Geo:0,0")
    assert result.lat == 0.0


def test_high_precision_coordinates():
    """High precision coordinates parsed correctly."""
    result = parse_geo_uri("geo:37.38605,-122.08385")
    assert result.lat == 37.38605
    assert result.lon == -122.08385


def test_integers_for_lat_lon():
    """Integer lat/lon without decimal point parsed."""
    result = parse_geo_uri("geo:37,-122")
    assert result.lat == 37.0
    assert result.lon == -122.0


def test_param_with_equals_in_value():
    """Param value can contain = character."""
    result = parse_geo_uri("geo:0,0;x=a=b")
    assert result.params == {"x": "a=b"}


def test_crs_before_u():
    """crs before u order works."""
    result = parse_geo_uri("geo:0,0;crs=wgs84;u=5")
    assert result.crs == "wgs84"
    assert result.uncertainty == 5.0


def test_u_before_crs():
    """u before crs order works."""
    result = parse_geo_uri("geo:0,0;u=5;crs=wgs84")
    assert result.uncertainty == 5.0
    assert result.crs == "wgs84"


def test_crs_after_altitude():
    """crs after altitude still works."""
    result = parse_geo_uri("geo:0,0,100;crs=wgs84")
    assert result.alt == 100.0
    assert result.crs == "wgs84"


def test_all_params_combined():
    """All optional parts together."""
    result = parse_geo_uri(
        "geo:51.5008,-0.1247,10.5;crs=wgs84;u=2;foo=bar;baz=qux"
    )
    assert result.lat == 51.5008
    assert result.lon == -0.1247
    assert result.alt == 10.5
    assert result.crs == "wgs84"
    assert result.uncertainty == 2.0
    assert result.params == {"foo": "bar", "baz": "qux"}


def test_underscore_in_param_key():
    """Param keys can contain underscores."""
    result = parse_geo_uri("geo:0,0;foo_bar=baz")
    assert result.params == {"foo_bar": "baz"}


def test_dash_in_param_key():
    """Param keys can contain dashes."""
    result = parse_geo_uri("geo:0,0;foo-bar=baz")
    assert result.params == {"foo-bar": "baz"}


def test_leading_plus_lat():
    """Leading + sign for positive latitude."""
    result = parse_geo_uri("geo:+51.5,-0.12")
    assert result.lat == 51.5


def test_leading_plus_lon():
    """Leading + sign for positive longitude."""
    result = parse_geo_uri("geo:0,+122.0")
    assert result.lon == 122.0
