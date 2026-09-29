# Benchmark: geo-uri-parse-pure vs naive-split

**Environment**: Python 3.11.15, Linux (container)

**Method**: `time.perf_counter()`, `tracemalloc` | Iterations per workload: 5

| Workload | geo-uri-parse-pure (mean µs) | naive-split (mean µs) | Overhead |

|----------|---------------------------|----------------------|----------|
| basic_2d | 10.0 | 2.2 | 4.5× |
| basic_3d | 10.3 | 2.6 | 4.0× |
| negative_coords | 9.0 | 2.2 | 4.1× |
| wgs84_alt | 8.9 | 2.2 | 4.0× |
| crs_param | 72.0 | 1.9 | 37.9× |
| uncertainty | 11.1 | 1.8 | 6.2× |
| full_params | 26.2 | 3.7 | 7.1× |
| param_disorder | 22.4 | 2.5 | 9.0× |
| zero_coords | 6.5 | 1.3 | 5.0× |
| edge_bounds | 13.8 | 2.4 | 5.8× |
