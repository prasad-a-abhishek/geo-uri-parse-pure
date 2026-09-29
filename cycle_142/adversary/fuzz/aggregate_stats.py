"""Parse logs/*.log + crashes/* and emit AGGREGATE_STATS.json + CORPUS_RUN.md."""
import json
import os
import re
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
        content = f.read()
        for line in content.splitlines():
            # Atheris prints "INFO:__main__:Done 1234567 iters in 30.0s"
            if "Done" in line and "iters" in line:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p == "Done" and i + 1 < len(parts) and parts[i + 1].isdigit():
                        surface_stats["iters"] = int(parts[i + 1])
                        break
            # libFuzzer final stats: stat::number_of_executed_units: 1234567
            m = re.search(r"stat::number_of_executed_units:\s*(\d+)", line)
            if m:
                surface_stats["iters"] = int(m.group(1))
            # Capture exit code
            if "exited with signal" in line or ("Exit" in line and line.strip().endswith(tuple(str(i) for i in range(10)))):
                parts = line.strip().split()
                for p in reversed(parts):
                    if p.isdigit():
                        surface_stats["exit_code"] = int(p)
                        break

    crash_dir = f"crashes/{name}"
    if os.path.isdir(crash_dir):
        surface_stats["crashes"] = len(os.listdir(crash_dir))

    stats["per_surface"][name] = surface_stats
    stats["total_iters"] += surface_stats["iters"]
    stats["total_crashes"] += surface_stats["crashes"]

with open("AGGREGATE_STATS.json", "w") as f:
    json.dump(stats, f, indent=2)

with open("CORPUS_RUN.md", "w") as f:
    f.write("# Corpus Run Report\n\n")
    f.write("## Per-Surface Stats\n\n")
    f.write("| Surface | Iterations | Crashes | Exit Code |\n")
    f.write("|---------|------------|---------|----------|\n")
    for name, st in stats["per_surface"].items():
        f.write(f"| {name} | {st['iters']:,} | {st['crashes']} | {st['exit_code']} |\n")
    f.write(f"\n**Total**: {stats['total_iters']:,} iters, {stats['total_crashes']} crashes\n")
    f.write(f"\n## Fuzzer Settings\n\n")
    f.write("- Wall-time limit: 300s (5 min) per surface\n")
    f.write("- `-max_len=4096`, `-print_final_stats=1`\n")
    f.write("- Sanitizers: ASan + UBSan enabled\n")
    f.write(f"- Framework: atheris (libFuzzer backend)\n")
    if stats["total_crashes"] > 0:
        f.write("\n## Notable Findings\n\n")
        f.write("See `findings/` directory for crash artifacts.\n")
    else:
        f.write("\n## Notable Findings\n\n")
        f.write("No crashes detected.\n")

print(f"Aggregate: {stats['total_iters']:,} iters, {stats['total_crashes']} crashes")
