#!/bin/bash
# Run all 4 Atheris harnesses with 5min wall-time per surface.
# Each runs in its own subdir to keep stats_*.json separate.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs crashes corpus stats
for harness in fuzz_parse fuzz_dispatch fuzz_cli_parse fuzz_geo_uri_attrs; do
  echo "=== Running ${harness} ==="
  timeout 300 python3 "${harness}.py" \
    -atheris_runs=1000000 \
    -artifact_prefix="crashes/${harness}/" \
    > "logs/${harness}.log" 2>&1 || true
done
echo "Done. Aggregating stats..."
python3 aggregate_stats.py
