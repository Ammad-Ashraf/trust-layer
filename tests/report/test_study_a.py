"""Tests for the Study A report: scoring, tables and the CLI's output files."""

from __future__ import annotations

from pathlib import Path

import yaml

from trustlayer.inject import load_study_config
from trustlayer.report.__main__ import main
from trustlayer.report.study_a import catch_table, run_study, to_records

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments" / "02-study-a" / "config.yaml"


def test_study_a_scores_every_case() -> None:
    result = run_study(load_study_config(CONFIG, ROOT))
    injections = [o for o in result.outcomes if o.case.kind == "injection"]
    near = [o for o in result.outcomes if o.case.kind == "near_miss"]
    assert injections and all(o.flagged for o in injections)
    assert near and not any(o.flagged for o in near)
    assert len(result.skipped) == 4


def test_catch_table_counts_the_own_check_separately() -> None:
    result = run_study(load_study_config(CONFIG, ROOT))
    rows = {line.split(" | ")[0].strip("| "): line for line in catch_table(result.outcomes)}
    assert "C1: 0/6 (0%)" in rows["1a"]  # C1 can't see a valid-but-wrong unit; C4/C5 catch it
    assert "6/6 (100%)" in rows["1a"]


def test_records_are_plain_data() -> None:
    result = run_study(load_study_config(CONFIG, ROOT))
    records = to_records(result)
    assert yaml.safe_load(yaml.safe_dump(records)) == records
    assert {r["group"] for r in records} == {"0016", "0017"}


def test_cli_writes_the_tables_and_the_cases(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["study-a", "--root", str(ROOT), "--out", str(tmp_path)]) == 0
    page = (tmp_path / "study-a.md").read_text(encoding="utf-8")
    assert "Do not edit by hand" in page and "not pre-registered" in page
    data = yaml.safe_load((tmp_path / "cases.yaml").read_text(encoding="utf-8"))
    assert data["tau"] == 0.05 and len(data["cases"]) > 40
    assert "false alarms" in capsys.readouterr().out
