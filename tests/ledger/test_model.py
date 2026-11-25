"""Tests for the ledger model: the formula product and missing factors."""

from pathlib import Path

import pytest

from trustlayer.ledger import Entry, Ledger, ledger_from_dict, load_ledger

TASKS = Path(__file__).resolve().parents[2] / "tasks"


def _ledger(
    sigma_unit: str = "fb",
    sigma: float = 30.1656,
    corrections: list[dict[str, object]] | None = None,
) -> Ledger:
    return ledger_from_dict(
        {
            "schema_version": 2,
            "task": "sus-16-034_sim-TChiWZ",
            "quantities": {
                "cross_section": {"value": sigma, "unit": sigma_unit},
                "luminosity": {"value": 35.9, "unit": "fb^-1"},
                "branching_fraction": {"value": 0.101, "unit": "dimensionless"},
                "efficiency": {"value": 0.0495, "unit": "dimensionless"},
            },
            "corrections": corrections or [],
        }
    )


def test_tchiwz_hand_ledger_gives_5_41_events() -> None:
    product = load_ledger(TASKS / "sus-16-034_sim-TChiWZ" / "ledger.yaml").product()
    assert product.unit_free
    assert product.value == pytest.approx(5.41, rel=1e-3)


def test_sigma_in_pb_gives_the_same_product() -> None:
    assert _ledger("pb", 0.0301656).product().value == pytest.approx(_ledger().product().value)


def test_corrections_multiply_in() -> None:
    trigger = [{"name": "trigger", "value": 0.943, "unit": "dimensionless"}]
    expected = _ledger().product().value * 0.943
    assert _ledger(corrections=trigger).product().value == pytest.approx(expected)


def test_missing_factors_on_half_filled_template() -> None:
    ledger = load_ledger(TASKS / "sus-16-046_sim-T5Wg" / "ledger.yaml")
    assert ledger.missing_factors() == ["cross_section", "branching_fraction", "efficiency"]
    with pytest.raises(ValueError, match="missing: cross_section"):
        ledger.product()


def test_entry_quantity_needs_value_and_unit() -> None:
    with pytest.raises(ValueError, match="no unit"):
        Entry(name="cross_section", value=1.0, unit=None).quantity()
    with pytest.raises(ValueError, match="no value"):
        Entry(name="cross_section", value=None, unit="fb").quantity()
