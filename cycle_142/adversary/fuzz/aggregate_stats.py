"""Parse logs/*.log + crashes/* and emit AGGREGATE_STATS.json."""
import json
import os
import glob

stats = {
    "total_iters": 0,
    "total_crashes": 0,
    "total_oracle_mismatches": 0,
    "per_surface": {},
}
for log in glob.glob("logs/*.log"):
    name = os.path.basename(log).replace(".log", "")
    surface_stats = {"iters": 0, "crashes": 0, "oracle_mismatches": 0, "exit_code": 0}
    with open(log) as f:
        for line in f:
            # Atheris prints "INFO:__main__:Done 1234567 iters in 30.0s"
            if "iters" in line and "Done" in line:
                try:
                    surface_stats["iters"] = int(line.split()[2])
                except (IndexError, ValueError):
                    pass
            # Capture exit code from "Process exited with signal" or "Exit 0"
            if "exited with signal" in line or "Exit" in line:
                parts = line.strip().split()
                if parts[-1].isdigit():
                    surface_stats["exit_code"] = int(parts[-1])
    crash_dir = f"crashes/{name}"
    if os.path.isdir(crash_dir):
        surface_stats["crashes"] = len(os.listdir(crash_dir))
    stats["per_surface"][name] = surface_stats
    stats["total_iters"] += surface_stats["iters"]
    stats["total_crashes"] += surface_stats["crashes"]

# Write AGGREGATE_STATS.json + CORPUS_RUN.md placeholder
with open("AGGREGATE_STATS.json", "w") as f:
    json.dump(stats, f, indent=2)

with open("CORPUS_RUN.md", "w") as f:
    f.write("# Corpus Run Report\n\n## Per-Surface Stats\n\n")
    for name, st in stats["per_surface"].items():
        f.write(f"- **{name}**: {st['iters']} iters, {st['crashes']} crashes\n")
    f.write(f"\n**Total**: {stats['total_iters']} iters, {stats['total_crashes']} crashes\n")
print(f"Aggregate: {stats['total_iters']} iters, {stats['total_crashes']} crashes")
