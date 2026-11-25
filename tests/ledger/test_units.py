"""Tests for the fixed unit table (guards 1a: pb <-> fb, inverse units, unknown units)."""

import math

import pytest

from trustlayer.ledger.units import (
    DIMENSIONLESS,
    UNITS,
    Quantity,
    UnitError,
    multiply,
    parse_unit,
)


@pytest.mark.parametrize(
    ("text", "name"),
    [
        ("fb", "fb"),
        ("PB", "pb"),
        ("fb^-1", "fb^-1"),
        ("fb-1", "fb^-1"),
        ("/fb", "fb^-1"),
        ("fb⁻¹", "fb^-1"),
        (" pb ^-1 ", "pb^-1"),
        ("1/pb", "pb^-1"),
        ("dimensionless", "dimensionless"),
        ("1", "dimensionless"),
        ("events", "dimensionless"),
    ],
)
def test_parse_unit_accepts_spellings(text: str, name: str) -> None:
    assert parse_unit(text).name == name


@pytest.mark.parametrize("text", ["nb", "fb^-2", "GeV", "", "barn"])
def test_parse_unit_rejects_unknown(text: str) -> None:
    with pytest.raises(UnitError, match="unknown unit"):
        parse_unit(text)


def test_pb_converts_to_1000_fb() -> None:
    assert Quantity(0.03, parse_unit("pb")).canonical() == pytest.approx(30.0)
    assert Quantity(1.0, parse_unit("pb^-1")).canonical() == pytest.approx(1.0e-3)


def test_sigma_times_lumi_is_unit_free_across_mixed_units() -> None:
    product = multiply([Quantity(0.03, parse_unit("pb")), Quantity(35.9, parse_unit("fb^-1"))])
    assert product.unit_free
    assert product.value == pytest.approx(30.0 * 35.9)


def test_sigma_alone_is_not_unit_free() -> None:
    product = multiply([Quantity(3.96, parse_unit("fb")), Quantity(0.5, DIMENSIONLESS)])
    assert product.area_power == 1
    assert not product.unit_free


def test_multiply_rejects_non_finite() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        multiply([Quantity(math.inf, parse_unit("fb"))])


def test_table_matches_pint() -> None:
    pint = pytest.importorskip("pint")
    ureg = pint.UnitRegistry()
    pint_name = {"fb": "fb", "pb": "pb", "fb^-1": "1/fb", "pb^-1": "1/pb"}
    for name, unit in UNITS.items():
        if unit.area_power == 0:
            continue
        canonical = "femtobarn" if unit.area_power == 1 else "1/femtobarn"
        magnitude = ureg.Quantity(1, pint_name[name]).to(canonical).magnitude
        assert magnitude == pytest.approx(unit.scale), name
