"""Tests for reading Prospino output and for C2's Prospino verification (decision 0017)."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

import pytest

from tests.checks.helpers import ROOT, clean_ledger, inputs, with_entry
from trustlayer.checks import check_source
from trustlayer.checks.prospino import ProspinoResult, collect, parse_dat
from trustlayer.ledger import Ledger, load_ledger

# Row layout as in Collider-Bench's own tests (tests/test_prospino.py), header after the data.
ROW = (
    "nn  5  2   0.0   0.0   1.0   550   550   0.000   "
    "{lo}   0.01   {nlo}   0.01   2.0   {lo_ms}   {nlo_ms}\n"
)
HEADER = (
    "    i1 i2  dummy0 dummy1 scafac  m1  m2  angle  LO[pb]  rel_error  NLO[pb]  rel_error  K\n"
)
R2_LEDGER = (
    ROOT
    / "experiments"
    / "04-gate-test"
    / "runs"
    / "20261126-0125_sus-16-034_checker_1"
    / "ledger.yaml"
)


def write_dat(folder: Path, nlo_pb: float, lo_pb: float = 0.01, ms: bool = True) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    row = ROW.format(
        lo=lo_pb if not ms else 1e-9,
        nlo=nlo_pb if not ms else 1e-9,
        lo_ms=lo_pb if ms else 0.0,
        nlo_ms=nlo_pb if ms else 0.0,
    )
    dat = folder / "prospino.dat"
    dat.write_text(row + HEADER, encoding="utf-8")
    return dat


def test_parse_dat_prefers_free_squark_mass_columns(tmp_path: Path) -> None:
    result = parse_dat(write_dat(tmp_path, nlo_pb=0.0301656, lo_pb=0.0215))
    assert result is not None
    assert (result.process, result.nlo_pb, result.lo_pb) == ("nn", 0.0301656, 0.0215)


def test_parse_dat_falls_back_to_degenerate_columns(tmp_path: Path) -> None:
    result = parse_dat(write_dat(tmp_path, nlo_pb=0.00396, lo_pb=0.00164, ms=False))
    assert result is not None and result.nlo_pb == 0.00396


@pytest.mark.parametrize("text", ["", "# comments only\n", HEADER, "nn 5 2 broken\n"])
def test_parse_dat_without_a_data_row(tmp_path: Path, text: str) -> None:
    dat = tmp_path / "prospino.dat"
    dat.write_text(text, encoding="utf-8")
    assert parse_dat(dat) is None
    assert parse_dat(tmp_path / "missing.dat") is None


def test_collect_skips_older_runs_and_duplicates(tmp_path: Path) -> None:
    old = write_dat(tmp_path / "cb" / "prospino_scratch" / "nn-old", nlo_pb=0.5)
    os.utime(old, (1_000, 1_000))
    write_dat(tmp_path / "cb" / "prospino_scratch" / "nn-new", nlo_pb=0.0301656)
    (tmp_path / "ws").mkdir()
    found = collect([tmp_path / "ws", tmp_path / "cb", tmp_path / "cb"], since=2_000)
    assert [r.nlo_pb for r in found] == [0.0301656]
    assert len(collect([tmp_path / "cb"], since=None)) == 2


# --- C2 with Prospino verification ----------------------------------------------------------


def prospino_labelled(value_fb: float = 30.1656) -> Ledger:
    return with_entry(
        clean_ledger(),
        "cross_section",
        value=value_fb,
        source_type="prospino",
        source="bin/prospino nn NLO",
    )


def run_result(nlo_pb: float, lo_pb: float = 0.0215) -> ProspinoResult:
    return ProspinoResult(
        path=Path("/cb/prospino_scratch/nn-abc/prospino.dat"),
        process="nn",
        lo_pb=lo_pb,
        nlo_pb=nlo_pb,
    )


def test_c2_passes_when_sigma_matches_a_prospino_nlo_result() -> None:
    r = check_source(inputs(prospino_labelled(), prospino_results=(run_result(0.0301656),)))
    assert r.passed and "matches a Prospino NLO result" in r.messages[0]


def test_c2_fails_when_no_prospino_result_exists() -> None:
    r = check_source(inputs(prospino_labelled(), prospino_results=()))
    assert not r.passed and "no finished Prospino result" in r.messages[0]


def test_c2_fails_when_sigma_matches_no_result() -> None:
    r = check_source(inputs(prospino_labelled(0.15), prospino_results=(run_result(0.0301656),)))
    assert not r.passed
    assert "matches none of this run's Prospino NLO results: 30.17 fb (nn, nn-abc)" in r.messages[0]


def test_c2_flags_the_prospino_lo_value() -> None:
    r = check_source(inputs(prospino_labelled(21.5), prospino_results=(run_result(0.0301656),)))
    assert not r.passed and "Prospino LO value" in r.messages[0]


def test_c2_without_collected_results_only_notes() -> None:
    r = check_source(inputs(prospino_labelled(0.15)))
    assert r.passed and "not verified" in r.messages[0]


def test_c2_leaves_other_sources_alone() -> None:
    assert check_source(inputs(clean_ledger(), prospino_results=())).passed


def test_r2_fabricated_ledger_is_now_caught() -> None:
    """R2 (04-gate-test, Haiku): sigma = 0.15 fb labelled Prospino, but Prospino never
    returned a value. With 0017, C2 must reject it (it passed all five checks before)."""
    ledger = load_ledger(R2_LEDGER)
    r = check_source(replace(inputs(ledger), prospino_results=()))
    assert not r.passed and "no finished Prospino result" in r.messages[0]
