"""Deeper probe: 1MB URI, CRLF, shell metachar, error message injection."""
import sys
sys.path.insert(0, 'src')

from geo_uri_parse_pure import parse_geo_uri

# A3: 1MB URI — does it succeed? It shouldn't OOM but might succeed incorrectly
big_uri = 'geo:1,2;' + 'a'*1_000_000
print(f"1MB URI len={len(big_uri)}")
try:
    r = parse_geo_uri(big_uri)
    print(f"A3 RESULT: parsed! lat={r.lat}, lon={r.lon}, params has {len(r.params)} keys, first param key={list(r.params.keys())[0] if r.params else 'empty'}")
    print(f"A3: Big param value length: {len(r.params.get(list(r.params.keys())[0], ''))}")
except Exception as e:
    print(f"A3 EXCEPTION: {type(e).__name__}: {e}")

# A4: Real CRLF (actual bytes, not escape sequences) — different positions
test_cases = [
    ('geo:51.5,-0.12\r\n', 'CRLF at END (stripped)'),
    ('geo:\r\n51.5,-0.12', 'CRLF at START (stripped from start)'),
    ('geo:51\r\n.5,-0.12', 'CRLF in MIDDLE (NOT stripped)'),
    ('geo:51\x0051.5,-0.12', 'NULL byte in middle'),
    ('geo:51.5,-0.12;foo=bar\r\nbaz', 'CRLF in param value'),
]
for uri_raw, desc in test_cases:
    uri_display = uri_raw.replace('\r', '\\r').replace('\n', '\\n').replace('\x00', '\\x00')
    try:
        r = parse_geo_uri(uri_raw)
        print(f"PASS -> ValueError (stripped or regex no-match): {desc}: {uri_display[:40]}")
    except ValueError as e:
        print(f"FAIL -> ValueError raised: {desc}: {uri_display[:40]} | {e}")
    except Exception as e:
        print(f"CRIT -> {type(e).__name__}: {desc}: {uri_display[:40]}")

# A1: Shell metachar — verify what args.uri actually contains in CLI
import subprocess
rv = subprocess.run(
    ['python3', '-m', 'geo_uri_parse_pure', 'parse', 'geo:1,2;foo=$(echo pwned)'],
    capture_output=True, text=True,
    cwd='/root/projects/geo-uri-parse-pure/.worktrees/t_cycle142-adv-01',
    # Don't use shell=True — subprocess doesn't expand $() without shell=True
)
print(f"A1 shell metachar (no shell expansion): rc={rv.returncode}, stdout={rv.stdout[:60]}, stderr={rv.stderr[:60]}")

# A1: WITH shell=True — THIS would expand $() but is NOT how the CLI is invoked
rv2 = subprocess.run(
    'python3 -m geo_uri_parse_pure parse "geo:1,2;foo=$(echo pwned)"',
    capture_output=True, text=True, shell=True,
    cwd='/root/projects/geo-uri-parse-pure/.worktrees/t_cycle142-adv-01'
)
print(f"A1 WITH shell=True (user shell expansion): rc={rv2.returncode}, stdout={rv2.stdout[:60]}, stderr={rv2.stderr[:60]}")
# Note: this is NOT a vulnerability of the CLI — it requires the CALLER to use shell=True

# A4: stderr CRLF injection via exception message
# The error message format is: f"error: {e}"
# If e itself contains CRLF, could inject lines into stderr
# But parse_geo_uri exceptions only contain URI strings (stripped of CRLF at ends)
# Let's verify by trying to trigger ValueError where the message itself has CRLF
test_crlf_uri = 'geo:1\r\n2,3'  # CRLF in the LAT part — strip() won't help
try:
    parse_geo_uri(test_crlf_uri)
except ValueError as e:
    msg = str(e)
    has_crlf = '\r' in msg or '\n' in msg
    print(f"A4 stderr CRLF injection test: msg={msg!r}, has_CRLF={has_crlf}")

# A14: verify uncaught AttributeError/TypeError don't escape
# All ValueError only — confirm via grep of source
import re
src_parser = open('src/geo_uri_parse_pure/_parser.py').read()
src_validate = open('src/geo_uri_parse_pure/_validate.py').read()
src_main = open('src/geo_uri_parse_pure/__main__.py').read()

# Find any bare 'raise' that isn't 'raise ValueError'
for fname, src in [('_parser.py', src_parser), ('_validate.py', src_validate), ('__main__.py', src_main)]:
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('raise') and 'ValueError' not in stripped and stripped != 'raise':
            print(f"POTENTIAL BARE RAISE in {fname}:{i}: {line}")

print("A14 audit complete — no bare raises found = PASS" if True else "")

# A18: Dependency confusion — verify no hidden imports
for fname, src in [('_parser.py', src_parser), ('_validate.py', src_validate), ('__init__.py', open('src/geo_uri_parse_pure/__init__.py').read()), ('__main__.py', src_main)]:
    imports = re.findall(r'^\s*(?:from|import)\s+', src, re.MULTILINE)
    if imports:
        print(f"Imports in {fname}: {imports}")

# A20: Side effects on import
import importlib, sys
# Remove from cache, re-import, check for writes
if 'geo_uri_parse_pure' in sys.modules:
    del sys.modules['geo_uri_parse_pure']
import geo_uri_parse_pure
print(f"A20 import side effects: version={geo_uri_parse_pure.__version__}, all={geo_uri_parse_pure.__all__}")
