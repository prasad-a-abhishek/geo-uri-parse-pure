"""Tests for geo-uri-parse-pure validation helpers (RFC 5870 bounds)."""

import pytest
from geo_uri_parse_pure._validate import (
    validate_altitude,
    validate_latitude,
    validate_longitude,
    validate_num,
    validate_uncertainty,
)


# ---------------------------------------------------------------------------
# validate_num
# ---------------------------------------------------------------------------

class TestValidateNumHappy:
    def test_positive_integer(self):
        assert validate_num("42", "x") == 42.0

    def test_negative_integer(self):
        assert validate_num("-42", "x") == -42.0

    def test_positive_float(self):
        assert validate_num("3.14159", "x") == pytest.approx(3.14159)

    def test_negative_float(self):
        assert validate_num("-273.15", "x") == pytest.approx(-273.15)

    def test_leading_plus_sign(self):
        assert validate_num("+10.5", "x") == 10.5

    def test_integer_no_decimal(self):
        assert validate_num("0", "x") == 0.0

    def test_scientific_notation_like(self):
        # RFC 5870 doesn't require scientific notation support but
        # float() accepts it; validate_num should pass it through
        assert validate_num("1e2", "x") == 100.0


class TestValidateNumEdgeCases:
    def test_none_raises(self):
        with pytest.raises(ValueError, match="must not be None"):
            validate_num(None, "lat")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            validate_num("", "lon")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            validate_num(42, "lat")  # type: ignore

        with pytest.raises(ValueError, match="must be a string"):
            validate_num(b"1.0", "lat")  # type: ignore

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="must not be NaN"):
            validate_num("nan", "lat")

    def test_inf_raises(self):
        with pytest.raises(ValueError, match="must not be infinite"):
            validate_num("inf", "lon")

    def test_minus_inf_raises(self):
        with pytest.raises(ValueError, match="must not be infinite"):
            validate_num("-inf", "lon")

    def test_garbage_string_raises(self):
        with pytest.raises(ValueError, match="is not a valid number"):
            validate_num("hello", "lat")

    def test_leading_zeros_in_value(self):
        """Leading zeros in numeric values are accepted."""
        # Leading zeros are technically allowed (stripped by float())
        assert validate_num("007", "x") == 7.0
        assert validate_num("01.5", "x") == 1.5

    def test_plus_only_no_digits_raises(self):
        with pytest.raises(ValueError, match="is not a valid number"):
            validate_num("+", "lat")


# ---------------------------------------------------------------------------
# validate_latitude
# ---------------------------------------------------------------------------

class TestLatitudeHappy:
    def test_zero(self):
        assert validate_latitude("0") == 0.0

    def test_positive_boundary(self):
        assert validate_latitude("90") == 90.0

    def test_negative_boundary(self):
        assert validate_latitude("-90") == -90.0

    def test_mid_positive(self):
        assert validate_latitude("51.5008") == 51.5008

    def test_mid_negative(self):
        assert validate_latitude("-33.8688") == -33.8688

    def test_minus_zero(self):
        assert validate_latitude("-0.0") == -0.0


class TestLatitudeBoundary:
    def test_just_over_90_raises(self):
        with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
            validate_latitude("90.0001")

    def test_just_under_minus_90_raises(self):
        with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
            validate_latitude("-90.0001")

    def test_way_over_90_raises(self):
        with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
            validate_latitude("180")

    def test_way_under_minus_90_raises(self):
        with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
            validate_latitude("-180")


class TestLatitudeMalformed:
    def test_none_raises(self):
        with pytest.raises(ValueError, match="latitude must not be None"):
            validate_latitude(None)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="latitude must not be empty"):
            validate_latitude("")

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="must not be NaN"):
            validate_latitude("nan")

    def test_inf_raises(self):
        with pytest.raises(ValueError, match="must not be infinite"):
            validate_latitude("inf")


# ---------------------------------------------------------------------------
# validate_longitude
# ---------------------------------------------------------------------------

class TestLongitudeHappy:
    def test_zero(self):
        assert validate_longitude("0") == 0.0

    def test_positive_180(self):
        assert validate_longitude("180") == 180.0

    def test_negative_180(self):
        assert validate_longitude("-180") == -180.0

    def test_mid_positive(self):
        assert validate_longitude("122.399677") == 122.399677

    def test_mid_negative(self):
        assert validate_longitude("-0.1247") == -0.1247


class TestLongitudeBoundary:
    def test_just_over_180_raises(self):
        with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
            validate_longitude("180.0001")

    def test_just_under_minus_180_raises(self):
        with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
            validate_longitude("-180.0001")

    def test_way_over_180_raises(self):
        with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
            validate_longitude("360")

    def test_way_under_minus_180_raises(self):
        with pytest.raises(ValueError, match="longitude out of WGS-84 bounds"):
            validate_longitude("-360")


class TestLongitudeMalformed:
    def test_none_raises(self):
        with pytest.raises(ValueError, match="longitude must not be None"):
            validate_longitude(None)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="longitude must not be empty"):
            validate_longitude("")

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="must not be NaN"):
            validate_longitude("nan")


# ---------------------------------------------------------------------------
# validate_altitude
# ---------------------------------------------------------------------------

class TestAltitudeHappy:
    def test_zero(self):
        assert validate_altitude("0") == 0.0

    def test_positive(self):
        assert validate_altitude("10.5") == 10.5

    def test_negative(self):
        assert validate_altitude("-110.0") == -110.0

    def test_large_positive(self):
        # altitude is unrestricted per RFC 5870
        assert validate_altitude("8848.86") == 8848.86

    def test_large_negative(self):
        # Death Sea level approx
        assert validate_altitude("-430.0") == -430.0


class TestAltitudeOptional:
    def test_none_returns_none(self):
        assert validate_altitude(None) is None

    def test_empty_returns_none(self):
        assert validate_altitude("") is None


class TestAltitudeMalformed:
    def test_nan_raises(self):
        with pytest.raises(ValueError, match="altitude must not be NaN"):
            validate_altitude("nan")

    def test_inf_raises(self):
        with pytest.raises(ValueError, match="altitude must not be infinite"):
            validate_altitude("inf")


# ---------------------------------------------------------------------------
# validate_uncertainty
# ---------------------------------------------------------------------------

class TestUncertaintyHappy:
    def test_zero(self):
        assert validate_uncertainty("0") == 0.0

    def test_positive_float(self):
        assert validate_uncertainty("10.5") == 10.5

    def test_positive_integer(self):
        assert validate_uncertainty("100") == 100.0

    def test_small_positive(self):
        assert validate_uncertainty("0.001") == 0.001


class TestUncertaintyOptional:
    def test_none_returns_none(self):
        assert validate_uncertainty(None) is None

    def test_empty_returns_none(self):
        assert validate_uncertainty("") is None


class TestUncertaintyMalformed:
    def test_negative_raises(self):
        with pytest.raises(ValueError, match="uncertainty must be non-negative"):
            validate_uncertainty("-5.0")

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="uncertainty must not be NaN"):
            validate_uncertainty("nan")

    def test_inf_raises(self):
        with pytest.raises(ValueError, match="uncertainty must not be infinite"):
            validate_uncertainty("inf")
