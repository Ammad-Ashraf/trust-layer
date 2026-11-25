"""The gate: a Claude Code Stop hook that runs C1-C5 when the agent tries to finish.

Exit codes follow Claude Code's hook contract: 0 lets the agent stop; 2 blocks it, and stderr
is shown to the agent as feedback. Decisions:

- every check passes                        -> exit 0, log `pass`
- some check fails, fewer than the cap so far -> exit 2 with the problems, log `bounce`
- some check fails, cap reached               -> exit 0, log `submitted_with_warnings`
- the gate itself can't run (our setup error) -> exit 0, log `gate_error`; the run is then
  marked invalid by the runner's post-run check, so the agent is never punished for our bug.

Messages use absolute paths (attachment point 2) and only the agent's own numbers. They never
mention the bounce cap, so the agent can't plan to wait the gate out.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from trustlayer.checks import (
    CheckInputs,
    CheckResult,
    InputsError,
    Submission,
    load_submission,
    load_task_context,
    prospino,
    run_checks,
)
from trustlayer.gate import log
from trustlayer.gate.config import ConfigError, load_config
from trustlayer.gate.locate import LocateError, locate
from trustlayer.ledger import Ledger, LedgerError, empty_ledger, load_ledger

CHECK_NAMES = {
    "C1": "units",
    "C2": "cross-section source",
    "C3": "complete formula",
    "C4": "matches the task",
    "C5": "results match the ledger",
}


@dataclass(frozen=True)
class Outcome:
    """What the hook returns: exit code and the text for stderr."""

    exit_code: int
    stderr: str


def _parse_hook_input(text: str) -> dict[str, object]:
    try:
        data = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _read_ledger(path: Path) -> tuple[Ledger, str | None]:
    if not path.is_file():
        return empty_ledger(), (
            f"No ledger found at {path}. Record each factor of sigma*L*BR*eps with "
            "bin/record-quantity (see agent_context/AGENTS.md)."
        )
    try:
        return load_ledger(path), None
    except LedgerError as exc:
        return empty_ledger(), f"Your ledger at {path} can't be read: {exc}"


def _read_submission(path: Path | None, error: str | None) -> tuple[Submission | None, str | None]:
    if path is None:
        return None, error
    try:
        return load_submission(path), None
    except InputsError as exc:
        return None, str(exc)


def _scratch_roots(workspace: Path, env: Mapping[str, str]) -> list[Path]:
    """Where `bin/prospino` may have written: the workspace, and the Collider-Bench root it
    `cd`s into ($REPO_ROOT, or three levels above our runtime/ folder)."""
    roots = [workspace]
    if env.get("REPO_ROOT"):
        roots.append(Path(env["REPO_ROOT"]))
    if env.get("TRUSTLAYER_RUNTIME"):
        roots.append(Path(env["TRUSTLAYER_RUNTIME"]).resolve().parents[2])
    return roots


def _run_start(workspace: Path) -> float | None:
    """When this run began: the harness writes prompt.txt just before starting the agent."""
    try:
        return (workspace / "prompt.txt").stat().st_mtime
    except OSError:
        return None


def render(
    failed: Sequence[CheckResult], preamble: str | None, ledger: Path, results: Path | None
) -> str:
    """The feedback the agent sees when the gate sends it back."""
    lines = [
        "[trust-layer checker] Your normalization record has problems. Fix them, then finish again."
    ]
    lines.append(f"Ledger:  {ledger}")
    lines.append(f"Results: {results or '(not found)'}")
    if preamble:
        lines.append(preamble)
    for r in failed:
        for message in r.messages:
            lines.append(f"- {r.check_id} ({CHECK_NAMES.get(r.check_id, r.check_id)}): {message}")
    lines.append(
        "Check your ledger with `bin/record-quantity show`. "
        "This check runs every time you try to finish."
    )
    return "\n".join(lines)


def run(hook_input: str, cwd: Path, env: Mapping[str, str]) -> Outcome:
    """Run the gate once. Pure apart from reading the inputs and appending to the bounce log."""
    data = _parse_hook_input(hook_input)
    session_id = str(data.get("session_id") or "unknown")
    workspace = Path(str(data.get("cwd") or cwd))
    log_file = log.log_path(env)
    base = {
        "session_id": session_id,
        "workspace": str(workspace),
        "stop_hook_active": bool(data.get("stop_hook_active")),
    }
    try:
        paths = locate(workspace, env)
        config = load_config(
            env.get("TRUSTLAYER_CONFIG")
            or (
                Path(env["TRUSTLAYER_RUNTIME"]) / "config.yaml"
                if env.get("TRUSTLAYER_RUNTIME")
                else None
            )
        )
        task = load_task_context(paths.task_context)
    except (LocateError, ConfigError, InputsError) as exc:
        log.append(log_file, {**base, "event": log.GATE_ERROR, "error": str(exc)})
        return Outcome(0, f"[trust-layer gate] setup error, run not blocked: {exc}")

    ledger, ledger_problem = _read_ledger(paths.ledger)
    submission, submission_error = _read_submission(paths.results, paths.results_error)
    prospino_runs = prospino.collect(
        _scratch_roots(paths.workspace, env), _run_start(paths.workspace)
    )
    inputs = CheckInputs(
        ledger=ledger,
        task=task,
        submission=submission,
        submission_error=submission_error,
        ledger_path=paths.ledger,
        c5_tolerance=config.c5_tolerance,
        prospino_results=prospino_runs,
    )
    results = run_checks(inputs)
    failed = [r for r in results if not r.passed]
    record = {
        **base,
        "task": task.task,
        "ledger": str(paths.ledger),
        "results": str(paths.results) if paths.results else None,
        "config": {
            "c5_tolerance": config.c5_tolerance,
            "max_bounces": config.max_bounces,
            "source": config.source,
        },
        "checks": [
            {"id": r.check_id, "subgap": r.subgap, "passed": r.passed, "messages": list(r.messages)}
            for r in results
        ],
        "ledger_problem": ledger_problem,
        "prospino_results": [
            {"process": r.process, "lo_pb": r.lo_pb, "nlo_pb": r.nlo_pb, "path": str(r.path)}
            for r in prospino_runs
        ],
    }
    if not failed:
        log.append(log_file, {**record, "event": log.PASS})
        return Outcome(0, "")
    bounces = log.count_bounces(log_file, session_id)
    message = render(failed, ledger_problem, paths.ledger, paths.results)
    if bounces >= config.max_bounces:
        log.append(log_file, {**record, "event": log.SUBMITTED_WITH_WARNINGS, "bounce": bounces})
        return Outcome(0, message)
    log.append(log_file, {**record, "event": log.BOUNCE, "bounce": bounces + 1})
    return Outcome(2, message)


def main(stdin: TextIO | None = None, env: Mapping[str, str] | None = None) -> int:
    """Entry point for `python -m trustlayer.gate` (the Stop hook command)."""
    stream = stdin if stdin is not None else sys.stdin
    text = "" if stream.isatty() else stream.read()
    outcome = run(text, Path.cwd(), env if env is not None else os.environ)
    if outcome.stderr:
        print(outcome.stderr, file=sys.stderr)
    return outcome.exit_code
