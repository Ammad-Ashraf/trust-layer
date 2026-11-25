"""Study A's fixed injection list (decision 0016, docs/design/checker-v0.md section 7) as
regression tests on the sus-16-034 ledger. Each case names the checks that must fail.

The submission stays the clean one (as if the agent's bins were right and only the ledger
changed), except for the 1e cases, where only the bins change.
"""

from __future__ import annotations

import pytest

from tests.checks.helpers import (
    TCHIWZ_BINS,
    clean_ledger,
    failing,
    inputs,
    with_entry,
    with_quantity,
    without,
)
from trustlayer.checks import CheckInputs
from trustlayer.ledger import Entry


def _cases() -> list[tuple[str, CheckInputs, set[str]]]:
    clean = clean_ledger()
    lo = Entry(
        name="generator_cross_section",
        value=12.0,
        unit="fb",
        source_type="generator",
        source="MadGraph LO",
    )
    return [
        # 1a: sigma in pb written as fb (x1000 small); L in pb^-1 left unconverted.
        ("1a-sigma-pb-as-fb", inputs(with_entry(clean, "cross_section", value=0.0301656)), {"C5"}),
        ("1a-lumi-pb-inverse", inputs(with_entry(clean, "luminosity", unit="pb^-1")), {"C4", "C5"}),
        # 1b: LO sigma labelled as generator; the same LO value under a false prospino label.
        (
            "1b-lo-generator",
            inputs(
                with_quantity(
                    with_entry(clean, "cross_section", value=12.0, source_type="generator"), lo
                )
            ),
            {"C2", "C5"},
        ),
        (
            "1b-lo-false-label",
            inputs(
                with_quantity(
                    with_entry(clean, "cross_section", value=12.0, source_type="prospino"), lo
                )
            ),
            {"C2", "C5"},
        ),
        # 1c: BR removed; BR = 1 with no reason.
        ("1c-br-removed", inputs(without(clean, "branching_fraction")), {"C3", "C5"}),
        (
            "1c-br-one-no-reason",
            inputs(with_entry(clean, "branching_fraction", value=1.0)),
            {"C3", "C5"},
        ),
        # 1d: sigma at the neighbouring mass point (550 -> 500 GeV; sigma grows ~1.6x); L = 36.1.
        (
            "1d-mass-500",
            inputs(
                with_entry(
                    clean,
                    "cross_section",
                    value=46.3533,  # SUSY xsec WG NLO-NLL, 500 GeV
                    masses_gev={"chargino_1": 500.0, "neutralino_2": 500.0},
                )
            ),
            {"C4", "C5"},
        ),
        ("1d-lumi-36.1", inputs(with_entry(clean, "luminosity", value=36.1)), {"C4"}),
        # 1e: bins left at an earlier, unscaled value; one bin left null.
        ("1e-bins-unscaled", inputs(bins=tuple(b / 0.101 for b in TCHIWZ_BINS)), {"C5"}),
        ("1e-null-bin", inputs(bins=(0.45, 1.37, None, 1.94)), {"C5"}),
    ]


def _near_misses() -> list[tuple[str, CheckInputs]]:
    clean = clean_ledger()
    return [
        ("clean", inputs()),
        (
            "sigma-in-pb-converted",
            inputs(with_entry(clean, "cross_section", value=0.0301656, unit="pb")),
        ),
        (
            "br-one-with-reason",
            inputs(
                with_entry(
                    with_entry(
                        clean,
                        "branching_fraction",
                        value=1.0,
                        reason="Z -> ll is folded into the efficiency",
                    ),
                    "efficiency",
                    value=0.0495 * 0.101,
                )
            ),
        ),
        ("br-0.10-vs-0.101", inputs(with_entry(clean, "branching_fraction", value=0.10))),
    ]


@pytest.mark.parametrize(
    ("case", "check_inputs", "expected"), _cases(), ids=lambda x: x if isinstance(x, str) else ""
)
def test_injection_is_caught_by_the_expected_checks(
    case: str, check_inputs: CheckInputs, expected: set[str]
) -> None:
    assert failing(check_inputs) == expected, case


@pytest.mark.parametrize(
    ("case", "check_inputs"), _near_misses(), ids=lambda x: x if isinstance(x, str) else ""
)
def test_near_miss_raises_no_false_alarm(case: str, check_inputs: CheckInputs) -> None:
    assert failing(check_inputs) == set(), case
