"""After a checker-arm run: tamper check, copy the bounce log, summarize the gate's decisions.

Run on the runner after each `simple_ledger` run (design section 5):

    python3 scripts/postrun_check.py <harness run dir> <experiments run folder>

<harness run dir> is external/collider-bench/runs/<runner>_<model>/<task>_<agent-id>/.
It checks that the workspace's .claude/settings.json still registers exactly the gate hook and
that the hook script is unchanged against the built agent folder. It then copies the bounce log
into the run folder as gate-bounces.jsonl and prints the manifest fields
(bounces, final gate event, tampered, gate_error). A run with tampered or gate_error set is
reported, but it is not valid for Study B.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

HOME_DIRS = (".claude_home", ".claude_api_home")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"


def _expected_hook(settings: Path) -> str | None:
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
        (group,) = data["hooks"]["Stop"]
        (hook,) = group["hooks"]
        command = hook["command"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if set(data) != {"hooks"} or set(data["hooks"]) != {"Stop"}:
        return None
    return command if isinstance(command, str) else None


def check(run_dir: Path, agent_folder: Path) -> dict[str, Any]:
    """Return the manifest fields for one harness run directory."""
    settings = run_dir / "workspace" / ".claude" / "settings.json"
    command = _expected_hook(settings)
    hook_ok = command is not None and Path(command).parts[-3:] == (
        "runtime",
        "hooks",
        "trustlayer-gate",
    )
    built_hook = agent_folder / "runtime" / "hooks" / "trustlayer-gate"
    script_ok = command is not None and _sha(Path(command)) == _sha(built_hook)
    log = next(
        (
            run_dir / h / ".trustlayer" / "bounces.jsonl"
            for h in HOME_DIRS
            if (run_dir / h / ".trustlayer" / "bounces.jsonl").is_file()
        ),
        None,
    )
    events = []
    if log is not None:
        events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]
    return {
        "bounces": sum(e.get("event") == "bounce" for e in events),
        "gate_final_event": events[-1]["event"] if events else None,
        "gate_error": any(e.get("event") == "gate_error" for e in events),
        "tampered": not (hook_ok and script_ok),
        "bounce_log": str(log) if log else None,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("run_dir", type=Path)
    p.add_argument("dest", type=Path, help="experiments/<exp>/runs/<run-id>/")
    p.add_argument(
        "--agent-folder",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "build" / "agent" / "simple_ledger",
    )
    args = p.parse_args(argv)
    fields = check(args.run_dir, args.agent_folder)
    if fields["bounce_log"]:
        args.dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fields["bounce_log"], args.dest / "gate-bounces.jsonl")
    print(yaml.safe_dump({k: v for k, v in fields.items() if k != "bounce_log"}, sort_keys=False))
    return 1 if fields["tampered"] or fields["gate_error"] or fields["bounce_log"] is None else 0


if __name__ == "__main__":
    sys.exit(main())
