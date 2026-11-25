"""C4 Match. Guards 1d (mismatched input: sigma for the wrong process or mass point, wrong L).

Passes when sigma's `process` and every mass sigma depends on equal the task's benchmark (from
the public task card), any other recorded mass of a benchmark particle matches too, L equals
the task's luminosity, and the ledger's `task`, if set, is this task.
"""

from __future__ import annotations

from trustlayer.checks.base import CheckInputs, CheckResult, result
from trustlayer.ledger.model import CROSS_SECTION, LUMINOSITY, Entry
from trustlayer.ledger.names import canonical_particle, canonical_process
from trustlayer.ledger.units import UnitError

MASS_TOLERANCE_GEV = 0.5
LUMI_TOLERANCE = 0.001  # relative


def _fmt(masses: dict[str, float]) -> str:
    return ", ".join(f"{k}={v:g}" for k, v in masses.items()) or "none"


def _sigma_problems(sigma: Entry, inputs: CheckInputs) -> list[str]:
    ctx = inputs.task
    bench = f" (task benchmark {ctx.benchmark})" if ctx.benchmark else ""
    problems: list[str] = []
    process = canonical_process(sigma.process) if sigma.process else None
    if process is None:
        problems.append(
            f"cross_section has no known --process; this task's process is {ctx.process}{bench}"
        )
    elif process != ctx.process:
        problems.append(f"cross_section is for {process}, but this task is {ctx.process}{bench}")
    recorded: dict[str, float] = {}
    for particle, mass in sigma.masses_gev.items():
        name = canonical_particle(particle)
        if name is None:
            problems.append(f"cross_section mass for unknown particle {particle!r}")
        else:
            recorded[name] = mass
    for particle, mass in ctx.sigma_masses_gev.items():
        if particle not in recorded:
            problems.append(
                f"cross_section does not say which {particle} mass it is for; record "
                f"--mass {particle}=<GeV> (task: {particle}={mass:g}{bench})"
            )
    wrong = {
        p: m
        for p, m in recorded.items()
        if p in ctx.masses_gev and abs(m - ctx.masses_gev[p]) > MASS_TOLERANCE_GEV
    }
    if wrong:
        expected = {p: ctx.masses_gev[p] for p in wrong}
        problems.append(
            f"cross_section is for masses {_fmt(wrong)}, but the task's benchmark has "
            f"{_fmt(expected)}{bench}"
        )
    return problems


def _lumi_problem(lumi: Entry, inputs: CheckInputs) -> str | None:
    try:
        value_fb = lumi.quantity().canonical()
    except (ValueError, UnitError):
        return None  # C1 reports unit problems
    expected = inputs.task.luminosity_fb
    if abs(value_fb / expected - 1) > LUMI_TOLERANCE:
        return f"luminosity is {value_fb:g} fb^-1, but this task uses {expected:g} fb^-1"
    return None


def check_match(inputs: CheckInputs) -> CheckResult:
    """C4: sigma's process and masses, and L, match the task's public benchmark."""
    ledger = inputs.ledger
    problems: list[str] = []
    if ledger.task and ledger.task != inputs.task.task:
        problems.append(f"ledger is for task {ledger.task!r}, but this run is {inputs.task.task!r}")
    sigma = ledger.get(CROSS_SECTION)
    if sigma is not None and sigma.value is not None:
        problems += _sigma_problems(sigma, inputs)
    lumi = ledger.get(LUMINOSITY)
    if (
        lumi is not None
        and lumi.value is not None
        and lumi.unit is not None
        and (problem := _lumi_problem(lumi, inputs)) is not None
    ):
        problems.append(problem)
    return result("C4", "1d", problems)
