# Benchmark: geo-uri-parse-pure vs naive-split

**Environment**: Python 3.11.15, Linux (container)

**Method**: `time.perf_counter()`, `tracemalloc` | Iterations per workload: 5

| Workload | geo-uri-parse-pure (mean µs) | naive-split (mean µs) | Overhead |

|----------|---------------------------|----------------------|----------|
| basic_2d | 11.0 | 2.4 | 4.6× |
| basic_3d | 11.2 | 2.7 | 4.1× |
| negative_coords | 9.9 | 2.3 | 4.3× |
| wgs84_alt | 9.6 | 2.3 | 4.2× |
| crs_param | 78.1 | 2.1 | 37.2× |
| uncertainty | 11.8 | 1.8 | 6.6× |
| full_params | 27.7 | 3.9 | 7.1× |
| param_disorder | 23.6 | 2.6 | 9.1× |
| zero_coords | 6.8 | 1.3 | 5.2× |
| edge_bounds | 14.6 | 2.4 | 6.1× |
