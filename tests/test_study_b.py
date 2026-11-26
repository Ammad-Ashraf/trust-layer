"""Tests for scripts/study_b.py: schedule, outcome rules, checker time, secret scan."""

from __future__ import annotations

import gzip
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("study_b", ROOT / "scripts" / "study_b.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["study_b"] = module
    spec.loader.exec_module(module)
    return module


sb = _module()
CFG = yaml.safe_load((ROOT / "experiments" / "03-study-b" / "config.yaml").read_text("utf-8"))


def test_schedule_has_36_balanced_slots_and_pilot_first() -> None:
    slots = sb.make_schedule(CFG, CFG["schedule_seed"])
    assert len(slots) == 36
    cells = Counter((s.model, s.task, s.arm) for s in slots)
    assert set(cells.values()) == {3}
    assert all(s.pilot for s in slots[:3])
    assert {(s.model, s.arm, s.rep) for s in slots[:3]} == {("claude-sonnet-4-6", "baseline", 1)}
    assert {s.task for s in slots[:3]} == set(CFG["tasks"])
    assert not any(s.pilot for s in slots[3:])
    reps = [s.rep for s in slots]
    assert reps == sorted(reps)


def test_schedule_is_deterministic_and_committed_file_matches() -> None:
    a = sb.make_schedule(CFG, CFG["schedule_seed"])
    assert a == sb.make_schedule(CFG, CFG["schedule_seed"])
    committed = yaml.safe_load((ROOT / "experiments" / "03-study-b" / "schedule.yaml").read_text())
    assert [sb.Slot(**s) for s in committed["slots"]] == a


def _init() -> dict[str, Any]:
    return {"type": "system", "subtype": "init", "model": "claude-haiku-4-5"}


def test_classify_scored_timeout_crash() -> None:
    ok = [_init(), {"type": "result", "is_error": False, "result": "done"}]
    assert sb.classify(ok, "", has_score=True) == "scored"
    assert sb.classify(ok, "", has_score=False) == "crash"
    log = "[runner] task walltime (36000 s) exceeded; killing"
    assert sb.classify(ok, log, has_score=True) == "timeout"


def test_classify_void_on_usage_limit_or_login_failure() -> None:
    rejected = {"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}}
    assert sb.classify([_init(), rejected], "", has_score=True) == "void"
    limit = {"type": "result", "is_error": True, "result": "Claude AI usage limit reached"}
    assert sb.classify([_init(), limit], "", has_score=True) == "void"
    assert sb.classify([], "Invalid API key · Please run /login", has_score=False) == "void"
    allowed = {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed"}}
    assert sb.classify([_init(), allowed], "", has_score=True) == "scored"


def test_a_physics_error_is_not_void() -> None:
    err = {"type": "result", "is_error": True, "result": "Delphes crashed"}
    assert sb.classify([_init(), err], "", has_score=False) == "crash"


def _tool(ts: str, tid: str, cmd: str) -> dict[str, Any]:
    content = [{"type": "tool_use", "id": tid, "input": {"command": cmd}}]
    return {"type": "assistant", "timestamp": ts, "message": {"content": content}}


def _result(ts: str, tid: str) -> dict[str, Any]:
    content = [{"type": "tool_result", "tool_use_id": tid}]
    return {"type": "user", "timestamp": ts, "message": {"content": content}}


def test_checker_time_sums_ledger_calls_and_work_after_first_bounce() -> None:
    events = [
        _tool("2026-12-16T10:00:00Z", "a", "bin/record-quantity cross_section --value 1"),
        _result("2026-12-16T10:00:04Z", "a"),
        _tool("2026-12-16T10:01:00Z", "b", "bin/simulate"),
        _result("2026-12-16T10:05:00Z", "b"),
        _tool("2026-12-16T10:10:00Z", "c", "bin/record-quantity show"),
        _result("2026-12-16T10:10:02Z", "c"),
        _result("2026-12-16T10:20:00Z", "zzz"),
    ]
    bounces = [{"event": "bounce", "time": "2026-12-16T10:15:00+00:00"}, {"event": "pass"}]
    t = sb.checker_time(events, bounces)
    assert t["record_quantity_calls"] == 2
    assert t["record_quantity_seconds"] == 6.0
    assert t["after_first_bounce_seconds"] == 300.0
    assert t["checker_seconds"] == 306.0
    assert sb.checker_time(events, [])["after_first_bounce_seconds"] == 0.0


def test_find_secrets_catches_the_token_even_inside_gzip(tmp_path: Path) -> None:
    (tmp_path / "manifest.yaml").write_text("outcome: scored\n")
    assert sb.find_secrets(tmp_path, "tok-123") == []
    with gzip.open(tmp_path / "session.jsonl.gz", "wt") as fh:
        fh.write(json.dumps({"x": "leaked tok-123"}))
    (tmp_path / "launch.log").write_text("Authorization: Bearer abc\n")
    assert sb.find_secrets(tmp_path, "tok-123") == ["launch.log", "session.jsonl.gz"]


def test_harness_config_only_baseline_names_an_agent() -> None:
    base = sb.Slot("S01", "claude-sonnet-4-6", CFG["tasks"][0], "baseline", 1, True)
    check = sb.Slot("S04", "claude-sonnet-4-6", CFG["tasks"][0], "checker", 1, False)
    assert sb.harness_config(base, CFG)["agent"] == "simple"
    assert "agent" not in sb.harness_config(check, CFG)
    assert sb.harness_config(check, CFG)["auth"] == "token"


def test_folder_name() -> None:
    s = sb.Slot("S07", "claude-haiku-4-5", "sus-16-051_sim-T2tt_comp", "checker", 2, False)
    assert s.folder_name() == "S07_sus-16-051-T2tt_comp_haiku-4-5_checker_2"


@pytest.mark.parametrize("missing", ["tag", "schedule_seed", "usage_limits"])
def test_config_has_driver_keys(missing: str) -> None:
    assert missing in CFG
