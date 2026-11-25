"""Tests for loading and saving ledgers (schema v1 hand ledgers and v2)."""

from pathlib import Path

import pytest
import yaml

from trustlayer.ledger import (
    LedgerError,
    ledger_from_dict,
    ledger_to_dict,
    load_ledger,
    save_ledger,
)

TASKS = Path(__file__).resolve().parents[2] / "tasks"
TCHIWZ = TASKS / "sus-16-034_sim-TChiWZ" / "ledger.yaml"
T5WG_TEMPLATE = TASKS / "sus-16-046_sim-T5Wg" / "ledger.yaml"


def _minimal(**quantities: object) -> dict[str, object]:
    return {"schema_version": 2, "task": "t", "quantities": quantities}


def test_loads_filled_hand_ledger() -> None:
    ledger = load_ledger(TCHIWZ)
    assert ledger.schema_version == 2
    sigma = ledger.get("cross_section")
    assert sigma is not None
    assert (sigma.value, sigma.unit, sigma.uncertainty) == (30.1656, "fb", 2.88065)
    assert "in_plain_words" in sigma.extra
    assert "signal_model" in ledger.extra


def test_loads_half_filled_template_with_nulls() -> None:
    ledger = load_ledger(T5WG_TEMPLATE)
    sigma = ledger.get("cross_section")
    assert ledger.schema_version == 1
    assert sigma is not None and sigma.value is None and sigma.unit is None


def test_round_trip_keeps_everything(tmp_path: Path) -> None:
    original = load_ledger(TCHIWZ)
    out = tmp_path / "ledger.yaml"
    save_ledger(original, out)
    assert load_ledger(out) == original
    assert ledger_to_dict(load_ledger(out)) == ledger_to_dict(original)


def test_round_trip_v2_fields(tmp_path: Path) -> None:
    data = {
        "schema_version": 2,
        "task": "sus-16-046_sim-T5Wg",
        "quantities": {
            "cross_section": {
                "value": 3.96,
                "unit": "fb",
                "source": "prospino",
                "source_type": "prospino",
                "process": "gluino_pair",
                "masses_gev": {"gluino": 1750},
            },
            "efficiency": {"value": 0.0093, "unit": "dimensionless", "n_pass": 93, "n_gen": 10000},
        },
        "corrections": [{"name": "trigger", "value": 0.943, "unit": "dimensionless"}],
    }
    ledger = ledger_from_dict(data)
    out = tmp_path / "l.yaml"
    save_ledger(ledger, out)
    again = load_ledger(out)
    assert again == ledger
    assert again.corrections[0].name == "trigger"
    sigma = again.get("cross_section")
    assert sigma is not None and sigma.masses_gev == {"gluino": 1750.0}


def test_save_leaves_no_temp_files(tmp_path: Path) -> None:
    save_ledger(ledger_from_dict(_minimal()), tmp_path / "ledger.yaml")
    assert [p.name for p in tmp_path.iterdir()] == ["ledger.yaml"]


@pytest.mark.parametrize(
    ("data", "match"),
    [
        ([], "top level"),
        ({"schema_version": 3}, "schema_version"),
        ({"schema_version": True}, "schema_version"),
        ({"schema_version": 2, "quantities": []}, "quantities: must be a mapping"),
        (_minimal(sigma={"value": 1}), "unknown"),
        (_minimal(cross_section={"value": "3.96"}), "must be a number"),
        (_minimal(cross_section={"value": True}), "must be a number"),
        (_minimal(cross_section={"value": float("nan")}), "finite"),
        (_minimal(cross_section={"value": 1, "unit": 5}), "must be text"),
        (_minimal(cross_section={"value": 1, "masses_gev": [1750]}), "mapping of particle"),
        (_minimal(cross_section={"value": 1, "masses_gev": {"gluino": None}}), "mass is missing"),
        (_minimal(cross_section=3.96), "must be a mapping with value"),
        ({"schema_version": 2, "corrections": [{"value": 0.9}]}, "needs a name"),
        ({"schema_version": 2, "corrections": {"trigger": 0.9}}, "must be a list"),
    ],
)
def test_structural_errors_name_the_field(data: object, match: str) -> None:
    with pytest.raises(LedgerError, match=match):
        ledger_from_dict(data)


def test_invalid_yaml_is_a_ledger_error(tmp_path: Path) -> None:
    bad = tmp_path / "ledger.yaml"
    bad.write_text("quantities: [unclosed", encoding="utf-8")
    with pytest.raises(LedgerError, match="not valid YAML"):
        load_ledger(bad)


def test_saved_file_is_plain_yaml(tmp_path: Path) -> None:
    out = tmp_path / "ledger.yaml"
    save_ledger(ledger_from_dict(_minimal(luminosity={"value": 35.9, "unit": "fb^-1"})), out)
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["quantities"]["luminosity"] == {"value": 35.9, "unit": "fb^-1"}
