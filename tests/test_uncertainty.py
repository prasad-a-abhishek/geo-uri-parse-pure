"""Tests for uncertainty (u) parameter parsing."""

import pytest
from geo_uri_parse_pure import parse_geo_uri


class TestUncertaintyHappy:
    def test_u_positive_float(self):
        result = parse_geo_uri("geo:0,0;u=5.5")
        assert result.uncertainty == 5.5

    def test_u_zero(self):
        result = parse_geo_uri("geo:0,0;u=0")
        assert result.uncertainty == 0.0

    def test_u_integer(self):
        result = parse_geo_uri("geo:0,0;u=100")
        assert result.uncertainty == 100.0

    def test_u_small_float(self):
        result = parse_geo_uri("geo:0,0;u=0.001")
        assert result.uncertainty == 0.001

    def test_u_large_float(self):
        result = parse_geo_uri("geo:0,0;u=99999.9")
        assert result.uncertainty == 99999.9

    def test_u_absent(self):
        result = parse_geo_uri("geo:0,0")
        assert result.uncertainty is None

    def test_u_with_crs(self):
        result = parse_geo_uri("geo:0,0;u=10;crs=wgs84")
        assert result.uncertainty == 10.0
        assert result.crs == "wgs84"

    def test_u_with_altitude(self):
        result = parse_geo_uri("geo:0,0,100;u=5")
        assert result.uncertainty == 5.0
        assert result.alt == 100.0


class TestUncertaintyInvalid:
    def test_u_negative_raises(self):
        with pytest.raises(ValueError, match="uncertainty must be non-negative"):
            parse_geo_uri("geo:0,0;u=-5")

    def test_u_nan_raises(self):
        with pytest.raises(ValueError, match="must not be NaN"):
            parse_geo_uri("geo:0,0;u=nan")

    def test_u_inf_raises(self):
        with pytest.raises(ValueError, match="must not be infinite"):
            parse_geo_uri("geo:0,0;u=inf")

    def test_u_leading_zeros(self):
        """Leading zeros are fine."""
        result = parse_geo_uri("geo:0,0;u=007")
        assert result.uncertainty == 7.0
