"""Tests for the `record-quantity` CLI: what it accepts, what it refuses, and `show`."""

from pathlib import Path

import pytest

from trustlayer.ledger import load_ledger
from trustlayer.ledger.cli import main

TASKS = Path(__file__).resolve().parents[2] / "tasks"


@pytest.fixture
def ledger_path(tmp_path: Path) -> Path:
    return tmp_path / "ledger.yaml"


def run(path: Path, *args: str) -> int:
    return main([*args, "--ledger", str(path)])


def record_full_tchiwz(path: Path) -> None:
    assert (
        run(
            path,
            "cross_section",
            "--value",
            "30.1656",
            "--unit",
            "fb",
            "--source",
            "xsec WG",
            "--source-type",
            "xsec_wg",
            "--process",
            "Chargino_Neutralino",
            "--mass",
            "chargino_1=550",
            "--mass",
            "neutralino_1=200",
        )
        == 0
    )
    assert run(path, "luminosity", "--value", "35.9", "--unit", "fb^-1", "--source", "paper") == 0
    assert run(path, "branching_fraction", "--value", "0.101", "--source", "PDG") == 0
    assert (
        run(
            path,
            "efficiency",
            "--value",
            "0.0495",
            "--n-pass",
            "495",
            "--n-gen",
            "10000",
            "--source",
            "cut flow",
        )
        == 0
    )


def test_records_all_factors_and_show_gives_product(
    ledger_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    record_full_tchiwz(ledger_path)
    ledger = load_ledger(ledger_path)
    assert ledger.schema_version == 2
    sigma = ledger.get("cross_section")
    assert sigma is not None
    assert sigma.process == "chargino_neutralino"
    assert sigma.masses_gev == {"chargino_1": 550.0, "neutralino_1": 200.0}
    capsys.readouterr()
    assert run(ledger_path, "show") == 0
    out = capsys.readouterr().out
    assert "sigma*L*BR*eps = 5.41" in out
    assert "expected events" in out


def test_show_on_empty_ledger_says_incomplete(
    ledger_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(ledger_path, "show") == 0
    assert "incomplete, missing cross_section, luminosity" in capsys.readouterr().out
    assert not ledger_path.exists()


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["luminosity", "--value", "35.9", "--unit", "fb", "--source", "p"], "use fb^-1 or pb^-1"),
        (
            [
                "cross_section",
                "--value",
                "3.96",
                "--unit",
                "fb^-1",
                "--source",
                "p",
                "--source-type",
                "prospino",
            ],
            "use fb or pb",
        ),
        (
            [
                "cross_section",
                "--value",
                "3.96",
                "--unit",
                "nb",
                "--source",
                "p",
                "--source-type",
                "prospino",
            ],
            "unknown unit",
        ),
        (
            ["cross_section", "--value", "3.96", "--source", "p", "--source-type", "prospino"],
            "--unit is required",
        ),
        (
            ["cross_section", "--value", "3.96", "--unit", "fb", "--source", "p"],
            "--source-type is required",
        ),
        (["luminosity", "--value", "35.9", "--unit", "fb^-1"], "--source is required"),
        (["luminosity", "--unit", "fb^-1", "--source", "p"], "--value is required"),
        (["branching_fraction", "--value", "1", "--source", "p"], "needs --reason"),
        (["branching_fraction", "--value", "1.2", "--source", "p"], "at most 1"),
        (["efficiency", "--value", "0", "--source", "p"], "positive"),
        (
            ["efficiency", "--value", "0.5", "--n-pass", "93", "--n-gen", "10000", "--source", "p"],
            "does not match n_pass/n_gen",
        ),
        (["efficiency", "--value", "0.5", "--n-pass", "5", "--source", "p"], "both --n-pass"),
        (
            ["luminosity", "--value", "35.9", "--unit", "fb^-1", "--source", "p", "--n-gen", "5"],
            "efficiency only",
        ),
        (
            [
                "cross_section",
                "--value",
                "3.96",
                "--unit",
                "fb",
                "--source",
                "p",
                "--source-type",
                "prospino",
                "--mass",
                "gluino",
            ],
            "PARTICLE=GEV",
        ),
        (["correction", "--value", "0.943", "--source", "p"], "--name is required"),
    ],
)
def test_refuses_bad_input_with_a_reason(
    ledger_path: Path, capsys: pytest.CaptureFixture[str], args: list[str], message: str
) -> None:
    assert run(ledger_path, *args) == 1
    assert message in capsys.readouterr().err
    assert not ledger_path.exists()


def test_value_of_one_is_fine_with_a_reason(ledger_path: Path) -> None:
    assert (
        run(
            ledger_path,
            "branching_fraction",
            "--value",
            "1",
            "--source",
            "SLHA",
            "--reason",
            "all decays are simulated",
        )
        == 0
    )
    entry = load_ledger(ledger_path).get("branching_fraction")
    assert entry is not None and entry.reason == "all decays are simulated"


def test_generator_sigma_defaults_to_generator_source_type(ledger_path: Path) -> None:
    assert (
        run(
            ledger_path,
            "generator_cross_section",
            "--value",
            "1.453",
            "--unit",
            "fb",
            "--source",
            "MadGraph LO banner",
        )
        == 0
    )
    entry = load_ledger(ledger_path).get("generator_cross_section")
    assert entry is not None and entry.source_type == "generator"


def test_last_value_wins_and_corrections_replace_by_name(ledger_path: Path) -> None:
    for value in ("36.1", "35.9"):
        assert (
            run(ledger_path, "luminosity", "--value", value, "--unit", "fb^-1", "--source", "paper")
            == 0
        )
    for value in ("0.9", "0.943"):
        assert (
            run(
                ledger_path,
                "correction",
                "--name",
                "trigger",
                "--value",
                value,
                "--source",
                "paper",
            )
            == 0
        )
    assert (
        run(
            ledger_path,
            "correction",
            "--name",
            "photon_sf",
            "--value",
            "1.05",
            "--source",
            "eff file",
        )
        == 0
    )
    ledger = load_ledger(ledger_path)
    lumi = ledger.get("luminosity")
    assert lumi is not None and lumi.value == 35.9
    assert [(c.name, c.value) for c in ledger.corrections] == [
        ("trigger", 0.943),
        ("photon_sf", 1.05),
    ]


def test_recording_onto_v1_ledger_upgrades_version(tmp_path: Path) -> None:
    path = tmp_path / "ledger.yaml"
    path.write_text((TASKS / "sus-16-051_sim-T2tt_SRG" / "ledger.yaml").read_text("utf-8"), "utf-8")
    assert run(path, "luminosity", "--value", "35.9", "--unit", "fb^-1", "--source", "paper") == 0
    ledger = load_ledger(path)
    assert ledger.schema_version == 2
    assert "signal_model" in ledger.extra


def test_broken_ledger_file_is_reported(
    ledger_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger_path.write_text("schema_version: 9\n", encoding="utf-8")
    assert run(ledger_path, "show") == 1
    assert "schema_version" in capsys.readouterr().err


def test_env_var_sets_ledger_path_and_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "agent" / "ledger.yaml"
    target.parent.mkdir()
    monkeypatch.setenv("TRUSTLAYER_LEDGER", str(target))
    monkeypatch.setenv("TRUSTLAYER_TASK", "sus-16-046_sim-T5Wg")
    assert main(["luminosity", "--value", "35.9", "--unit", "fb^-1", "--source", "paper"]) == 0
    assert load_ledger(target).task == "sus-16-046_sim-T5Wg"


def test_default_path_is_working_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRUSTLAYER_LEDGER", raising=False)
    monkeypatch.chdir(tmp_path)
    assert main(["luminosity", "--value", "35.9", "--unit", "fb^-1", "--source", "paper"]) == 0
    assert (tmp_path / "ledger.yaml").exists()


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--mass", "squarkino=500"], "unknown particle"),
        (["--process", "gluon_fusion"], "--process 'gluon_fusion': unknown"),
    ],
)
def test_refuses_unknown_names(
    ledger_path: Path, capsys: pytest.CaptureFixture[str], args: list[str], message: str
) -> None:
    base = [
        "cross_section",
        "--value",
        "3.96",
        "--unit",
        "fb",
        "--source",
        "p",
        "--source-type",
        "prospino",
    ]
    assert run(ledger_path, *base, *args) == 1
    assert message in capsys.readouterr().err


def test_particle_aliases_are_normalized(ledger_path: Path) -> None:
    assert (
        run(
            ledger_path,
            "cross_section",
            "--value",
            "3.96",
            "--unit",
            "fb",
            "--source",
            "p",
            "--source-type",
            "prospino",
            "--process",
            "Gluino Pair",
            "--mass",
            "~g=1750",
            "--mass",
            "1000022=1700",
        )
        == 0
    )
    sigma = load_ledger(ledger_path).get("cross_section")
    assert sigma is not None
    assert sigma.process == "gluino_pair"
    assert sigma.masses_gev == {"gluino": 1750.0, "neutralino_1": 1700.0}
