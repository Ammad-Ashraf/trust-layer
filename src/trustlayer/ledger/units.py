"""Fixed unit table for the normalization formula (decision 0009: no `pint` in the container).

The formula sigma x L x BR x eps only needs cross-section units, their inverses (luminosity)
and dimensionless factors. Each unit is stored as a scale to a canonical unit plus an
"area power": fb is area^+1, fb^-1 is area^-1, a pure number is area^0. A product of
quantities is unit-free exactly when the area powers sum to zero.

Guards 1a (wrong units): unknown unit strings raise instead of being guessed.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass


class UnitError(ValueError):
    """Raised for a unit string that is not in the table."""


@dataclass(frozen=True)
class Unit:
    """One unit: its canonical name, the factor to fb^area_power, and its area power."""

    name: str
    scale: float
    area_power: int


DIMENSIONLESS = Unit("dimensionless", 1.0, 0)

UNITS: dict[str, Unit] = {
    "fb": Unit("fb", 1.0, 1),
    "pb": Unit("pb", 1.0e3, 1),
    "fb^-1": Unit("fb^-1", 1.0, -1),
    "pb^-1": Unit("pb^-1", 1.0e-3, -1),
    "dimensionless": DIMENSIONLESS,
}

_ALIASES: dict[str, str] = {
    "fb-1": "fb^-1",
    "/fb": "fb^-1",
    "1/fb": "fb^-1",
    "fb⁻¹": "fb^-1",
    "pb-1": "pb^-1",
    "/pb": "pb^-1",
    "1/pb": "pb^-1",
    "pb⁻¹": "pb^-1",
    "1": "dimensionless",
    "unitless": "dimensionless",
    "events": "dimensionless",
}


def parse_unit(text: str) -> Unit:
    """Return the Unit for `text` (case-insensitive, spaces ignored).

    Raises UnitError for anything not in the table, e.g. "nb" or "fb^-2".
    """
    key = text.strip().replace(" ", "")
    lowered = key.lower()
    canonical = _ALIASES.get(key, _ALIASES.get(lowered, lowered))
    unit = UNITS.get(canonical)
    if unit is None:
        known = ", ".join(sorted(UNITS))
        raise UnitError(f"unknown unit {text!r}; use one of: {known}")
    return unit


@dataclass(frozen=True)
class Quantity:
    """A value with its unit. Never pass physics numbers around as bare floats."""

    value: float
    unit: Unit

    def canonical(self) -> float:
        """The value expressed in fb^area_power (fb, fb^-1 or a pure number)."""
        return self.value * self.unit.scale


@dataclass(frozen=True)
class Product:
    """Result of multiplying quantities: canonical value and total area power."""

    value: float
    area_power: int

    @property
    def unit_free(self) -> bool:
        """True when the area units cancel, as sigma (fb) x L (fb^-1) must."""
        return self.area_power == 0


def multiply(quantities: Iterable[Quantity]) -> Product:
    """Multiply quantities, converting each to its canonical unit first.

    Example: 0.03 pb x 35.9 fb^-1 = 30 fb x 35.9 fb^-1 = 1077 (unit-free).
    """
    value = 1.0
    power = 0
    for q in quantities:
        if not math.isfinite(q.value):
            raise ValueError(f"non-finite value {q.value!r} in {q.unit.name}")
        value *= q.canonical()
        power += q.unit.area_power
    return Product(value, power)
