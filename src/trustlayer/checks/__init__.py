"""Checks C1-C5. Each is a pure function `CheckInputs -> CheckResult`, guarding sub-gaps 1a-1e.

The registry `CHECKS` is what the gate runs; it knows nothing about individual checks.
Rules: docs/design/checker-v0.md section 4.
"""

from trustlayer.checks.base import (
    DEFAULT_C5_TOLERANCE,
    Check,
    CheckInputs,
    CheckResult,
)
from trustlayer.checks.c1_units import check_units
from trustlayer.checks.c2_source import check_source
from trustlayer.checks.c3_complete import check_complete
from trustlayer.checks.c4_match import check_match
from trustlayer.checks.c5_carried import check_carried
from trustlayer.checks.inputs import (
    InputsError,
    Submission,
    TaskContext,
    load_submission,
    load_task_context,
)

CHECKS: tuple[Check, ...] = (check_units, check_source, check_complete, check_match, check_carried)


def run_checks(inputs: CheckInputs, checks: tuple[Check, ...] = CHECKS) -> list[CheckResult]:
    """Run every registered check and return the results in order."""
    return [check(inputs) for check in checks]


__all__ = [
    "CHECKS",
    "DEFAULT_C5_TOLERANCE",
    "Check",
    "CheckInputs",
    "CheckResult",
    "InputsError",
    "Submission",
    "TaskContext",
    "check_carried",
    "check_complete",
    "check_match",
    "check_source",
    "check_units",
    "load_submission",
    "load_task_context",
    "run_checks",
]
