"""Study A's broken copies: one known mistake per copy, built from a correct hand ledger.

The injection list is fixed by decision 0016 (docs/design/checker-v0.md section 7); the two
rows added by decision 0017 are kept in their own group so they are reported separately.
Every case is generic: it uses only the hand ledger, the public task context and two public
numbers per task from the experiment config (sigma at a neighbouring mass point and the
generator's LO sigma). A case that makes no sense for a task (e.g. "BR = 1 without a reason"
where BR really is 1) is returned as skipped with the reason, never silently dropped.

Ledger injections keep the clean bins (as if only the ledger were wrong); the 1e injections
change only the bins.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

import yaml

from trustlayer.checks import CheckInputs, ProspinoResult, Submission, TaskContext
from trustlayer.checks.inputs import load_task_context
from trustlayer.ledger import (
    BRANCHING_FRACTION,
    CROSS_SECTION,
    EFFICIENCY,
    GENERATOR_CROSS_SECTION,
    LUMINOSITY,
    Entry,
    Ledger,
    load_ledger,
)

Group = Literal["0016", "0017"]
Kind = Literal["injection", "near_miss"]
SUBMISSION_PATH = Path("results/histogram.yaml")


class StudyConfigError(ValueError):
    """The Study A config or a hand ledger is missing something the injections need."""


@dataclass(frozen=True)
class TaskInputs:
    """One task's correct ledger and the public numbers its injections need."""

    task: str
    ledger: Ledger
    context: TaskContext
    bins: tuple[float, ...]
    neighbour: Entry
    generator_lo: Entry
    prospino_process: str
    provisional: tuple[str, ...] = ()


@dataclass(frozen=True)
class Case:
    """One copy given to the checks: an injection (must be caught) or a near-miss (must pass)."""

    task: str
    case_id: str
    subgap: str
    group: Group
    kind: Kind
    description: str
    inputs: CheckInputs
    provisional: bool = False


@dataclass(frozen=True)
class Skipped:
    """A listed case that does not apply to this task, with the reason."""

    task: str
    case_id: str
    group: Group
    reason: str


@dataclass(frozen=True)
class StudyConfig:
    """The parts of experiments/02-study-a/config.yaml the injector uses."""

    c5_tolerance: float
    fabricated_sigma_divisor: float
    tasks: tuple[TaskInputs, ...]


# --- loading ----------------------------------------------------------------------------------


def _need(raw: Mapping[str, Any], key: str, where: str) -> Any:
    if raw.get(key) is None:
        raise StudyConfigError(f"{where}: '{key}' is required")
    return raw[key]


def _sigma_entry(raw: Mapping[str, Any], name: str, source_type: str, where: str) -> Entry:
    return Entry(
        name=name,
        value=float(_need(raw, "value", where)),
        unit=str(_need(raw, "unit", where)),
        source=str(_need(raw, "source", where)),
        source_type=source_type,
        masses_gev={str(k): float(v) for k, v in (raw.get("masses_gev") or {}).items()},
    )


def _clean_bins(ledger: Ledger, where: str) -> tuple[float, ...]:
    expected = ledger.extra.get("expected_events")
    per_bin = expected.get("per_bin") if isinstance(expected, Mapping) else None
    if not isinstance(per_bin, Mapping) or not per_bin:
        raise StudyConfigError(f"{where}: hand ledger has no expected_events.per_bin")
    return tuple(float(v) for v in per_bin.values())


def load_task_inputs(raw: Mapping[str, Any], root: Path) -> TaskInputs:
    """Read one `tasks:` entry of the config: ledger, context and the two extra public numbers."""
    task = str(_need(raw, "task", "tasks entry"))
    ledger = load_ledger(root / str(_need(raw, "ledger", task)))
    context = load_task_context(root / str(_need(raw, "context", task)))
    sigma = ledger.get(CROSS_SECTION)
    if sigma is None or ledger.missing_factors():
        raise StudyConfigError(f"{task}: hand ledger is incomplete: {ledger.missing_factors()}")
    neighbour_raw = _need(raw, "neighbour", task)
    lo_raw = _need(raw, "generator_lo", task)
    neighbour = replace(
        _sigma_entry(neighbour_raw, CROSS_SECTION, sigma.source_type or "xsec_wg", task),
        process=sigma.process,
    )
    provisional = tuple(
        key
        for key, part in (("neighbour", neighbour_raw), ("generator_lo", lo_raw))
        if part.get("provisional")
    )
    return TaskInputs(
        task=task,
        ledger=ledger,
        context=context,
        bins=_clean_bins(ledger, task),
        neighbour=neighbour,
        generator_lo=_sigma_entry(lo_raw, GENERATOR_CROSS_SECTION, "generator", task),
        prospino_process=str(raw.get("prospino_process") or "xx"),
        provisional=provisional,
    )


def load_study_config(path: Path, root: Path) -> StudyConfig:
    """Load the Study A config; paths inside it are relative to the repo `root`."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise StudyConfigError(f"{path}: not a mapping")
    tasks = data.get("tasks") or []
    if not tasks:
        raise StudyConfigError(f"{path}: no tasks listed")
    return StudyConfig(
        c5_tolerance=float(_need(data, "c5_tolerance", str(path))),
        fabricated_sigma_divisor=float(data.get("fabricated_sigma_divisor") or 201),
        tasks=tuple(load_task_inputs(t, root) for t in tasks),
    )


# --- building cases ---------------------------------------------------------------------------


def _set(ledger: Ledger, name: str, **changes: Any) -> Ledger:
    entry = ledger.quantities[name]
    return replace(ledger, quantities={**ledger.quantities, name: replace(entry, **changes)})


def _put(ledger: Ledger, entry: Entry) -> Ledger:
    return replace(ledger, quantities={**ledger.quantities, entry.name: entry})


def _drop(ledger: Ledger, name: str) -> Ledger:
    return replace(ledger, quantities={k: v for k, v in ledger.quantities.items() if k != name})


def _sigma_fb(ledger: Ledger) -> float:
    return ledger.quantities[CROSS_SECTION].quantity().canonical()


def _masses(entry: Entry) -> str:
    return ", ".join(f"{k} {v:g}" for k, v in entry.masses_gev.items())


def _round2(x: float) -> float:
    return float(f"{x:.2g}")


class _Builder:
    """Collects the cases and skips for one task."""

    def __init__(self, t: TaskInputs, tau: float) -> None:
        self.t = t
        self.tau = tau
        self.cases: list[Case] = []
        self.skipped: list[Skipped] = []

    def add(
        self,
        case_id: str,
        subgap: str,
        kind: Kind,
        description: str,
        ledger: Ledger | None = None,
        bins: tuple[float | None, ...] | None = None,
        group: Group = "0016",
        prospino: tuple[ProspinoResult, ...] | None = None,
        provisional: bool = False,
    ) -> None:
        inputs = CheckInputs(
            ledger=ledger if ledger is not None else self.t.ledger,
            task=self.t.context,
            submission=Submission(SUBMISSION_PATH, bins if bins is not None else self.t.bins),
            c5_tolerance=self.tau,
            prospino_results=prospino,
        )
        self.cases.append(
            Case(self.t.task, case_id, subgap, group, kind, description, inputs, provisional)
        )

    def skip(self, case_id: str, reason: str, group: Group = "0016") -> None:
        self.skipped.append(Skipped(self.t.task, case_id, group, reason))

    def prospino_run(self, nlo_fb: float) -> ProspinoResult:
        folder = f"{self.t.prospino_process}-studya"
        return ProspinoResult(
            path=Path("prospino_scratch") / folder / "prospino.dat",
            process=self.t.prospino_process,
            lo_pb=self.t.generator_lo.quantity().canonical() / 1000,
            nlo_pb=nlo_fb / 1000,
        )


def _injections_0016(b: _Builder) -> None:
    t, clean = b.t, b.t.ledger
    sigma_fb = _sigma_fb(clean)
    br = clean.quantities[BRANCHING_FRACTION]
    lo = t.generator_lo
    lo_fb = lo.quantity().canonical()
    lo_prov = "generator_lo" in t.provisional

    # 1a: a pb number written with an fb label; L entered in pb^-1 without converting.
    b.add(
        "1a-sigma-pb-as-fb",
        "1a",
        "injection",
        "sigma's pb value written with unit fb",
        _set(clean, CROSS_SECTION, value=sigma_fb / 1000, unit="fb"),
    )
    lumi = clean.quantities[LUMINOSITY]
    b.add(
        "1a-lumi-pb-inverse",
        "1a",
        "injection",
        "L's fb^-1 value written with unit pb^-1",
        _set(clean, LUMINOSITY, value=lumi.quantity().canonical(), unit="pb^-1"),
    )

    # 1b: the generator's LO sigma used, labelled honestly, and under a false prospino label.
    for case_id, label, what in (
        ("1b-lo-generator", "generator", "LO sigma used, labelled generator"),
        ("1b-lo-false-label", "prospino", "LO sigma used, falsely labelled prospino"),
    ):
        wrong = _set(
            clean, CROSS_SECTION, value=lo_fb, unit="fb", source_type=label, source=lo.source
        )
        b.add(case_id, "1b", "injection", what, _put(wrong, lo), provisional=lo_prov)

    # 1c: BR forgotten; BR set to 1 without a reason.
    b.add(
        "1c-br-removed",
        "1c",
        "injection",
        "branching fraction not recorded",
        _drop(clean, BRANCHING_FRACTION),
    )
    if br.value == 1.0:
        b.skip(
            "1c-br-one-no-reason",
            "BR really is 1 in this simplified model; dropping the reason is not a counting error",
        )
    else:
        b.add(
            "1c-br-one-no-reason",
            "1c",
            "injection",
            "BR set to 1 with no reason",
            _set(clean, BRANCHING_FRACTION, value=1.0, reason=None),
        )

    # 1d: sigma read at the neighbouring mass point; L = 36.1 (another dataset's value).
    b.add(
        "1d-mass-neighbour",
        "1d",
        "injection",
        f"sigma taken at the neighbouring mass point ({_masses(t.neighbour)} GeV)",
        _put(clean, t.neighbour),
    )
    b.add(
        "1d-lumi-36.1",
        "1d",
        "injection",
        "L = 36.1 fb^-1 instead of 35.9",
        _set(clean, LUMINOSITY, value=36.1),
    )

    # 1e: the bins keep an earlier normalization (LO sigma, before the fix); one bin null.
    scale = lo_fb / sigma_fb
    b.add(
        "1e-bins-unscaled",
        "1e",
        "injection",
        "bins left at the earlier LO normalization after sigma was fixed",
        bins=tuple(x * scale for x in t.bins),
        provisional=lo_prov,
    )
    nulled: list[float | None] = list(t.bins)
    nulled[len(nulled) // 2] = None
    b.add("1e-null-bin", "1e", "injection", "one bin left null", bins=tuple(nulled))


def _near_misses_0016(b: _Builder) -> None:
    clean = b.t.ledger
    sigma_fb = _sigma_fb(clean)
    br = clean.quantities[BRANCHING_FRACTION]
    eps = clean.quantities[EFFICIENCY]
    b.add("clean", "clean", "near_miss", "the correct ledger")
    b.add(
        "sigma-in-pb-converted",
        "clean",
        "near_miss",
        "sigma recorded in pb, correctly",
        _set(clean, CROSS_SECTION, value=sigma_fb / 1000, unit="pb"),
    )
    if br.value == 1.0 or br.value is None or eps.value is None:
        b.skip("br-one-with-reason", "BR is already 1 with a reason in the correct ledger")
    else:
        folded = _set(
            clean,
            BRANCHING_FRACTION,
            value=1.0,
            reason="the decay requirement is folded into the efficiency",
        )
        b.add(
            "br-one-with-reason",
            "clean",
            "near_miss",
            "BR = 1 with BR folded into eps",
            _set(folded, EFFICIENCY, value=eps.value * br.value),
        )
    name = BRANCHING_FRACTION if br.value not in (None, 1.0) else EFFICIENCY
    value = clean.quantities[name].value
    assert value is not None  # checked by load_task_inputs
    b.add(
        "rounded-2-sig-figs",
        "clean",
        "near_miss",
        f"{name} rounded to 2 significant figures ({value:g} -> {_round2(value):g})",
        _set(clean, name, value=_round2(value)),
    )


def _rows_0017(b: _Builder, divisor: float) -> None:
    clean = b.t.ledger
    sigma_fb = _sigma_fb(clean)
    invented = _set(
        clean,
        CROSS_SECTION,
        value=sigma_fb / divisor,
        unit="fb",
        source_type="prospino",
        source=f"bin/prospino {b.t.prospino_process} NLO",
    )
    b.add(
        "0017-prospino-no-output",
        "1b",
        "injection",
        f"invented sigma (correct / {divisor:g}) labelled prospino; Prospino never ran",
        invented,
        group="0017",
        prospino=(),
    )
    b.add(
        "0017-prospino-mismatch",
        "1b",
        "injection",
        f"invented sigma (correct / {divisor:g}) labelled prospino; Prospino ran and disagrees",
        invented,
        group="0017",
        prospino=(b.prospino_run(sigma_fb),),
    )
    honest = _set(
        clean,
        CROSS_SECTION,
        value=sigma_fb,
        unit="fb",
        source_type="prospino",
        source=f"bin/prospino {b.t.prospino_process} NLO",
    )
    b.add(
        "0017-prospino-matches",
        "clean",
        "near_miss",
        "sigma labelled prospino and equal to the run's Prospino NLO result",
        honest,
        group="0017",
        prospino=(b.prospino_run(sigma_fb),),
    )


def build_cases(
    t: TaskInputs, c5_tolerance: float, fabricated_sigma_divisor: float = 201
) -> tuple[list[Case], list[Skipped]]:
    """All Study A cases for one task (0016 table, then the 0017 rows), plus the skipped ones.

    The 0016 cases run with `prospino_results=None` (C2 as fixed in 0016 cannot verify a label);
    the 0017 rows carry the run's Prospino evidence explicitly.
    """
    b = _Builder(t, c5_tolerance)
    _injections_0016(b)
    _near_misses_0016(b)
    _rows_0017(b, fabricated_sigma_divisor)
    return b.cases, b.skipped
