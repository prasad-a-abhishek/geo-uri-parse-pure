# Benchmark: geo-uri-parse-pure vs naive-split

**Environment**: Python 3.11.15, Linux (container)

**Method**: `time.perf_counter()`, `tracemalloc` | Iterations per workload: 5

| Workload | geo-uri-parse-pure (mean µs) | naive-split (mean µs) | Overhead |

|----------|---------------------------|----------------------|----------|
| basic_2d | 14.4 | 2.7 | 5.3× |
| basic_3d | 12.5 | 3.2 | 3.9× |
| negative_coords | 11.0 | 2.6 | 4.2× |
| wgs84_alt | 10.8 | 2.6 | 4.2× |
| crs_param | 88.2 | 2.4 | 36.8× |
| uncertainty | 13.5 | 2.1 | 6.4× |
| full_params | 32.0 | 4.5 | 7.1× |
| param_disorder | 27.4 | 3.0 | 9.1× |
| zero_coords | 8.0 | 1.6 | 5.0× |
| edge_bounds | 16.8 | 2.9 | 5.8× |
