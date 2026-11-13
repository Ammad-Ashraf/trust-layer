"""Create a run folder with a manifest template.

Usage:
    python scripts/new_run.py 00-smoke-run sus-16-034 baseline

Creates experiments/<experiment>/runs/<YYYYMMDD-HHMM>_<task>_<arm>_<n>/ with
manifest.yaml and labels.yaml to fill in during and after the run.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = """schema_version: 1
experiment: {experiment}
task: {task}
arm: {arm}                 # baseline | checker
model_snapshot: null
collider_bench_commit: null
container_digest: null
machine: null              # e.g. runner-laptop-8c, cloud-128vcpu
cores: null
n_gen: null
wall_clock_hours: null
tokens: null
api_cost_usd: null
bounces: null              # checker arm only
outcome: null              # scored | timeout | crash
notes: ""
"""

LABELS = """# Every mistake found in this run, with its sub-gap code (1a-1e, 2a-2e, 3a-3f).
schema_version: 1
labels: []
#  - code: 1a
#    where: "transcript line / step"
#    what: "10 pb used as 10 fb"
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a run folder")
    parser.add_argument("experiment")
    parser.add_argument("task")
    parser.add_argument("arm", choices=["baseline", "checker"])
    args = parser.parse_args()

    runs = ROOT / "experiments" / args.experiment / "runs"
    if not runs.is_dir():
        print(f"No such experiment: {args.experiment}", file=sys.stderr)
        return 1
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    n = len(list(runs.glob(f"*_{args.task}_{args.arm}_*"))) + 1
    run = runs / f"{stamp}_{args.task}_{args.arm}_{n}"
    (run / "raw").mkdir(parents=True)
    (run / "manifest.yaml").write_text(MANIFEST.format(**vars(args)), encoding="utf-8")
    (run / "labels.yaml").write_text(LABELS, encoding="utf-8")
    print(run.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
