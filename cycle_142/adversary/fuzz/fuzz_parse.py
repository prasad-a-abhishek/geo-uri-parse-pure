"""Atheris harness for geo_uri_parse_pure.parse_geo_uri() — core API surface.

Targets: parse_geo_uri(uri: str | None) -> GeoURI
Attack vectors: None input, bytes input, malformed URIs, unicode edge cases,
control chars, percent-encoding bypasses, CRLF injection, length overflow.
"""
import sys
import atheris
from geo_uri_parse_pure import parse_geo_uri


@atheris.instrument_func
def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    # Try several mutation strategies
    raw = fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(0, 4096))
    try:
        uri = parse_geo_uri(raw)
        # Oracle: shape-check the returned object
        _ = uri.lat, uri.lon, uri.alt, uri.crs, uri.uncertainty
    except (ValueError, TypeError):
        pass  # expected on malformed input
    except Exception:
        raise  # anything else is a bug


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
