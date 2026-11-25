"""Gate tests: a fake Collider-Bench run folder, hook JSON on stdin, exit codes and the log."""

from __future__ import annotations

import io
import json
import shutil
from pathlib import Path

import pytest

from trustlayer.gate import load_config, main, run
from trustlayer.gate.config import ConfigError
from trustlayer.gate.locate import LocateError, find_task_context

ROOT = Path(__file__).resolve().parents[2]
CONTEXTS = ROOT / "integration" / "task-context"
HAND_LEDGER = ROOT / "tasks" / "sus-16-034_sim-TChiWZ" / "ledger.yaml"

RESULTS = """\
instructions: "Fill the nulls"
target: "TChiWZ"
luminosity_fb: 35.9
---
dependent_variables:
- header: {{name: TChiWZ_550_200}}
  values:
  - {{value: {0}}}
  - {{value: {1}}}
  - {{value: {2}}}
  - {{value: {3}}}
independent_variables:
- header: {{name: MET, units: GEV}}
  values:
  - {{low: 100, high: 150}}
  - {{low: 150, high: 250}}
  - {{low: 250, high: 350}}
  - {{low: 350, high: 450}}
"""


@pytest.fixture
def setup(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    runtime = tmp_path / "runtime"
    shutil.copytree(CONTEXTS, runtime / "task-context")
    (runtime / "config.yaml").write_text("c5_tolerance: 0.05\nmax_bounces: 3\n", encoding="utf-8")
    ws = tmp_path / "runs" / "claude_sonnet-4-6" / "sus-16-034_sim-TChiWZ_GayDrell_1" / "workspace"
    (ws / "results").mkdir(parents=True)
    env = {
        "TRUSTLAYER_RUNTIME": str(runtime),
        "TRUSTLAYER_BOUNCE_LOG": str(tmp_path / "home" / ".trustlayer" / "bounces.jsonl"),
    }
    return ws, env


def write_results(ws: Path, *bins: object) -> None:
    (ws / "results" / "histogram.yaml").write_text(RESULTS.format(*bins), encoding="utf-8")


def hook(ws: Path, env: dict[str, str], session: str = "s1") -> tuple[int, str]:
    payload = json.dumps(
        {
            "session_id": session,
            "cwd": str(ws),
            "hook_event_name": "Stop",
            "stop_hook_active": False,
        }
    )
    outcome = run(payload, Path("/elsewhere"), env)
    return outcome.exit_code, outcome.stderr


def events(env: dict[str, str]) -> list[dict[str, object]]:
    lines = Path(env["TRUSTLAYER_BOUNCE_LOG"]).read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


def test_good_ledger_and_results_pass(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    shutil.copy(HAND_LEDGER, ws / "ledger.yaml")
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    assert hook(ws, env) == (0, "")
    (entry,) = events(env)
    assert entry["event"] == "pass" and entry["task"] == "sus-16-034_sim-TChiWZ"
    assert entry["config"] == {
        "c5_tolerance": 0.05,
        "max_bounces": 3,
        "source": str(Path(env["TRUSTLAYER_RUNTIME"]) / "config.yaml"),
    }


def test_no_ledger_bounces_three_times_then_submits(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    codes = [hook(ws, env)[0] for _ in range(4)]
    assert codes == [2, 2, 2, 0]
    assert [e["event"] for e in events(env)] == ["bounce"] * 3 + ["submitted_with_warnings"]
    assert [e.get("bounce") for e in events(env)] == [1, 2, 3, 3]


def test_bounce_message_is_actionable_and_uses_absolute_paths(
    setup: tuple[Path, dict[str, str]],
) -> None:
    ws, env = setup
    write_results(ws, 45, 137, 165, 194)  # bins never rescaled (1e)
    shutil.copy(HAND_LEDGER, ws / "ledger.yaml")
    code, message = hook(ws, env)
    assert code == 2
    assert str((ws / "ledger.yaml").resolve()) in message
    assert str((ws / "results" / "histogram.yaml").resolve()) in message
    assert "- C5 (results match the ledger):" in message
    assert "larger than the ledger" in message
    text = message.replace(str(ws.resolve()), "<ws>").lower()  # the tmp path contains test names
    assert not any(word in text for word in ("bounce", "attempt", "times", "warning"))


def test_bounce_count_is_per_session(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    for _ in range(3):
        hook(ws, env, session="a")
    assert hook(ws, env, session="b")[0] == 2


def test_fix_after_bounce_then_pass(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    assert hook(ws, env)[0] == 2
    shutil.copy(HAND_LEDGER, ws / "ledger.yaml")
    assert hook(ws, env)[0] == 0
    assert [e["event"] for e in events(env)] == ["bounce", "pass"]


def test_unreadable_ledger_is_reported(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    (ws / "ledger.yaml").write_text("schema_version: 7\n", encoding="utf-8")
    code, message = hook(ws, env)
    assert code == 2 and "can't be read" in message


def test_missing_results_file(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    shutil.copy(HAND_LEDGER, ws / "ledger.yaml")
    code, message = hook(ws, env)
    assert code == 2 and "no results/*.yaml" in message


def test_setup_error_never_blocks_the_agent(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    broken = {**env, "TRUSTLAYER_RUNTIME": str(ws.parent / "nowhere")}
    code, message = hook(ws, broken)
    assert code == 0 and "setup error" in message
    assert events(env)[0]["event"] == "gate_error"


def test_bad_config_is_a_setup_error(setup: tuple[Path, dict[str, str]]) -> None:
    ws, env = setup
    (Path(env["TRUSTLAYER_RUNTIME"]) / "config.yaml").write_text("c5_tolerance: 5\n", "utf-8")
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    assert hook(ws, env)[0] == 0
    assert events(env)[0]["event"] == "gate_error"


def test_main_reads_stdin_and_prints_to_stderr(
    setup: tuple[Path, dict[str, str]], capsys: pytest.CaptureFixture[str]
) -> None:
    ws, env = setup
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    payload = io.StringIO(json.dumps({"session_id": "m", "cwd": str(ws)}))
    assert main(payload, env) == 2
    assert "[trust-layer checker]" in capsys.readouterr().err


def test_find_task_context_takes_longest_prefix(tmp_path: Path) -> None:
    for stem in ("sus-16-051_sim-T2tt_SRG", "sus-16-051_sim-T2tt_comp", "sus-16-046_sim-TChiWg"):
        (tmp_path / f"{stem}.yaml").write_text("x", encoding="utf-8")
    ws = tmp_path / "runs" / "r" / "sus-16-051_sim-T2tt_comp_Abc_1" / "workspace"
    assert find_task_context(ws, tmp_path).stem == "sus-16-051_sim-T2tt_comp"
    with pytest.raises(LocateError, match="no task context"):
        find_task_context(tmp_path / "runs" / "r" / "other_task_1" / "workspace", tmp_path)


def test_config_defaults_and_validation(tmp_path: Path) -> None:
    assert load_config(None).source == "defaults"
    assert load_config(tmp_path / "missing.yaml").max_bounces == 3
    bad = tmp_path / "c.yaml"
    bad.write_text("max_bounces: -1\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="max_bounces"):
        load_config(bad)


def _prospino_ledger(ws: Path) -> None:
    text = HAND_LEDGER.read_text(encoding="utf-8").replace(
        "source_type: xsec_wg", "source_type: prospino"
    )
    (ws / "ledger.yaml").write_text(text, encoding="utf-8")


def test_prospino_label_needs_prospino_output(setup: tuple[Path, dict[str, str]]) -> None:
    """Decision 0017, the R2 pattern: a sigma labelled prospino with no Prospino run."""
    ws, env = setup
    (ws / "prompt.txt").write_text("prompt", encoding="utf-8")
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    _prospino_ledger(ws)
    code, message = hook(ws, env)
    assert code == 2 and "- C2 (cross-section source):" in message
    assert "no finished Prospino result" in message


def test_prospino_label_matching_this_runs_output_passes(
    setup: tuple[Path, dict[str, str]],
) -> None:
    ws, env = setup
    (ws / "prompt.txt").write_text("prompt", encoding="utf-8")
    write_results(ws, 0.45, 1.37, 1.65, 1.94)
    _prospino_ledger(ws)
    scratch = ws / "prospino_scratch" / "nn-abc123"
    scratch.mkdir(parents=True)
    (scratch / "prospino.dat").write_text(
        "nn  5  2   0.0   0.0   1.0   550   550   0.000   "
        "0.0215   0.01   0.0301656   0.01   1.40   0.0215   0.0301656\n",
        encoding="utf-8",
    )
    assert hook(ws, env)[0] == 0
    (entry,) = events(env)
    assert entry["prospino_results"][0]["nlo_pb"] == 0.0301656
