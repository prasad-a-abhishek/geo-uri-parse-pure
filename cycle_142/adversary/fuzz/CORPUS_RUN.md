# Corpus Run Report

## Per-Surface Stats

| Surface | Iterations | Crashes | Exit Code |
|---------|------------|---------|----------|
| fuzz_geo_uri_attrs | 228,075,424 | 0 | 0 |
| fuzz_dispatch | 186,338,453 | 0 | 0 |
| fuzz_cli_parse | 1,697,745 | 0 | 0 |
| fuzz_parse | 236,049,047 | 0 | 0 |

**Total**: 652,160,669 iters, 0 crashes

## Fuzzer Settings

- Wall-time limit: 300s (5 min) per surface
- `-max_len=4096`, `-print_final_stats=1`
- Sanitizers: ASan + UBSan enabled
- Framework: atheris (libFuzzer backend)

## Notable Findings

No crashes detected.
