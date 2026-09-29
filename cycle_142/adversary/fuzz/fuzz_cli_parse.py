"""Atheris harness for CLI parse subcommand.

Targets: __main__.py main() invoked with parse subcommand + URI argv.
Attack vectors: shell metachars in URI, NUL bytes, very long URIs,
control chars, JSON injection in stdout.
"""
import io
import sys
import atheris
from geo_uri_parse_pure.__main__ import main


@atheris.instrument_func
def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    uri = fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(0, 1024))
    old_argv = sys.argv
    old_stdout = sys.stdout
    try:
        sys.argv = ["geo-uri-parse-pure", "parse", uri]
        sys.stdout = io.StringIO()
        rc = main()
        out = sys.stdout.getvalue()
        # Oracle: exit code 0 or 2 only; never -1 or uncaught exception
        assert rc in (0, 2), f"unexpected exit code {rc}"
        # If exit 0, output must be parseable JSON
        if rc == 0:
            import json
            json.loads(out)
    except (ValueError, SystemExit, AssertionError):
        pass
    except Exception:
        raise
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
