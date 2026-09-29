"""End-to-end tests with real-world RFC 5870 / BIP 21 URIs."""

import pytest
from geo_uri_parse_pure import parse_geo_uri, GeoURI


class TestRealWorldURIs:
    """Real-world URIs from RFC 5870 examples, BIP 21, and QRPC."""

    def test_rfc5870_example_1(self):
        # RFC 5870 §6 examples
        result = parse_geo_uri("geo:51.5008,-0.1247")
        assert isinstance(result, GeoURI)
        assert result.lat == 51.5008
        assert result.lon == -0.1247

    def test_rfc5870_example_with_altitude(self):
        result = parse_geo_uri("geo:33.8569,-117.6033,350")
        assert result.lat == 33.8569
        assert result.lon == -117.6033
        assert result.alt == 350.0

    def test_bip21_london_eye(self):
        result = parse_geo_uri("geo:51.5008,-0.1247;crs=wgs84;u=10")
        assert result.lat == 51.5008
        assert result.lon == -0.1247
        assert result.crs == "wgs84"
        assert result.uncertainty == 10.0
        assert result.params == {}

    def test_geo_uri_with_param(self):
        # QR code encoded with extra parameters
        result = parse_geo_uri("geo:37.38605,-122.08385;crs=wgs84;u=50;ref=apple")
        assert result.lat == 37.38605
        assert result.lon == -122.08385
        assert result.crs == "wgs84"
        assert result.uncertainty == 50.0
        assert result.params == {"ref": "apple"}

    def test_dallas_texas(self):
        result = parse_geo_uri("geo:32.814,-96.8714")
        assert result.lat == 32.814
        assert result.lon == -96.8714

    def test_zero_coordinates(self):
        result = parse_geo_uri("geo:0,0")
        assert result.lat == 0.0
        assert result.lon == 0.0
        assert result.alt is None
        assert result.crs == "wgs84"

    def test_sydney_opera_house(self):
        result = parse_geo_uri("geo:-33.8688,151.2093,10")
        assert result.lat == -33.8688
        assert result.lon == 151.2093
        assert result.alt == 10.0

    def test_paris_eiffel_tower(self):
        result = parse_geo_uri("geo:48.8584,2.2945")
        assert result.lat == 48.8584
        assert result.lon == 2.2945

    def test_geo_uri_param_semicolon_preserved(self):
        # Multiple params
        result = parse_geo_uri("geo:0,0;x=1;y=2;z=3")
        assert result.params == {"x": "1", "y": "2", "z": "3"}

    def test_negative_altitude_dead_sea(self):
        # Dead Sea: lowest land point on Earth
        result = parse_geo_uri("geo:31.5,35.5,-430")
        assert result.alt == -430.0


class TestRoundTrip:
    """AC11: format(parse(uri)) round-trip stability."""

    def test_roundtrip_basic(self):
        uri = "geo:51.5008,-0.1247"
        result = parse_geo_uri(uri)
        # Re-format as geo: URI string
        reformatted = f"geo:{result.lat},{result.lon}"
        reparsed = parse_geo_uri(reformatted)
        assert reparsed.lat == result.lat
        assert reparsed.lon == result.lon

    def test_roundtrip_with_altitude(self):
        uri = "geo:37.4,-122.1,10.5"
        result = parse_geo_uri(uri)
        reformatted = f"geo:{result.lat},{result.lon},{result.alt}"
        reparsed = parse_geo_uri(reformatted)
        assert reparsed.lat == result.lat
        assert reparsed.lon == result.lon
        assert reparsed.alt == result.alt

    def test_roundtrip_with_all_params(self):
        uri = "geo:51.5,-0.12,10;crs=wgs84;u=5;foo=bar"
        result = parse_geo_uri(uri)
        assert result.lat == 51.5
        assert result.lon == -0.12
        assert result.alt == 10.0
        assert result.crs == "wgs84"
        assert result.uncertainty == 5.0
        assert result.params == {"foo": "bar"}


class TestMalformedURIs:
    """Robustness: malformed URIs raise ValueError, not crash."""

    def test_missing_latitude(self):
        with pytest.raises(ValueError):
            parse_geo_uri("geo:,0")

    def test_missing_longitude(self):
        with pytest.raises(ValueError):
            parse_geo_uri("geo:0,")

    def test_double_comma(self):
        with pytest.raises(ValueError):
            parse_geo_uri("geo:0,,0")

    def test_missing_scheme(self):
        with pytest.raises(ValueError, match="not a geo: URI"):
            parse_geo_uri("51.5,-0.12")

    def test_only_scheme_geo_colon(self):
        with pytest.raises(ValueError):
            parse_geo_uri("geo:")

    def test_malformed_coords_non_numeric(self):
        with pytest.raises(ValueError):
            parse_geo_uri("geo:abc,def")

    def test_malformed_coords_mixed(self):
        with pytest.raises(ValueError):
            parse_geo_uri("geo:51.5,abc")

    def test_latlon_reversed(self):
        # Intentionally reversed lat/lon — should still parse
        # (we don't know user intent, just bounds)
        result = parse_geo_uri("geo:-0.1247,51.5008")
        assert result.lat == -0.1247
        assert result.lon == 51.5008

    def test_huge_numbers_rejected(self):
        with pytest.raises(ValueError, match="latitude out of WGS-84 bounds"):
            parse_geo_uri("geo:999.0,0")

    def test_negative_huge_altitude_valid(self):
        # Very negative altitude is valid (below Earth's surface)
        result = parse_geo_uri("geo:0,0,-10000")
        assert result.alt == -10000.0

    def test_very_large_altitude_valid(self):
        # Very large altitude is valid (satellite orbit)
        result = parse_geo_uri("geo:0,0,400000")
        assert result.alt == 400000.0
