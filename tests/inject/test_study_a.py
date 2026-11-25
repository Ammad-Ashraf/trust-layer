"""Tests for Study A's injector (decision 0016 list plus the 0017 rows)."""

from __future__ import annotations

from pathlib import Path

import pytest

from trustlayer.checks import run_checks
from trustlayer.inject import (
    StudyConfigError,
    build_cases,
    load_study_config,
    load_task_inputs,
)
from trustlayer.ledger import CROSS_SECTION

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "experiments" / "02-study-a" / "config.yaml"
TASK_IDS = ("sus-16-034_sim-TChiWZ", "sus-16-046_sim-T5Wg", "sus-16-051_sim-T2tt_comp")


@pytest.fixture(scope="module")
def config():  # type: ignore[no-untyped-def]
    return load_study_config(CONFIG, ROOT)


def test_config_lists_the_three_study_a_tasks(config) -> None:  # type: ignore[no-untyped-def]
    assert tuple(t.task for t in config.tasks) == TASK_IDS
    assert config.c5_tolerance == 0.05


@pytest.mark.parametrize("index", range(3))
def test_clean_bins_match_the_hand_ledger_product(config, index: int) -> None:  # type: ignore[no-untyped-def]
    t = config.tasks[index]
    assert sum(t.bins) == pytest.approx(t.ledger.product().value, rel=0.002)


def test_every_listed_case_is_built_or_skipped_with_a_reason(config) -> None:  # type: ignore[no-untyped-def]
    for t in config.tasks:
        cases, skipped = build_cases(t, config.c5_tolerance)
        ids = {c.case_id for c in cases} | {s.case_id for s in skipped}
        assert {
            "1a-sigma-pb-as-fb",
            "1b-lo-generator",
            "1c-br-one-no-reason",
            "1d-mass-neighbour",
            "1e-null-bin",
            "clean",
            "br-one-with-reason",
            "0017-prospino-no-output",
            "0017-prospino-matches",
        } <= ids
        assert all(s.reason for s in skipped)
        assert len(ids) == len(cases) + len(skipped)


def test_br_one_tasks_skip_the_br_reason_cases(config) -> None:  # type: ignore[no-untyped-def]
    t5wg = config.tasks[1]
    _, skipped = build_cases(t5wg, 0.05)
    assert {s.case_id for s in skipped} == {"1c-br-one-no-reason", "br-one-with-reason"}


def test_each_injection_changes_exactly_one_thing(config) -> None:  # type: ignore[no-untyped-def]
    t = config.tasks[0]
    cases, _ = build_cases(t, 0.05)
    by_id = {c.case_id: c for c in cases}
    neighbour = by_id["1d-mass-neighbour"].inputs
    assert neighbour.ledger.quantities[CROSS_SECTION].value == 46.3533
    assert neighbour.submission is not None and neighbour.submission.bins == t.bins
    null = by_id["1e-null-bin"].inputs
    assert null.ledger == t.ledger
    assert null.submission is not None and None in null.submission.bins


def test_0016_cases_do_not_carry_prospino_evidence(config) -> None:  # type: ignore[no-untyped-def]
    cases, _ = build_cases(config.tasks[0], 0.05)
    assert all(c.inputs.prospino_results is None for c in cases if c.group == "0016")
    rows = {c.case_id: c for c in cases if c.group == "0017"}
    assert rows["0017-prospino-no-output"].inputs.prospino_results == ()
    assert len(rows["0017-prospino-mismatch"].inputs.prospino_results or ()) == 1


def test_injections_fail_and_near_misses_pass(config) -> None:  # type: ignore[no-untyped-def]
    for t in config.tasks:
        cases, _ = build_cases(t, config.c5_tolerance)
        for c in cases:
            failed = [r.check_id for r in run_checks(c.inputs) if not r.passed]
            assert bool(failed) == (c.kind == "injection"), (t.task, c.case_id, failed)


def test_stand_in_inputs_are_marked_provisional(config) -> None:  # type: ignore[no-untyped-def]
    assert config.tasks[0].provisional == ("generator_lo",)
    assert config.tasks[1].provisional == ()
    cases, _ = build_cases(config.tasks[0], 0.05)
    assert {c.case_id for c in cases if c.provisional} == {
        "1b-lo-generator",
        "1b-lo-false-label",
        "1e-bins-unscaled",
    }


def test_missing_neighbour_fails_loudly() -> None:
    raw = {
        "task": "sus-16-034_sim-TChiWZ",
        "ledger": "tasks/sus-16-034_sim-TChiWZ/ledger.yaml",
        "context": "integration/task-context/sus-16-034_sim-TChiWZ.yaml",
        "generator_lo": {"value": 1.0, "unit": "fb", "source": "x"},
    }
    with pytest.raises(StudyConfigError, match="neighbour"):
        load_task_inputs(raw, ROOT)


def test_incomplete_hand_ledger_fails_loudly() -> None:
    raw = {
        "task": "sus-16-051_sim-T2tt_SRG",
        "ledger": "tasks/sus-16-051_sim-T2tt_SRG/ledger.yaml",
        "context": "integration/task-context/sus-16-051_sim-T2tt_SRG.yaml",
        "neighbour": {"value": 1.0, "unit": "fb", "source": "x"},
        "generator_lo": {"value": 1.0, "unit": "fb", "source": "x"},
    }
    with pytest.raises(StudyConfigError, match="incomplete"):
        load_task_inputs(raw, ROOT)
