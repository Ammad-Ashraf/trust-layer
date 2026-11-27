"""Study B launcher with a 70% five-hour usage pause (decision 0023).

Runs the same slots, in the same fixed order, through the frozen `scripts/study_b.py`. Only the
usage pause differs: it starts a run while the five-hour window is below 0.70 (config.yaml says
0.40) and the seven-day window is below 0.85. This file lives outside the frozen paths on
purpose. It never changes what a run sees or how it is scored.

Each round: probe usage (wait 15 min while busy), pick the first slot in schedule order that is
not final, then `study_b.py run <slot> --no-probe`. A void is retried only after a fresh probe.
It stops when every slot is final, a slot has 3 voids, or study_b.py exits with an error.

    systemd-run --user --unit tl-study-b --same-dir \
      --setenv=PATH="$PWD/external/collider-bench/.venv/bin:$PATH" \
      systemd-inhibit --what=sleep:idle --why="Study B" \
      /usr/bin/python3 experiments/03-study-b/usage_loop.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import study_b as sb  # noqa: E402  (frozen; only read from)

LIMITS = {"five_hour": 0.70, "seven_day": 0.85}
WAIT_S = 900


def say(msg: str) -> None:
    print(f"usage_loop: {msg}", flush=True)


def wait_for_room() -> None:
    env = {**os.environ, "CLAUDE_CODE_OAUTH_TOKEN": sb._token()}
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
        env.pop(name, None)
    cfg = {"models": {"extra_arm": "claude-haiku-4-5"}}
    while True:
        use = sb.usage_probe(env, cfg)
        busy = {k: v for k, v in use.items() if v >= LIMITS.get(k, 1.0)}
        if not busy:
            say(f"usage {use} below {LIMITS}")
            return
        say(f"usage {busy} at or above {LIMITS}; waiting {WAIT_S // 60} min")
        time.sleep(WAIT_S)


def next_slot() -> sb.Slot | None:
    for s in sb.load_schedule():
        state, voids = sb.slot_state(s)
        if state in sb.FINAL:
            continue
        if voids >= sb.MAX_VOIDS:
            say(f"{s.id} voided {voids} times; stop and report")
            sys.exit(1)
        return s
    return None


def main() -> int:
    dry = "--dry-run" in sys.argv
    while True:
        slot = next_slot()
        if slot is None:
            say("nothing left")
            return 0
        if dry:
            say(f"next would be {slot.id} ({slot.model}, {slot.task}, {slot.arm})")
            wait_for_room()
            return 0
        wait_for_room()
        cmd = [sys.executable, str(ROOT / "scripts" / "study_b.py"), "run", slot.id, "--no-probe"]
        code = subprocess.run(cmd, cwd=ROOT).returncode
        if code != 0:
            say(f"study_b.py run {slot.id} exited {code}; stop")
            return code


if __name__ == "__main__":
    sys.exit(main())
