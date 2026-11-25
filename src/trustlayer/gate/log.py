"""The bounce log: one JSON line per gate decision, kept outside the agent's workspace.

Default location `$HOME/.trustlayer/bounces.jsonl` (the harness's fake home, attachment point 2);
`TRUSTLAYER_BOUNCE_LOG` overrides it. The runner copies it into the run folder after each run.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BOUNCE = "bounce"
PASS = "pass"
SUBMITTED_WITH_WARNINGS = "submitted_with_warnings"
GATE_ERROR = "gate_error"


def log_path(env: Mapping[str, str]) -> Path:
    """Where the bounce log lives for this environment."""
    explicit = env.get("TRUSTLAYER_BOUNCE_LOG")
    if explicit:
        return Path(explicit)
    home = env.get("HOME") or str(Path.home())
    return Path(home) / ".trustlayer" / "bounces.jsonl"


def count_bounces(path: Path, session_id: str) -> int:
    """How many times this session has already been sent back. Unreadable lines are skipped."""
    if not path.is_file():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(entry, dict)
            and entry.get("event") == BOUNCE
            and entry.get("session_id") == session_id
        ):
            count += 1
    return count


def append(path: Path, entry: Mapping[str, Any]) -> None:
    """Add one entry, stamped with the UTC time."""
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"time": datetime.now(UTC).isoformat(timespec="seconds"), **entry}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=False) + "\n")
