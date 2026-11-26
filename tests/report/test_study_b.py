"""Tests for trustlayer.report.study_b: reading run folders and the headline tables."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from trustlayer.report import study_b


def _run(
    root: Path,
    name: str,
    arm: str,
    outcome: str,
    norm_l2: float,
    labels: list[str] | None = None,
) -> None:
    d = root / name
    d.mkdir(parents=True)
    slot = {
        "id": name[:3],
        "model": "claude-sonnet-4-6",
        "task": "sus-16-034_sim-TChiWZ",
        "arm": arm,
        "rep": 1,
        "pilot": False,
    }
    man = {
        "slot": slot,
        "outcome": outcome,
        "wall_clock_hours": 1.0,
        "judge": {"provenance_status": "VERIFIED", "overrule": "NONE"},
    }
    if arm == "checker":
        man["gate"] = {"bounces": 1}
        man["checker_time"] = {"checker_seconds": 120.0}
    (d / "manifest.yaml").write_text(yaml.safe_dump(man))
    score = {"normalization": {"Delta": norm_l2, "relative_l2": norm_l2}, "shape": {}}
    (d / "score.json").write_text(json.dumps(score))
    if labels is not None:
        lab = {"read": "full", "labels": [{"code": c} for c in labels]}
        (d / "labels.yaml").write_text(yaml.safe_dump(lab))


def test_load_runs_skips_voids_and_counts_them(tmp_path: Path) -> None:
    _run(tmp_path, "S01_a_sonnet-4-6_baseline_1", "baseline", "scored", 0.5, ["1b", "3c"])
    _run(tmp_path, "S02_a_sonnet-4-6_checker_1", "checker", "scored", 0.2, [])
    _run(tmp_path, "S02_a_sonnet-4-6_checker_1_void1", "checker", "void", 0.9)
    (tmp_path / "R6-pilot-report.md").write_text("x")
    runs, voids = study_b.load_runs(tmp_path)
    assert [r.slot for r in runs] == ["S01", "S02"]
    assert voids == {"S02": 1}
    base, check = runs
    assert (base.gap1, base.labels, base.labelled, base.passed) == (1, 2, True, False)
    assert (check.gap1, check.passed, check.bounces, check.checker_seconds) == (0, True, 1, 120.0)


def test_timeouts_stay_in_and_unlabelled_runs_are_flagged(tmp_path: Path) -> None:
    _run(tmp_path, "S01_a_sonnet-4-6_baseline_1", "baseline", "timeout", 0.9)
    runs, voids = study_b.load_runs(tmp_path)
    page = study_b.render_markdown(runs, voids, "test")
    assert "0/1/0" in page
    assert "not labelled" in page
    assert "1 runs not yet labelled" in page


def test_headline_table_has_both_arms(tmp_path: Path) -> None:
    _run(tmp_path, "S01_a_sonnet-4-6_baseline_1", "baseline", "scored", 0.5, ["1b"])
    _run(tmp_path, "S02_a_sonnet-4-6_checker_1", "checker", "scored", 0.2, [])
    runs, voids = study_b.load_runs(tmp_path)
    table = "\n".join(study_b.arm_table(runs, voids))
    assert "| sonnet-4-6 | baseline | 1 | 1/0/0 | 0 | 0/1 | 0.50 | 1 in 1/1 |" in table
    assert "| sonnet-4-6 | checker | 1 | 1/0/0 | 0 | 1/1 | 0.20 | 0 in 0/1 |" in table
