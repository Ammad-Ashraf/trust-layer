"""`python -m trustlayer.report study-a | study-b`: write a study's results folder.

study-a: runs Study A, writes `results/study-a.md` (tables) and `results/cases.yaml`.
study-b: reads Study B's run folders, writes `results/study-b.md` and `results/runs.yaml`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from trustlayer.inject import load_study_config
from trustlayer.report import study_b
from trustlayer.report.study_a import render_markdown, run_study, to_records

ROOT = Path(__file__).resolve().parents[3]


def _version(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m trustlayer.report")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("study-a", help="score Study A's injected copies and write the tables")
    p.add_argument("--root", type=Path, default=ROOT, help="repo root (paths in the config)")
    p.add_argument("--config", type=Path, default=None)
    p.add_argument("--out", type=Path, default=None)
    b = sub.add_parser("study-b", help="tabulate Study B's run folders")
    b.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.command == "study-b":
        return _study_b(args.root)

    root: Path = args.root
    config_path = args.config or root / "experiments" / "02-study-a" / "config.yaml"
    out = args.out or config_path.parent / "results"
    config = load_study_config(config_path, root)
    result = run_study(config)
    meta = {"version": _version(root), "command": "python -m trustlayer.report study-a"}
    out.mkdir(parents=True, exist_ok=True)
    (out / "study-a.md").write_text(render_markdown(result, config, meta), encoding="utf-8")
    (out / "cases.yaml").write_text(
        yaml.safe_dump(
            {"version": meta["version"], "tau": result.tau, "cases": to_records(result)},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    caught = sum(o.flagged for o in result.outcomes if o.case.kind == "injection")
    n_inj = sum(o.case.kind == "injection" for o in result.outcomes)
    alarms = sum(o.flagged for o in result.outcomes if o.case.kind == "near_miss")
    n_near = sum(o.case.kind == "near_miss" for o in result.outcomes)
    print(f"Study A: caught {caught}/{n_inj} injections, {alarms}/{n_near} false alarms -> {out}")
    return 0


def _study_b(root: Path) -> int:
    exp = root / "experiments" / "03-study-b"
    runs, voids = study_b.load_runs(exp / "runs")
    out = exp / "results"
    out.mkdir(parents=True, exist_ok=True)
    version = _version(root)
    (out / "study-b.md").write_text(study_b.render_markdown(runs, voids, version), encoding="utf-8")
    records = [{**vars(r), "passed": r.passed} for r in runs]
    (out / "runs.yaml").write_text(
        yaml.safe_dump({"version": version, "voids": voids, "runs": records}, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Study B: {len(runs)} final runs, {sum(voids.values())} void attempts -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
