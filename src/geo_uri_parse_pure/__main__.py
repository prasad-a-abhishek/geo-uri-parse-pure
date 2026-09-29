"""CLI entry point for geo-uri-parse-pure.

Usage:
    python -m geo_uri_parse_pure parse "geo:51.5008,-0.1247"
    python -m geo_uri_parse_pure validate "geo:51.5008,-0.1247"
    python -m geo_uri_parse_pure --help
"""

from __future__ import annotations

import argparse
import json
import sys

from ._parser import GeoURI, parse_geo_uri

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 2 on error."""
    parser = argparse.ArgumentParser(
        prog="geo-uri-parse-pure",
        description="Parse and validate RFC 5870 geo: URIs.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # parse subcommand
    p_parse = sub.add_parser("parse", help="Parse a geo: URI and emit JSON to stdout.")
    p_parse.add_argument("uri", help="The geo: URI to parse, e.g. geo:51.5,-0.12")

    # validate subcommand
    p_val = sub.add_parser("validate", help="Validate a geo: URI (exit 0 if valid).")
    p_val.add_argument("uri", help="The geo: URI to validate.")

    args = parser.parse_args(argv)

    try:
        if args.command == "parse":
            result = parse_geo_uri(args.uri)
            output = {
                "lat": result.lat,
                "lon": result.lon,
                "alt": result.alt,
                "crs": result.crs,
                "uncertainty": result.uncertainty,
                "params": result.params,
            }
            print(json.dumps(output, indent=2))
            return 0

        elif args.command == "validate":
            parse_geo_uri(args.uri)
            print("valid")
            return 0

    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
