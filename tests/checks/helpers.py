"""Shared test inputs: the sus-16-034 hand ledger, its public task context and a consistent
submission built from the ledger's own per-bin values."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from trustlayer.checks import CheckInputs, Submission, load_task_context, run_checks
from trustlayer.ledger import Entry, Ledger, load_ledger

ROOT = Path(__file__).resolve().parents[2]
TCHIWZ_LEDGER = ROOT / "tasks" / "sus-16-034_sim-TChiWZ" / "ledger.yaml"
TCHIWZ_CONTEXT = ROOT / "integration" / "task-context" / "sus-16-034_sim-TChiWZ.yaml"
TCHIWZ_BINS = (0.45, 1.37, 1.65, 1.94)  # the hand ledger's per_bin values (sum 5.41)


def clean_ledger() -> Ledger:
    return load_ledger(TCHIWZ_LEDGER)


def inputs(
    ledger: Ledger | None = None,
    bins: tuple[float | None, ...] = TCHIWZ_BINS,
    **kwargs: Any,
) -> CheckInputs:
    return CheckInputs(
        ledger=ledger if ledger is not None else clean_ledger(),
        task=load_task_context(TCHIWZ_CONTEXT),
        submission=Submission(Path("/ws/results/histogram.yaml"), bins),
        **kwargs,
    )


def with_entry(ledger: Ledger, name: str, **changes: Any) -> Ledger:
    entry = ledger.quantities[name]
    return replace(ledger, quantities={**ledger.quantities, name: replace(entry, **changes)})


def without(ledger: Ledger, name: str) -> Ledger:
    return replace(ledger, quantities={k: v for k, v in ledger.quantities.items() if k != name})


def with_quantity(ledger: Ledger, entry: Entry) -> Ledger:
    return replace(ledger, quantities={**ledger.quantities, entry.name: entry})


def failing(check_inputs: CheckInputs) -> set[str]:
    return {r.check_id for r in run_checks(check_inputs) if not r.passed}
