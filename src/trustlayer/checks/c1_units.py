"""C1 Units. Guards 1a (wrong units, e.g. pb used as fb, a 1000x error).

Passes when every recorded factor has a known unit of the right kind: sigma is a cross section
(fb, pb), L an inverse cross section (fb^-1, pb^-1), BR, eps and corrections dimensionless, and
the full product is unit-free. Factors that are absent are left to C3.
"""

from __future__ import annotations

from trustlayer.checks.base import CheckInputs, CheckResult, result
from trustlayer.ledger.model import (
    BRANCHING_FRACTION,
    CROSS_SECTION,
    EFFICIENCY,
    GENERATOR_CROSS_SECTION,
    LUMINOSITY,
    Entry,
)
from trustlayer.ledger.units import UnitError, parse_unit

EXPECTED_AREA_POWER = {
    CROSS_SECTION: 1,
    GENERATOR_CROSS_SECTION: 1,
    LUMINOSITY: -1,
    BRANCHING_FRACTION: 0,
    EFFICIENCY: 0,
}
_KIND = {
    1: "a cross section (fb or pb)",
    -1: "an inverse cross section (fb^-1 or pb^-1)",
    0: "dimensionless",
}


def _unit_problem(entry: Entry, expected: int, label: str) -> str | None:
    if entry.unit is None:
        return f"{label} has no unit; it must be {_KIND[expected]}"
    try:
        unit = parse_unit(entry.unit)
    except UnitError as exc:
        return f"{label}: {exc}"
    if unit.area_power != expected:
        return f"{label} is in {entry.unit!r}, but it must be {_KIND[expected]}"
    return None


def check_units(inputs: CheckInputs) -> CheckResult:
    """C1: every recorded unit is known and of the right kind; sigma*L*BR*eps is unit-free."""
    ledger = inputs.ledger
    problems: list[str] = []
    for name, expected in EXPECTED_AREA_POWER.items():
        entry = ledger.get(name)
        if entry is None or entry.value is None:
            continue
        if (problem := _unit_problem(entry, expected, name)) is not None:
            problems.append(problem)
    for corr in ledger.corrections:
        if (problem := _unit_problem(corr, 0, f"correction {corr.name!r}")) is not None:
            problems.append(problem)
    if not problems and not ledger.missing_factors():
        product = ledger.product()
        if not product.unit_free:
            problems.append(
                f"sigma*L*BR*eps does not come out unit-free (area power {product.area_power:+d})"
            )
    return result("C1", "1a", problems)
