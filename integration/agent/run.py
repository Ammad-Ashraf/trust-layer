#!/usr/bin/env python3
"""simple_ledger agent: upstream `simple` plus the trust-layer ledger CLI and Stop-hook gate.

Same prompt and tools as `simple` (the baseline arm). The only additions are
`bin/record-quantity`, one paragraph in AGENTS.md, and a project-level
`.claude/settings.json` in the workspace that registers the gate as a Stop hook. The
settings go into the workspace, not the host's ~/.claude, so baseline runs never get the gate.

Built by trust-layer's scripts/build_agent_folder.py; don't edit the copy in the fork.

Usage (from the Collider-Bench fork root):
    python -m agents.simple_ledger.run --task sus-16-034_sim-TChiWZ --runner claude --model ...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import agent_runtime.launch as launch
from agent_runtime.launch import launch_single_run
from agents.simple.run import build_prompt

AGENT_NAME = "simple_ledger"
GATE = Path(__file__).resolve().parent / "runtime" / "hooks" / "trustlayer-gate"


def gate_settings() -> dict[str, Any]:
    """Project settings that run the gate whenever the agent tries to stop."""
    hook = {"type": "command", "command": str(GATE), "timeout": 120}
    return {"hooks": {"Stop": [{"hooks": [hook]}]}}


def install_gate(workspace: Path) -> Path:
    """Write <workspace>/.claude/settings.json with the gate hook; return its path."""
    settings = workspace / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(gate_settings(), indent=2) + "\n")
    return settings


_upstream_build_workspace = launch.build_workspace


def _build_workspace_with_gate(*args: Any, **kwargs: Any) -> Path:
    workspace: Path = _upstream_build_workspace(*args, **kwargs)
    print(f"trust-layer gate installed: {install_gate(workspace)}")
    return workspace


def main() -> int:
    launch.build_workspace = _build_workspace_with_gate
    repo_root = Path(__file__).resolve().parents[2]
    return launch_single_run(AGENT_NAME, build_prompt, repo_root)


if __name__ == "__main__":
    sys.exit(main())
