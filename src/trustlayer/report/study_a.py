"""Score Study A's cases with the checks and render the results tables (never hand-edited).

Measured (decision 0016): the catch rate per sub-gap on the injected copies, and the
false-alarm rate on the clean and near-miss copies. The 0017 rows are reported in their own
table. A tau sweep is added as an exploratory table and labelled as not pre-registered.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import Any

from trustlayer.checks import run_checks
from trustlayer.inject import Case, Skipped, StudyConfig, build_cases
from trustlayer.ledger import UnitError

SUBGAPS = ("1a", "1b", "1c", "1d", "1e")
OWN_CHECK = {"1a": "C1", "1b": "C2", "1c": "C3", "1d": "C4", "1e": "C5"}
CHECK_IDS = ("C1", "C2", "C3", "C4", "C5")
TAU_SWEEP = (0.01, 0.02, 0.05, 0.10, 0.20)


@dataclass(frozen=True)
class Outcome:
    """What the checks said about one case."""

    case: Case
    failing: tuple[str, ...]
    ratio: float | None  # sum(bins) / ledger product; None if not computable

    @property
    def flagged(self) -> bool:
        return bool(self.failing)


@dataclass(frozen=True)
class StudyResult:
    """All outcomes plus the cases that did not apply."""

    tau: float
    outcomes: tuple[Outcome, ...]
    skipped: tuple[Skipped, ...]
    provisional: tuple[str, ...]  # "task: input" pairs that are stand-ins


def _ratio(case: Case) -> float | None:
    bins = case.inputs.submission.bins if case.inputs.submission else ()
    if not bins or any(b is None for b in bins):
        return None
    try:
        product = case.inputs.ledger.product()
    except (ValueError, UnitError):
        return None
    if not product.unit_free or product.value <= 0:
        return None
    return sum(b for b in bins if b is not None) / product.value


def score(case: Case) -> Outcome:
    """Run every registered check on one case."""
    failing = tuple(r.check_id for r in run_checks(case.inputs) if not r.passed)
    return Outcome(case, failing, _ratio(case))


def run_study(config: StudyConfig, tau: float | None = None) -> StudyResult:
    """Build every task's cases, score them, and collect skips and stand-in inputs."""
    tau = config.c5_tolerance if tau is None else tau
    outcomes: list[Outcome] = []
    skipped: list[Skipped] = []
    for t in config.tasks:
        cases, skips = build_cases(t, tau, config.fabricated_sigma_divisor)
        outcomes.extend(score(c) for c in cases)
        skipped.extend(skips)
    provisional = tuple(f"{t.task}: {p}" for t in config.tasks for p in t.provisional)
    return StudyResult(tau, tuple(outcomes), tuple(skipped), provisional)


# --- tables -----------------------------------------------------------------------------------


def _pick(outcomes: Iterable[Outcome], group: str, kind: str) -> list[Outcome]:
    return [o for o in outcomes if o.case.group == group and o.case.kind == kind]


def _rate(k: int, n: int) -> str:
    return f"{k}/{n} ({k / n:.0%})" if n else "—"


def _table(header: Sequence[str], rows: Iterable[Sequence[object]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return out


def catch_table(outcomes: Sequence[Outcome]) -> list[str]:
    """Catch rate per sub-gap on the 0016 injections, and how often its own check fired."""
    inj = _pick(outcomes, "0016", "injection")
    rows: list[list[object]] = []
    for sg in SUBGAPS:
        mine = [o for o in inj if o.case.subgap == sg]
        own = sum(OWN_CHECK[sg] in o.failing for o in mine)
        rows.append(
            [
                sg,
                len(mine),
                _rate(sum(o.flagged for o in mine), len(mine)),
                f"{OWN_CHECK[sg]}: {_rate(own, len(mine))}",
            ]
        )
    rows.append(["**all**", len(inj), _rate(sum(o.flagged for o in inj), len(inj)), ""])
    return _table(
        ("Sub-gap", "Injected copies", "Caught (any check)", "Caught by its own check"), rows
    )


def false_alarm_table(outcomes: Sequence[Outcome], group: str = "0016") -> list[str]:
    """False alarms on the clean and near-miss copies, per task."""
    near = _pick(outcomes, group, "near_miss")
    tasks = sorted({o.case.task for o in near})
    rows: list[list[object]] = [
        [
            t,
            len(m := [o for o in near if o.case.task == t]),
            _rate(sum(o.flagged for o in m), len(m)),
        ]
        for t in tasks
    ]
    rows.append(["**all**", len(near), _rate(sum(o.flagged for o in near), len(near))])
    return _table(("Task", "Clean / near-miss copies", "False alarms"), rows)


def check_table(outcomes: Sequence[Outcome]) -> list[str]:
    """How often each check fired, on injections and on near-misses (all groups)."""
    inj = [o for o in outcomes if o.case.kind == "injection"]
    near = [o for o in outcomes if o.case.kind == "near_miss"]
    rows = [
        [
            c,
            f"{sum(c in o.failing for o in inj)}/{len(inj)}",
            f"{sum(c in o.failing for o in near)}/{len(near)}",
            f"{sum(o.failing == (c,) for o in inj)}",
        ]
        for c in CHECK_IDS
    ]
    return _table(
        ("Check", "Fired on injections", "Fired on near-misses", "Only check that fired"), rows
    )


def _show_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "—"
    if 0.5 <= ratio <= 2:
        return f"{ratio - 1:+.1%}"
    return f"×{ratio:.4g}" if ratio >= 1 else f"×{ratio:.2g}"


def case_table(outcomes: Sequence[Outcome]) -> list[str]:
    """One row per case: what was broken and which checks failed."""
    rows = []
    for o in outcomes:
        dev = _show_ratio(o.ratio)
        mark = " †" if o.case.provisional else ""
        rows.append(
            [
                o.case.task,
                o.case.group,
                f"`{o.case.case_id}`{mark}",
                o.case.subgap,
                o.case.description,
                ", ".join(o.failing) or "none",
                dev,
            ]
        )
    return _table(
        (
            "Task",
            "Group",
            "Case",
            "Sub-gap",
            "What was broken",
            "Checks that failed",
            "Bins vs ledger",
        ),
        rows,
    )


def added_0017_table(outcomes: Sequence[Outcome]) -> list[str]:
    """The 0017 rows: Prospino labels without, and with, the run's own Prospino output."""
    inj = _pick(outcomes, "0017", "injection")
    near = _pick(outcomes, "0017", "near_miss")
    return _table(
        ("Copies", "Count", "Result"),
        [
            [
                "injections (Prospino label not backed by the run)",
                len(inj),
                "caught " + _rate(sum(x.flagged for x in inj), len(inj)),
            ],
            [
                "near-miss (label backed by the run's Prospino output)",
                len(near),
                "false alarms " + _rate(sum(x.flagged for x in near), len(near)),
            ],
        ],
    )


def tau_sweep_table(config: StudyConfig) -> list[str]:
    """Exploratory: the same 0016 cases at other tolerances (not pre-registered)."""
    rows = []
    for tau in TAU_SWEEP:
        outs = run_study(replace(config, c5_tolerance=tau)).outcomes
        inj, near = _pick(outs, "0016", "injection"), _pick(outs, "0016", "near_miss")
        rows.append(
            [
                f"{tau:.0%}" + (" (fixed)" if tau == config.c5_tolerance else ""),
                _rate(sum(o.flagged for o in inj), len(inj)),
                _rate(sum(o.flagged for o in near), len(near)),
            ]
        )
    return _table(("tau", "Injections caught", "False alarms"), rows)


def render_markdown(result: StudyResult, config: StudyConfig, meta: dict[str, str]) -> str:
    """The whole results page. `meta` gives the code version and the command that made it."""
    o = result.outcomes
    lines = [
        "# Study A results",
        "",
        f"Generated by `{meta.get('command', 'python -m trustlayer.report study-a')}` at code "
        f"version `{meta.get('version', 'unknown')}`. **Do not edit by hand**; rerun instead.",
        f"Tolerance tau = {result.tau:.0%} (fixed by decision 0016). Tasks: "
        + ", ".join(f"`{t.task}`" for t in config.tasks)
        + ".",
        "",
        "## Catch rate per sub-gap (decision 0016 injections)",
        "",
        *catch_table(o),
        "",
        "## False alarms (decision 0016 clean and near-miss copies)",
        "",
        *false_alarm_table(o),
        "",
        "## Added after 0016 (decision 0017), reported separately",
        "",
        *added_0017_table(o),
        "",
        "## Which check fired",
        "",
        *check_table(o),
        "",
        "## Every case",
        "",
        *case_table(o),
        "",
        '"Bins vs ledger" is how far the sum of the bins is from sigma x L x BR x eps (C5 compares '
        "its size with tau); — means it can't be computed (a factor or a bin is missing).",
    ]
    if result.provisional:
        lines += [
            "",
            "† uses a stand-in input, to be replaced: "
            + "; ".join(result.provisional)
            + ". Only the 'Bins vs ledger' size depends on it, not which checks fail, "
            "as long as the stand-in differs from the correct value by more than tau.",
        ]
    if result.skipped:
        lines += [
            "",
            "## Not applicable",
            "",
            *_table(
                ("Task", "Case", "Why"),
                [[s.task, f"`{s.case_id}`", s.reason] for s in result.skipped],
            ),
        ]
    lines += [
        "",
        "## Exploratory: other tolerances (not pre-registered)",
        "",
        *tau_sweep_table(config),
        "",
    ]
    return "\n".join(lines)


def to_records(result: StudyResult) -> list[dict[str, Any]]:
    """Machine-readable rows (one per case) for results/cases.yaml."""
    return [
        {
            "task": x.case.task,
            "case": x.case.case_id,
            "group": x.case.group,
            "kind": x.case.kind,
            "subgap": x.case.subgap,
            "description": x.case.description,
            "failing_checks": list(x.failing),
            "flagged": x.flagged,
            "bins_over_ledger": None if x.ratio is None else round(x.ratio, 6),
            "provisional_input": x.case.provisional,
        }
        for x in result.outcomes
    ]
