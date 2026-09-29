#!/usr/bin/env python3
# Minimized reproducer for F-001: 1MB URI without length guard
# The finding is the absence of a length limit; the minimal trigger
# is any URI whose pvalue exceeds ~1MB. Here: geo:1,2; + 1MB of 'a'.
import sys
sys.path.insert(0, 'src')
from geo_uri_parse_pure import parse_geo_uri
uri = 'geo:1,2;' + 'a' * 1000000
print(f"Input length: {len(uri)} bytes")
result = parse_geo_uri(uri)
print(f"Parsed successfully — no crash, no OOM")
print(f"Result: lat={result.lat}, lon={result.lon}, params={list(result.params.keys())[:3]}...")
