"""Ledger data model: one schema for the agent's ledger and the hand-filled ledgers in `tasks/`.

A ledger records each factor of expected events = sigma x L x BR x eps (x corrections), each
with a unit and a source. Schema version 2 adds `source_type`, `process`, `masses_gev`,
`reason`, `n_pass`/`n_gen` and `corrections`; version 1 files (the M2 hand ledgers) still load.
Design: docs/design/checker-v0.md section 3.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from trustlayer.ledger.units import Product, Quantity, multiply, parse_unit

SCHEMA_VERSION = 2
SUPPORTED_VERSIONS = (1, 2)

CROSS_SECTION = "cross_section"
LUMINOSITY = "luminosity"
BRANCHING_FRACTION = "branching_fraction"
EFFICIENCY = "efficiency"
GENERATOR_CROSS_SECTION = "generator_cross_section"

FACTORS = (CROSS_SECTION, LUMINOSITY, BRANCHING_FRACTION, EFFICIENCY)
"""The four factors of the normalization formula, in order."""

QUANTITY_NAMES = (*FACTORS, GENERATOR_CROSS_SECTION)
"""Names allowed under `quantities`. The generator's LO sigma is evidence for C2, not a factor."""

SOURCE_TYPES = frozenset({"prospino", "xsec_wg", "paper", "hepdata", "generator", "other"})


class LedgerError(ValueError):
    """Raised when a ledger file is structurally broken (not when a value is merely missing)."""


@dataclass(frozen=True)
class Entry:
    """One recorded number: a formula factor, the generator sigma, or a correction.

    `value` and `unit` may be None in a half-filled ledger; the checks report that.
    `extra` keeps fields this code doesn't interpret (e.g. `in_plain_words`) for round trips.
    """

    name: str
    value: float | None
    unit: str | None
    source: str | None = None
    source_type: str | None = None
    process: str | None = None
    masses_gev: Mapping[str, float] = field(default_factory=dict)
    reason: str | None = None
    n_pass: float | None = None
    n_gen: float | None = None
    uncertainty: float | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def quantity(self) -> Quantity:
        """The entry as a Quantity. Raises ValueError if the value or unit is missing or unknown."""
        if self.value is None:
            raise ValueError(f"{self.name}: no value recorded")
        if self.unit is None:
            raise ValueError(f"{self.name}: no unit recorded")
        return Quantity(self.value, parse_unit(self.unit))


@dataclass(frozen=True)
class Ledger:
    """A whole ledger: task id, the named quantities and any extra correction factors."""

    schema_version: int
    task: str | None
    quantities: Mapping[str, Entry]
    corrections: tuple[Entry, ...] = ()
    extra: Mapping[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> Entry | None:
        """The entry called `name`, or None if it was never recorded."""
        return self.quantities.get(name)

    def missing_factors(self) -> list[str]:
        """Formula factors that are absent or have no value."""
        return [n for n in FACTORS if (e := self.get(n)) is None or e.value is None]

    def product(self) -> Product:
        """sigma x L x BR x eps x corrections in canonical units.

        Raises ValueError naming the first factor that is missing or has an unknown unit.
        """
        missing = self.missing_factors()
        if missing:
            raise ValueError(f"cannot compute the formula, missing: {', '.join(missing)}")
        entries = [self.quantities[n] for n in FACTORS] + list(self.corrections)
        return multiply(e.quantity() for e in entries)


def empty_ledger(task: str | None = None) -> Ledger:
    """A new, empty ledger at the current schema version."""
    return Ledger(schema_version=SCHEMA_VERSION, task=task, quantities={})
