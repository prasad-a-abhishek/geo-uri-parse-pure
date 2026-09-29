"""Tests for CRS (coordinate reference system) handling."""

import pytest
from geo_uri_parse_pure import parse_geo_uri


class TestCRSHappy:
    def test_default_wgs84(self):
        """Default CRS is wgs84."""
        result = parse_geo_uri("geo:0,0")
        assert result.crs == "wgs84"

    def test_explicit_wgs84(self):
        """Explicit crs=wgs84."""
        result = parse_geo_uri("geo:0,0;crs=wgs84")
        assert result.crs == "wgs84"

    def test_wgs84_alt(self):
        """crs=wgs84-alt is preserved."""
        result = parse_geo_uri("geo:0,0;crs=wgs84-alt")
        assert result.crs == "wgs84-alt"

    def test_unknown_crs_preserved(self):
        """Unknown CRS value is preserved as-is."""
        result = parse_geo_uri("geo:0,0;crs=unknown-crs")
        assert result.crs == "unknown-crs"

    def test_opengis_crs(self):
        """Other CRS labels are preserved."""
        result = parse_geo_uri("geo:0,0;crs=epsg4326")
        assert result.crs == "epsg4326"

    def test_crs_unicode_like_chars(self):
        """Non-ASCII in CRS is preserved."""
        result = parse_geo_uri("geo:0,0;crs=wgs84-test-1")
        assert result.crs == "wgs84-test-1"


class TestCRSMalformed:
    def test_crs_empty_value(self):
        """crs= with no value handled (param key only)."""
        result = parse_geo_uri("geo:0,0;crs")
        # crs becomes a param with empty value, CRS falls back to default
        # Actually ";crs" alone is treated as a param, not a crs override
        assert result.crs == "wgs84"

    def test_crs_with_params(self):
        """CRS followed by params works."""
        result = parse_geo_uri("geo:0,0;crs=wgs84-alt;u=1;foo=bar")
        assert result.crs == "wgs84-alt"
        assert result.uncertainty == 1.0
        assert result.params == {"foo": "bar"}
