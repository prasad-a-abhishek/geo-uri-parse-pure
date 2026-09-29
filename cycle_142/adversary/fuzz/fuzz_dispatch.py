"""Atheris harness targeting parse_geo_uri's TypeError/AttributeError defense.

Targets: Invariant 21 — parse must be total over arbitrary input.
Attack vectors: None, bytes, int, list, dict, empty string, NUL bytes.
"""
import sys
import atheris
from geo_uri_parse_pure import parse_geo_uri


@atheris.instrument_func
def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    choice = fdp.ConsumeIntInRange(0, 6)
    if choice == 0:
        candidate = None
    elif choice == 1:
        candidate = b"geo:1,2"
    elif choice == 2:
        candidate = 42
    elif choice == 3:
        candidate = ["geo:1,2"]
    elif choice == 4:
        candidate = {"uri": "geo:1,2"}
    elif choice == 5:
        candidate = ""
    else:
        candidate = fdp.ConsumeUnicodeNoSurrogates(64)
    try:
        parse_geo_uri(candidate)
    except (ValueError, TypeError):
        pass
    except Exception:
        raise


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
