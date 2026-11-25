"""Tests for scripts/postrun_check.py: tamper detection and bounce-log summary."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "postrun_check", ROOT / "scripts" / "postrun_check.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _setup(tmp_path: Path, events: list[str]) -> tuple[Path, Path]:
    agent = tmp_path / "agent"
    (agent / "runtime" / "hooks").mkdir(parents=True)
    shutil.copy(ROOT / "integration" / "agent" / "trustlayer-gate", agent / "runtime" / "hooks")
    run = tmp_path / "run"
    (run / "workspace" / ".claude").mkdir(parents=True)
    hook = {"type": "command", "command": str(agent / "runtime" / "hooks" / "trustlayer-gate")}
    settings = {"hooks": {"Stop": [{"hooks": [hook]}]}}
    (run / "workspace" / ".claude" / "settings.json").write_text(json.dumps(settings), "utf-8")
    log = run / ".claude_home" / ".trustlayer" / "bounces.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text("".join(json.dumps({"event": e}) + "\n" for e in events), "utf-8")
    return run, agent


def test_clean_run(tmp_path: Path) -> None:
    run, agent = _setup(tmp_path, ["bounce", "bounce", "pass"])
    fields = _module().check(run, agent)
    assert fields["bounces"] == 2 and fields["gate_final_event"] == "pass"
    assert not fields["tampered"] and not fields["gate_error"]


def test_edited_settings_are_tampering(tmp_path: Path) -> None:
    run, agent = _setup(tmp_path, ["pass"])
    (run / "workspace" / ".claude" / "settings.json").write_text('{"hooks": {}}', "utf-8")
    assert _module().check(run, agent)["tampered"]


def test_edited_hook_script_is_tampering(tmp_path: Path) -> None:
    run, agent = _setup(tmp_path, ["pass"])
    built = tmp_path / "built"
    (built / "runtime" / "hooks").mkdir(parents=True)
    (built / "runtime" / "hooks" / "trustlayer-gate").write_text("#!/bin/sh\nexit 0\n", "utf-8")
    assert _module().check(run, built)["tampered"]


def test_gate_error_and_cli(tmp_path: Path) -> None:
    run, agent = _setup(tmp_path, ["gate_error"])
    dest = tmp_path / "dest"
    module = _module()
    assert module.check(run, agent)["gate_error"]
    assert module.main([str(run), str(dest), "--agent-folder", str(agent)]) == 1
    assert (dest / "gate-bounces.jsonl").is_file()
