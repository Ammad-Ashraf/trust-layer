"""Study B results: with vs without the checker, from the committed run folders.

Reads every `experiments/03-study-b/runs/<slot>_.../` folder (manifest.yaml, score.json,
labels.yaml) and builds the tables in `results/study-b.md`. Void attempts (`*_voidN`) are
counted, never scored (decision 0018). Timeouts and crashes are reported as they are and are
never dropped (decision 0019).

Pass = normalization relative L2 < 0.33, the paper's acceptance threshold tau (Acc_0.33).
Gap-1 errors = labels with a 1a-1e code, filled in by reading each transcript (`/label-run`).
"""

from __future__ import annotations

import json
import re
import statistics
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PASS_L2 = 0.33
SLOT_DIR = re.compile(r"^S\d{2}_")


@dataclass(frozen=True)
class Run:
    """One Study B run, as filed by scripts/study_b.py and labelled afterwards."""

    folder: str
    slot: str
    model: str
    task: str
    arm: str
    rep: int
    outcome: str
    wall_hours: float | None
    delta_norm: float | None
    norm_l2: float | None
    shape_l2: float | None
    judge_status: str | None
    overrule: str | None
    bounces: int | None
    checker_seconds: float | None
    labelled: bool
    gap1: int
    labels: int

    @property
    def passed(self) -> bool:
        return self.norm_l2 is not None and self.norm_l2 < PASS_L2


def _yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _num(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def read_run(folder: Path) -> Run:
    """Build a Run from one run folder."""
    man = _yaml(folder / "manifest.yaml")
    slot = man.get("slot") or {}
    score: dict[str, Any] = {}
    if (folder / "score.json").is_file():
        score = json.loads((folder / "score.json").read_text(encoding="utf-8"))
    norm = score.get("normalization") or {}
    shape = score.get("shape") or {}
    judge = man.get("judge") or {}
    gate = man.get("gate") or {}
    ctime = man.get("checker_time") or {}
    lab = _yaml(folder / "labels.yaml")
    codes = [str(x.get("code", "")) for x in lab.get("labels") or [] if isinstance(x, dict)]
    return Run(
        folder=folder.name,
        slot=str(slot.get("id", folder.name[:3])),
        model=str(slot.get("model") or man.get("model_requested")),
        task=str(slot.get("task") or man.get("task")),
        arm=str(slot.get("arm") or man.get("arm")),
        rep=int(slot.get("rep") or 0),
        outcome=str(man.get("outcome")),
        wall_hours=_num(man.get("wall_clock_hours")),
        delta_norm=_num(norm.get("Delta")),
        norm_l2=_num(norm.get("relative_l2")),
        shape_l2=_num(shape.get("relative_l2")),
        judge_status=judge.get("provenance_status"),
        overrule=judge.get("overrule"),
        bounces=gate.get("bounces"),
        checker_seconds=_num(ctime.get("checker_seconds")),
        labelled=bool(lab.get("read")),
        gap1=sum(c[:1] == "1" for c in codes),
        labels=len(codes),
    )


def load_runs(runs_dir: Path) -> tuple[list[Run], dict[str, int]]:
    """All final runs (sorted by slot) and the number of void attempts per slot."""
    runs: list[Run] = []
    voids: dict[str, int] = {}
    for folder in sorted(p for p in runs_dir.iterdir() if p.is_dir() and SLOT_DIR.match(p.name)):
        if "_void" in folder.name:
            voids[folder.name[:3]] = voids.get(folder.name[:3], 0) + 1
            continue
        if (folder / "manifest.yaml").is_file():
            runs.append(read_run(folder))
    return runs, voids


def _median(values: Iterable[float | None]) -> float | None:
    xs = [v for v in values if v is not None]
    return statistics.median(xs) if xs else None


def _fmt(value: float | None, digits: int = 2) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def _table(header: Sequence[str], rows: Iterable[Sequence[object]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines


def _groups(runs: Sequence[Run]) -> list[tuple[str, str]]:
    return sorted({(r.model, r.arm) for r in runs}, key=lambda g: (g[0], g[1] != "baseline"))


def arm_table(runs: Sequence[Run], voids: dict[str, int]) -> list[str]:
    """Headline: per model and arm, outcomes, pass rate, median delta_norm, Gap-1 errors, time."""
    rows = []
    slot_of = {r.slot: (r.model, r.arm) for r in runs}
    for model, arm in _groups(runs):
        rs = [r for r in runs if (r.model, r.arm) == (model, arm)]
        n = len(rs)
        count = {o: sum(r.outcome == o for r in rs) for o in ("scored", "timeout", "crash")}
        void = sum(k for s, k in voids.items() if slot_of.get(s) == (model, arm))
        labelled = [r for r in rs if r.labelled]
        gap1 = sum(r.gap1 for r in labelled)
        gap1_runs = sum(r.gap1 > 0 for r in labelled)
        failed = sum(r.judge_status == "FAILED" for r in rs)
        checker = _median(r.checker_seconds for r in rs)
        rows.append(
            [
                model.removeprefix("claude-"),
                arm,
                n,
                f"{count['scored']}/{count['timeout']}/{count['crash']}",
                void,
                f"{sum(r.passed for r in rs)}/{n}",
                _fmt(_median(r.delta_norm for r in rs)),
                f"{gap1} in {gap1_runs}/{len(labelled)}" if labelled else "not labelled",
                failed,
                _fmt(_median(r.wall_hours for r in rs)),
                "—" if arm == "baseline" else _fmt(None if checker is None else checker / 60, 1),
            ]
        )
    header = [
        "Model",
        "Arm",
        "Runs",
        "Scored/timeout/crash",
        "Void (rerun)",
        "Pass (L2 < 0.33)",
        "Median Δ_norm",
        "Gap-1 errors (in runs / labelled)",
        "Judge FAILED",
        "Median hours",
        "Median checker min",
    ]
    return _table(header, rows)


def task_table(runs: Sequence[Run]) -> list[str]:
    """Median Δ_norm of the 3 runs per task, without vs with the checker."""
    rows = []
    for model in sorted({r.model for r in runs}):
        for task in sorted({r.task for r in runs}):
            cell = {}
            for arm in ("baseline", "checker"):
                rs = [r for r in runs if (r.model, r.task, r.arm) == (model, task, arm)]
                cell[arm] = (_median(r.delta_norm for r in rs), sum(r.passed for r in rs), len(rs))
            rows.append(
                [
                    model.removeprefix("claude-"),
                    task,
                    f"{_fmt(cell['baseline'][0])} ({cell['baseline'][1]}/{cell['baseline'][2]})",
                    f"{_fmt(cell['checker'][0])} ({cell['checker'][1]}/{cell['checker'][2]})",
                ]
            )
    header = ["Model", "Task", "Without: median Δ_norm (pass)", "With: median Δ_norm (pass)"]
    return _table(header, rows)


def run_table(runs: Sequence[Run]) -> list[str]:
    """One row per run."""
    rows = [
        [
            r.slot,
            r.model.removeprefix("claude-"),
            r.task,
            r.arm,
            r.rep,
            r.outcome,
            _fmt(r.wall_hours),
            _fmt(r.delta_norm),
            _fmt(r.norm_l2),
            _fmt(r.shape_l2),
            r.judge_status or "—",
            "—" if r.bounces is None else r.bounces,
            r.gap1 if r.labelled else "—",
        ]
        for r in sorted(runs, key=lambda r: r.slot)
    ]
    header = [
        "Slot",
        "Model",
        "Task",
        "Arm",
        "Rep",
        "Outcome",
        "Hours",
        "Δ_norm",
        "Norm L2",
        "Shape L2",
        "Judge",
        "Bounces",
        "Gap-1",
    ]
    return _table(header, rows)


def render_markdown(runs: Sequence[Run], voids: dict[str, int], version: str) -> str:
    """The full results page."""
    unlabelled = sum(not r.labelled for r in runs)
    lines = [
        "# Study B results",
        "",
        f"Generated by `python -m trustlayer.report study-b` at `{version}`. Never edit by hand.",
        "",
        f"{len(runs)} final runs, {sum(voids.values())} void attempts (rerun, not scored),"
        f" {unlabelled} runs not yet labelled. Setup and rules: `../README.md`."
        " Deviation from the paper: 32 threads and a 10 h limit, not 128 cores and 2.5 h.",
        "",
        "## By model and arm",
        "",
        *arm_table(runs, voids),
        "",
        "## By task (median of 3)",
        "",
        *task_table(runs),
        "",
        "## Every run",
        "",
        *run_table(runs),
        "",
    ]
    return "\n".join(lines)
