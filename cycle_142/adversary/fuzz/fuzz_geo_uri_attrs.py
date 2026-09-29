"""Atheris harness for GeoURI namedtuple attribute round-trip.

Targets: parse -> GeoURI -> access every field; verify immutability.
"""
import sys
import atheris
from geo_uri_parse_pure import parse_geo_uri


@atheris.instrument_func
def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    raw = fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(0, 512))
    try:
        uri = parse_geo_uri(raw)
        # Read every field; verify types
        assert isinstance(uri.lat, (int, float))
        assert isinstance(uri.lon, (int, float))
        assert uri.alt is None or isinstance(uri.alt, (int, float))
        assert isinstance(uri.crs, str)
        assert uri.uncertainty is None or isinstance(uri.uncertainty, (int, float))
        assert isinstance(uri.params, dict)
        # Mutability check
        try:
            uri.lat = 0  # namedtuple should reject
            assert False, "namedtuple should be immutable"
        except AttributeError:
            pass
    except (ValueError, TypeError):
        pass
    except (AssertionError,):
        raise
    except Exception:
        raise


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
