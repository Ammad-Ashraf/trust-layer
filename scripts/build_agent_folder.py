"""Build the `simple_ledger` Collider-Bench agent folder (decision 0008; design section 6).

The result is upstream `agents/simple` plus:
  run.py                     our launcher: same prompt as `simple`, installs the gate hook
  AGENTS.md                  + the ledger paragraph (integration/agent/AGENTS-ledger.md)
  runtime/bin/record-quantity      ledger CLI shim (shows up as bin/record-quantity)
  runtime/hooks/trustlayer-gate    Stop-hook shim (not on the agent's bin/)
  runtime/lib/trustlayer/          the checker source (*.py only)
  runtime/task-context/*.yaml      public task facts (integration/task-context/)
  runtime/config.yaml              c5_tolerance (fixed by 0016) and max_bounces
  runtime/BUILD-INFO.yaml          trust-layer commit, dirty flag, build time

Nothing from tasks/, docs/, CLAUDE.md, .claude/ or papers/notes/ is copied;
tests/test_fairness.py builds the folder and checks that.

Usage:
    python scripts/build_agent_folder.py --out build/agent/simple_ledger
    python scripts/build_agent_folder.py --out <fork>/agents/simple_ledger --into-fork
"""

from __future__ import annotations

import argparse
import shutil
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SUBMODULE = ROOT / "external" / "collider-bench"
AGENT_SRC = ROOT / "integration" / "agent"
CONTEXTS = ROOT / "integration" / "task-context"
PACKAGE = ROOT / "src" / "trustlayer"
STUDY_A_CONFIG = ROOT / "experiments" / "02-study-a" / "config.yaml"
AGENT_NAME = "simple_ledger"
DEFAULT_MAX_BOUNCES = 3


class BuildError(RuntimeError):
    """Something the build refuses to do, with the reason."""


def _git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return out.stdout.strip()


def _write_lf(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n"))
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _c5_tolerance(config: Path) -> float:
    data = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    tau = data.get("c5_tolerance")
    if not isinstance(tau, int | float) or isinstance(tau, bool):
        raise BuildError(f"{config}: c5_tolerance is missing (decision 0016 fixes it)")
    return float(tau)


def build(
    out: Path,
    collider_bench: Path = SUBMODULE,
    config: Path = STUDY_A_CONFIG,
    max_bounces: int = DEFAULT_MAX_BOUNCES,
    into_fork: bool = False,
) -> Path:
    """Build the agent folder at `out` (replacing it) and return `out`."""
    out = out.resolve()
    if out.is_relative_to(SUBMODULE.resolve()) and not into_fork:
        raise BuildError(
            "refusing to write into external/collider-bench (pass --into-fork "
            "only for a fork checkout)"
        )
    simple = collider_bench / "agents" / "simple"
    if not (simple / "run.py").is_file():
        raise BuildError(f"{simple} is not a Collider-Bench `simple` agent folder")
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(simple, out, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    _write_lf(out / "run.py", (AGENT_SRC / "run.py").read_text(encoding="utf-8"), executable=True)
    agents_md = (out / "AGENTS.md").read_text(encoding="utf-8").rstrip("\n") + "\n"
    _write_lf(out / "AGENTS.md", agents_md + (AGENT_SRC / "AGENTS-ledger.md").read_text("utf-8"))

    runtime = out / "runtime"
    _write_lf(
        runtime / "bin" / "record-quantity",
        (AGENT_SRC / "record-quantity").read_text(encoding="utf-8"),
        executable=True,
    )
    _write_lf(
        runtime / "hooks" / "trustlayer-gate",
        (AGENT_SRC / "trustlayer-gate").read_text(encoding="utf-8"),
        executable=True,
    )
    for src in sorted(PACKAGE.rglob("*.py")):
        _write_lf(
            runtime / "lib" / "trustlayer" / src.relative_to(PACKAGE),
            src.read_text(encoding="utf-8"),
        )
    for ctx in sorted(CONTEXTS.glob("*.yaml")):
        _write_lf(runtime / "task-context" / ctx.name, ctx.read_text(encoding="utf-8"))

    tau = _c5_tolerance(config)
    _write_lf(
        runtime / "config.yaml",
        yaml.safe_dump(
            {
                "c5_tolerance": tau,
                "max_bounces": max_bounces,
                "fixed_by": "decision 0016",
                "from": config.resolve().relative_to(ROOT).as_posix(),
            },
            sort_keys=False,
        ),
    )
    info = {
        "agent": AGENT_NAME,
        "trust_layer_commit": _git("rev-parse", "HEAD"),
        "trust_layer_dirty": bool(_git("status", "--porcelain", "--", "src", "integration")),
        "collider_bench_commit": _git("-C", str(collider_bench), "rev-parse", "HEAD"),
        "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "c5_tolerance": tau,
        "max_bounces": max_bounces,
    }
    _write_lf(runtime / "BUILD-INFO.yaml", yaml.safe_dump(info, sort_keys=False))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out", type=Path, default=ROOT / "build" / "agent" / AGENT_NAME)
    p.add_argument("--collider-bench", type=Path, default=SUBMODULE)
    p.add_argument("--config", type=Path, default=STUDY_A_CONFIG)
    p.add_argument("--max-bounces", type=int, default=DEFAULT_MAX_BOUNCES)
    p.add_argument("--into-fork", action="store_true", help="allow writing into a fork checkout")
    args = p.parse_args(argv)
    try:
        out = build(args.out, args.collider_bench, args.config, args.max_bounces, args.into_fork)
    except BuildError as exc:
        print(f"build_agent_folder: {exc}", file=sys.stderr)
        return 1
    print(f"built {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
