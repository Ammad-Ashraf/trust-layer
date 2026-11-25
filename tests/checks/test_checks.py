"""Unit tests for C1-C5: a correct case, each failure each check guards, and edge cases."""

from __future__ import annotations

from dataclasses import replace

import pytest

from tests.checks.helpers import (
    clean_ledger,
    failing,
    inputs,
    with_entry,
    with_quantity,
    without,
)
from trustlayer.checks import (
    CHECKS,
    check_carried,
    check_complete,
    check_match,
    check_source,
    check_units,
    run_checks,
)
from trustlayer.ledger import Entry, empty_ledger


def test_clean_hand_ledger_passes_all_five() -> None:
    results = run_checks(inputs())
    assert [r.check_id for r in results] == ["C1", "C2", "C3", "C4", "C5"]
    assert [r.subgap for r in results] == ["1a", "1b", "1c", "1d", "1e"]
    assert all(r.passed for r in results), [r.messages for r in results if not r.passed]


def test_registry_order() -> None:
    assert (check_units, check_source, check_complete, check_match, check_carried) == CHECKS


# --- C1 Units -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "unit", "message"),
    [
        ("cross_section", None, "has no unit"),
        ("cross_section", "fb^-1", "must be a cross section"),
        ("cross_section", "nb", "unknown unit"),
        ("luminosity", "fb", "must be an inverse cross section"),
        ("efficiency", "pb", "must be dimensionless"),
    ],
)
def test_c1_flags_wrong_units(name: str, unit: str | None, message: str) -> None:
    r = check_units(inputs(with_entry(clean_ledger(), name, unit=unit)))
    assert not r.passed
    assert any(message in m for m in r.messages)


def test_c1_accepts_pb_and_pb_inverse() -> None:
    ledger = with_entry(clean_ledger(), "cross_section", value=0.0301656, unit="pb")
    assert check_units(inputs(ledger)).passed


def test_c1_flags_correction_with_units() -> None:
    corr = Entry(name="trigger", value=0.94, unit="fb")
    r = check_units(inputs(replace(clean_ledger(), corrections=(corr,))))
    assert not r.passed and "correction 'trigger'" in r.messages[0]


def test_c1_ignores_missing_factors() -> None:
    assert check_units(inputs(empty_ledger())).passed


# --- C2 Source ----------------------------------------------------------------------------


@pytest.mark.parametrize("source_type", ["generator", "other", None, "hepdata"])
def test_c2_rejects_non_nlo_sources(source_type: str | None) -> None:
    r = check_source(inputs(with_entry(clean_ledger(), "cross_section", source_type=source_type)))
    assert not r.passed and "source_type" in r.messages[0]


@pytest.mark.parametrize("source_type", ["prospino", "xsec_wg", "paper"])
def test_c2_accepts_nlo_sources(source_type: str) -> None:
    assert check_source(
        inputs(with_entry(clean_ledger(), "cross_section", source_type=source_type))
    ).passed


def test_c2_needs_source_text() -> None:
    r = check_source(inputs(with_entry(clean_ledger(), "cross_section", source="  ")))
    assert not r.passed and "no source text" in r.messages[0]


def test_c2_catches_lo_value_under_a_false_label() -> None:
    gen = Entry(name="generator_cross_section", value=0.0301656, unit="pb", source_type="generator")
    r = check_source(inputs(with_quantity(clean_ledger(), gen)))
    assert not r.passed and "equals the generator's own sigma" in r.messages[0]


def test_c2_passes_when_nlo_differs_from_generator() -> None:
    gen = Entry(name="generator_cross_section", value=12.5, unit="fb", source_type="generator")
    assert check_source(inputs(with_quantity(clean_ledger(), gen))).passed


def test_c2_skips_without_sigma() -> None:
    r = check_source(inputs(without(clean_ledger(), "cross_section")))
    assert r.passed and "skipped" in r.messages[0]


# --- C3 Complete --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name", ["cross_section", "luminosity", "branching_fraction", "efficiency"]
)
def test_c3_flags_each_missing_factor(name: str) -> None:
    r = check_complete(inputs(without(clean_ledger(), name)))
    assert not r.passed
    assert r.messages[0].startswith(f"{name} is missing. Record it: bin/record-quantity {name}")


def test_c3_flags_value_none() -> None:
    assert not check_complete(inputs(with_entry(clean_ledger(), "efficiency", value=None))).passed


@pytest.mark.parametrize(("name", "value"), [("branching_fraction", 1.2), ("efficiency", 0.0)])
def test_c3_flags_out_of_range_fractions(name: str, value: float) -> None:
    r = check_complete(inputs(with_entry(clean_ledger(), name, value=value)))
    assert not r.passed and "between 0 and 1" in r.messages[0]


def test_c3_value_one_needs_reason() -> None:
    no_reason = with_entry(clean_ledger(), "branching_fraction", value=1.0, reason=None)
    assert not check_complete(inputs(no_reason)).passed
    with_reason = with_entry(no_reason, "branching_fraction", reason="Z decays are in eps")
    assert check_complete(inputs(with_reason)).passed


def test_c3_flags_negative_sigma() -> None:
    r = check_complete(inputs(with_entry(clean_ledger(), "cross_section", value=-1.0)))
    assert not r.passed and "must be positive" in r.messages[0]


def test_c3_checks_counts_against_efficiency() -> None:
    good = with_entry(clean_ledger(), "efficiency", n_pass=495.0, n_gen=10000.0)
    assert check_complete(inputs(good)).passed
    bad = with_entry(clean_ledger(), "efficiency", n_pass=93.0, n_gen=10000.0)
    r = check_complete(inputs(bad))
    assert not r.passed and "does not match n_pass/n_gen" in r.messages[0]
    half = with_entry(clean_ledger(), "efficiency", n_pass=93.0, n_gen=None)
    assert not check_complete(inputs(half)).passed


def test_c3_flags_non_positive_correction() -> None:
    corr = Entry(name="trigger", value=0.0, unit="dimensionless")
    assert not check_complete(inputs(replace(clean_ledger(), corrections=(corr,)))).passed


# --- C4 Match -----------------------------------------------------------------------------


def test_c4_flags_wrong_process() -> None:
    r = check_match(inputs(with_entry(clean_ledger(), "cross_section", process="gluino_pair")))
    assert not r.passed and "this task is chargino_neutralino" in r.messages[0]


def test_c4_flags_missing_process_and_masses() -> None:
    r = check_match(
        inputs(with_entry(clean_ledger(), "cross_section", process=None, masses_gev={}))
    )
    assert not r.passed
    text = " ".join(r.messages)
    assert "no known --process" in text and "--mass chargino_1=<GeV>" in text


def test_c4_flags_wrong_mass_point() -> None:
    ledger = with_entry(
        clean_ledger(), "cross_section", masses_gev={"chargino_1": 500.0, "neutralino_2": 500.0}
    )
    r = check_match(inputs(ledger))
    assert not r.passed
    assert "chargino_1=500" in r.messages[0] and "chargino_1=550" in r.messages[0]


def test_c4_accepts_aliases_and_extra_masses() -> None:
    ledger = with_entry(
        clean_ledger(),
        "cross_section",
        masses_gev={"1000024": 550.0, "n2": 550.2, "chi10": 200.0},
    )
    assert check_match(inputs(ledger)).passed


def test_c4_flags_wrong_lsp_mass_when_recorded() -> None:
    ledger = with_entry(
        clean_ledger(),
        "cross_section",
        masses_gev={"chargino_1": 550.0, "neutralino_2": 550.0, "neutralino_1": 100.0},
    )
    assert not check_match(inputs(ledger)).passed


@pytest.mark.parametrize(
    ("value", "unit", "ok"),
    [
        (35.9, "fb^-1", True),
        (35900.0, "pb^-1", True),
        (36.1, "fb^-1", False),
        (35.9, "pb^-1", False),
    ],
)
def test_c4_luminosity(value: float, unit: str, ok: bool) -> None:
    ledger = with_entry(clean_ledger(), "luminosity", value=value, unit=unit)
    assert check_match(inputs(ledger)).passed is ok


def test_c4_flags_ledger_for_another_task() -> None:
    r = check_match(inputs(replace(clean_ledger(), task="sus-16-046_sim-T5Wg")))
    assert not r.passed and "ledger is for task" in r.messages[0]


# --- C5 Carried through -------------------------------------------------------------------


def test_c5_passes_within_tolerance_and_reports_numbers() -> None:
    r = check_carried(inputs())
    assert r.passed and "ledger gives 5.41" in r.messages[0]


def test_c5_flags_unscaled_bins() -> None:
    r = check_carried(inputs(bins=(45.0, 137.0, 165.0, 194.0)))
    assert not r.passed and "99.9x larger than the ledger" in r.messages[0]


def test_c5_flags_null_bin() -> None:
    r = check_carried(inputs(bins=(0.45, None, 1.65, 1.94)))
    assert not r.passed and "bin(s) 2 still null" in r.messages[0]


def test_c5_flags_missing_ledger() -> None:
    r = check_carried(inputs(empty_ledger()))
    assert not r.passed and "not recorded" in r.messages[0]


def test_c5_flags_missing_results() -> None:
    base = inputs()
    r = check_carried(replace(base, submission=None, submission_error="no results/*.yaml"))
    assert not r.passed and "no results/*.yaml" in r.messages[0]


def test_c5_tolerance_comes_from_inputs() -> None:
    bins = (0.45 * 1.08, 1.37 * 1.08, 1.65 * 1.08, 1.94 * 1.08)  # 8% high
    assert not check_carried(inputs(bins=bins)).passed
    assert check_carried(inputs(bins=bins, c5_tolerance=0.10)).passed


def test_c5_zero_bins() -> None:
    r = check_carried(inputs(bins=(0.0, 0.0, 0.0, 0.0)))
    assert not r.passed and "sum to zero" in r.messages[0]


def test_failing_helper_on_clean_case() -> None:
    assert failing(inputs()) == set()
