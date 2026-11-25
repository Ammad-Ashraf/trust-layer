"""The one interface every check shares (engineering standards section 3).

A check is a pure function `CheckInputs -> CheckResult`. It reads only the ledger, the public
task context and the agent's submitted results file, never Collider-Bench internals.
Adding a check means adding a function to the registry; the gate doesn't change.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from trustlayer.checks.inputs import Submission, TaskContext
from trustlayer.checks.prospino import ProspinoResult
from trustlayer.ledger.model import Ledger

DEFAULT_C5_TOLERANCE = 0.05
"""Fixed by decision 0016 before the checks existed; the experiment config sets the value used."""


@dataclass(frozen=True)
class CheckInputs:
    """Everything a check may look at.

    `submission` is None when no results file could be read; `submission_error` says why.
    `ledger_path` is only used to write absolute paths into messages.
    `prospino_results` holds the Prospino runs found in this run's scratch folders (decision
    0017). None means "not collected" (offline use, e.g. Study A without a run folder), so C2
    can't verify a Prospino label; an empty tuple means "collected, none found".
    """

    ledger: Ledger
    task: TaskContext
    submission: Submission | None
    submission_error: str | None = None
    ledger_path: Path | None = None
    c5_tolerance: float = DEFAULT_C5_TOLERANCE
    prospino_results: tuple[ProspinoResult, ...] | None = None


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one check: id (C1..C5), the sub-gap it guards, pass/fail and messages.

    Messages quote only the agent's own numbers and the public task facts, never references.
    """

    check_id: str
    subgap: str
    passed: bool
    messages: tuple[str, ...] = field(default_factory=tuple)


Check = Callable[[CheckInputs], CheckResult]


def result(
    check_id: str, subgap: str, problems: list[str], notes: list[str] | None = None
) -> CheckResult:
    """Pass when `problems` is empty; messages are the problems, or the notes when passing."""
    if problems:
        return CheckResult(check_id, subgap, False, tuple(problems))
    return CheckResult(check_id, subgap, True, tuple(notes or ()))
