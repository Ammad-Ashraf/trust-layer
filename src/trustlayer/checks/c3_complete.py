"""C3 Complete formula. Guards 1c (a missing factor, e.g. the branching fraction forgotten).

Passes when sigma, L, BR and eps all have values; sigma and L are positive; BR and eps lie in
(0, 1], with a value of exactly 1 only when a `reason` says why; corrections are positive; and
n_pass / n_gen, when given, agree with eps within 1%.
"""

from __future__ import annotations

from trustlayer.checks.base import CheckInputs, CheckResult, result
from trustlayer.ledger.model import (
    BRANCHING_FRACTION,
    CROSS_SECTION,
    EFFICIENCY,
    FACTORS,
    LUMINOSITY,
    Entry,
)

EPS_MATCH = 0.01

_HOW = {
    CROSS_SECTION: "bin/record-quantity cross_section --value V --unit fb "
    "--source-type prospino --process P --mass PARTICLE=GEV --source ...",
    LUMINOSITY: "bin/record-quantity luminosity --value V --unit fb^-1 --source ...",
    BRANCHING_FRACTION: "bin/record-quantity branching_fraction --value V --source ... "
    "(or --value 1 --reason '...' if all decays are in your simulation)",
    EFFICIENCY: "bin/record-quantity efficiency --value V --n-pass N --n-gen N --source ...",
}


def _fraction_problems(entry: Entry) -> list[str]:
    assert entry.value is not None
    if not 0 < entry.value <= 1:
        return [f"{entry.name} = {entry.value:g} must lie between 0 and 1"]
    if entry.value == 1 and not (entry.reason and entry.reason.strip()):
        return [f"{entry.name} = 1 without a reason: say why it is 1, or record the real value"]
    return []


def _count_problems(entry: Entry) -> list[str]:
    if entry.n_pass is None and entry.n_gen is None:
        return []
    if entry.n_pass is None or entry.n_gen is None or entry.n_gen <= 0:
        return ["efficiency: give both n_pass and n_gen (n_gen > 0), or neither"]
    assert entry.value is not None
    ratio = entry.n_pass / entry.n_gen
    if abs(entry.value - ratio) > EPS_MATCH * max(ratio, 1e-12):
        return [
            f"efficiency {entry.value:g} does not match n_pass/n_gen = "
            f"{entry.n_pass:g}/{entry.n_gen:g} = {ratio:g}"
        ]
    return []


def check_complete(inputs: CheckInputs) -> CheckResult:
    """C3: every factor of sigma*L*BR*eps is recorded, in range, and explained when equal to 1."""
    ledger = inputs.ledger
    problems = [f"{name} is missing. Record it: {_HOW[name]}" for name in ledger.missing_factors()]
    for name in FACTORS:
        entry = ledger.get(name)
        if entry is None or entry.value is None:
            continue
        if name in (CROSS_SECTION, LUMINOSITY) and entry.value <= 0:
            problems.append(f"{name} = {entry.value:g} must be positive")
        if name in (BRANCHING_FRACTION, EFFICIENCY):
            problems += _fraction_problems(entry)
        if name == EFFICIENCY:
            problems += _count_problems(entry)
    for corr in ledger.corrections:
        if corr.value is None or corr.value <= 0:
            problems.append(f"correction {corr.name!r} needs a positive value")
    return result("C3", "1c", problems)
