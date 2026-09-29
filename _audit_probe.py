"""Adversary probe script — writes results to stdout."""
import sys
sys.path.insert(0, 'src')

from geo_uri_parse_pure import parse_geo_uri, GeoURI

results = []

# A6: Type confusion
for tc_name, tc in [('None', None), ('bytes', b'geo:1,2'), ('int', 42), ('dict', {'a':1}), ('list', [1,2])]:
    try:
        parse_geo_uri(tc)
        results.append(('FAIL', f'A6 {tc_name}', 'no raise'))
    except ValueError:
        results.append(('PASS', f'A6 {tc_name}', 'ValueError'))
    except Exception as e:
        results.append(('FAIL', f'A6 {tc_name}', f'{type(e).__name__}'))

# A5: inf/nan
for val in ['inf', '-inf', 'nan', '1e308', '-1e308']:
    try:
        r = parse_geo_uri(f'geo:{val},0')
        results.append(('FAIL', f'A5 {val}', f'got {r}'))
    except ValueError:
        results.append(('PASS', f'A5 {val}', 'ValueError'))
    except Exception as e:
        results.append(('FAIL', f'A5 {val}', f'{type(e).__name__}'))

# A5: -90.0001
try:
    parse_geo_uri('geo:-90.0001,0')
    results.append(('FAIL', 'A5 -90.0001', 'no raise'))
except ValueError:
    results.append(('PASS', 'A5 -90.0001', 'ValueError'))

# A5: -0
try:
    r = parse_geo_uri('geo:-0,0')
    results.append(('PASS', 'A5 -0', f'lat={r.lat}'))
except Exception as e:
    results.append(('FAIL', 'A5 -0', f'{type(e).__name__}'))

# A4: %00
try:
    parse_geo_uri('geo:%00,0')
    results.append(('FAIL', 'A4 %00', 'no raise'))
except ValueError:
    results.append(('PASS', 'A4 %00', 'ValueError'))

# A4: CRLF
try:
    parse_geo_uri('geo:51.5,-0.12\r\n')
    results.append(('FAIL', 'A4 CRLF', 'no raise'))
except ValueError:
    results.append(('PASS', 'A4 CRLF', 'ValueError'))

# A4: raw ctrl char
try:
    parse_geo_uri('geo:\x011,2')
    results.append(('FAIL', 'A4 ctrl 0x01', 'no raise'))
except ValueError:
    results.append(('PASS', 'A4 ctrl 0x01', 'ValueError'))

# A3: 1MB URI
big_uri = 'geo:1,2;' + 'a'*1_000_000
try:
    parse_geo_uri(big_uri)
    results.append(('FAIL', 'A3 1MB URI', 'no raise'))
except ValueError as e:
    results.append(('PASS', 'A3 1MB URI', f'ValueError short-circuit: {str(e)[:60]}'))
except MemoryError:
    results.append(('CRIT', 'A3 1MB URI', 'MemoryError'))
except Exception as e:
    results.append(('FAIL', 'A3 1MB URI', f'{type(e).__name__}'))

# A2: zero-width joiner in lat
try:
    r = parse_geo_uri('geo:\u200b1,2')
    results.append(('INFO', 'A2 ZWJOINT', f'accepted lat={r.lat}'))
except ValueError:
    results.append(('PASS', 'A2 ZWJOINT', 'ValueError'))

# A15: 100 params
deep_params = ';'.join([f'p{i}=v{i}' for i in range(100)])
deep_uri = f'geo:1,2;{deep_params}'
try:
    r = parse_geo_uri(deep_uri)
    results.append(('PASS', 'A15 100params', f'parsed ok, {len(r.params)} params'))
except Exception as e:
    results.append(('FAIL', 'A15 100params', f'{type(e).__name__}'))

# A16: 10000 params
deep_params_10k = ';'.join([f'p{i}=v{i}' for i in range(10_000)])
deep_uri_10k = f'geo:1,2;{deep_params_10k}'
try:
    r = parse_geo_uri(deep_uri_10k)
    results.append(('PASS', 'A16 10kparams', f'parsed ok, {len(r.params)} params'))
except Exception as e:
    results.append(('FAIL', 'A16 10kparams', f'{type(e).__name__}'))

# A10: NaN equality (GeoURI as dict key)
try:
    r1 = parse_geo_uri('geo:nan,0')
    d = {r1: 'value'}
    results.append(('INFO', 'A10 NaN dict key', f'works, hash={hash(r1)}'))
except Exception as e:
    results.append(('FAIL', 'A10 NaN dict key', f'{type(e).__name__}'))

# A9/A11: repr safety
try:
    r = parse_geo_uri('geo:51.5,-0.12;crs=wgs84;u=5')
    repr_str = repr(r)
    results.append(('PASS', 'A9 repr safety', f'repr ok: {repr_str[:40]}'))
except Exception as e:
    results.append(('FAIL', 'A9 repr safety', f'{type(e).__name__}'))

# A13: JSON dump of GeoURI with None and NaN
import json
try:
    r = parse_geo_uri('geo:51.5,-0.12')
    json.dumps({'uri': r._asdict()})
    results.append(('PASS', 'A13 JSON safety', 'ok'))
except Exception as e:
    results.append(('FAIL', 'A13 JSON safety', f'{type(e).__name__}'))

# CLI A19: path traversal
import subprocess
rv = subprocess.run(
    ['python3', '-m', 'geo_uri_parse_pure', 'parse', '../../etc/passwd'],
    capture_output=True, text=True, cwd='/root/projects/geo-uri-parse-pure/.worktrees/t_cycle142-adv-01'
)
if rv.returncode == 2 and 'ValueError' in rv.stderr:
    results.append(('PASS', 'A19 path traversal', f'reject, rc={rv.returncode}'))
elif rv.returncode == 0:
    results.append(('FAIL', 'A19 path traversal', f'accepted!, output={rv.stdout[:40]}'))
else:
    results.append(('INFO', 'A19 path traversal', f'rc={rv.returncode}, out={rv.stdout[:20]}, err={rv.stderr[:40]}'))

# A1: shell metachar in argv
rv = subprocess.run(
    ['python3', '-m', 'geo_uri_parse_pure', 'parse', 'geo:1,2;foo=$(echo pwned)'],
    capture_output=True, text=True, cwd='/root/projects/geo-uri-parse-pure/.worktrees/t_cycle142-adv-01'
)
if rv.returncode == 0:
    results.append(('FAIL', 'A1 shell metachar', f'accepted shell expansion!'))
else:
    results.append(('PASS', 'A1 shell metachar', f'reject rc={rv.returncode}'))

# A7: ReDoS check on param key regex
import re
param_re = re.compile(r';(?P<key>[a-zA-Z][a-zA-Z0-9_-]*)(?:=(?P<val>[^;]*))?')
# Pathological: many repeated chars that almost-but-don't match
evil = ';a=' + 'a'*5000
try:
    param_re.findall(evil)
    results.append(('PASS', 'A7 ReDoS param-key', f'completed ok'))
except Exception as e:
    results.append(('FAIL', 'A7 ReDoS param-key', f'{type(e).__name__}'))

# A3: regex catastrophic backtracking potential in _NUM
num_re = re.compile(r'[+-]?[0-9]+(?:[.][0-9]+)?')
evil2 = '+' + '1'*5000 + '.'
try:
    num_re.match(evil2)
    results.append(('PASS', 'A7 ReDoS NUM', f'completed ok'))
except Exception as e:
    results.append(('FAIL', 'A7 ReDoS NUM', f'{type(e).__name__}'))

for verdict, name, detail in results:
    print(f'{verdict:6s} {name:22s} {detail}')
