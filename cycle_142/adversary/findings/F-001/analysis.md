# F-001 Analysis

## Finding
1,000,008-byte URI (`geo:1,2;` + 1MB of `a`) is accepted by `parse_geo_uri()`
without raising an exception, crashing, or causing OOM.

## Root Cause
The ABNF-defined param-value pattern `[^;]*` in `_parser.py` has no
explicit length bound. Python's `re.finditer` processes the 1MB string in
O(n) linear time. RFC 5870 §4.3 notes that implementations "can enforce a
local length limit" but this is a MAY, not a MUST.

## Severity Rationale (Low)
- No crash, no OOM, no uncaught exception
- Python's memory allocator handles the 1MB string without issue
- Not a security vulnerability (no code execution, no information disclosure)
- A missing implementation convenience note from the RFC

## Suggested Fix
Add an early length check in `_parser.py` before the ABNF pass:
```python
if len(uri) > 4096:
    raise ValueError(f"URI too long: {len(uri)} bytes (max 4096)")
```

## Fuzzer Coverage
652M Atheris iterations across all 4 surfaces did not surface this as a crash
because no crash/exceptions occurs — it is a non-crash robustness gap.
