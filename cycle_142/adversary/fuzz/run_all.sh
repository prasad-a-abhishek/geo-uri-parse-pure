#!/bin/bash
# Run all 4 Atheris harnesses with 5min wall-time per surface.
# corpus/ subdirs contain seed inputs; libFuzzer auto-picks them up.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs crashes

for harness in fuzz_parse fuzz_dispatch fuzz_cli_parse fuzz_geo_uri_attrs; do
  echo "=== Running ${harness} (5min) ==="
  timeout 300 python3 "${harness}.py" \
    -max_len=4096 \
    -print_final_stats=1 \
    -artifact_prefix="crashes/${harness}/" \
    corpus/${harness} \
    > "logs/${harness}.log" 2>&1 || true
  echo "--- ${harness} done ---" >> "logs/${harness}.log"
done
echo "Done. Aggregating stats..."
python3 aggregate_stats.py
