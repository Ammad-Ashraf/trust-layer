"""Run Study B (M6) on the runner: one run at a time, each filed as a committed run folder.

Decisions: 0005 (Sonnet 4.6), 0007 (Haiku 4.5 arm), 0014 (tasks), 0018 ($0: Israr's Max
subscription on the runner laptop), 0019 (10 h limit, pilot, timeout rules), 0020 (token login).
Protocol: experiments/03-study-b/README.md. Settings: experiments/03-study-b/config.yaml.

Usage, from the repo root:
    python3 scripts/study_b.py plan                 # Windows, once: write schedule.yaml
    python3 scripts/study_b.py smoke                # runner, R5: one Haiku checker run, test folder
    python3 scripts/study_b.py status               # runner: what is done, what is next
    python3 scripts/study_b.py next --pilot-only    # runner: the 3 pilot runs, then stop
    python3 scripts/study_b.py next                 # runner: all remaining runs, in order
    python3 scripts/study_b.py run S07              # runner: one slot by id

Each run: usage probe -> launch (baseline: Collider-Bench run-agent with `agent: simple`;
checker: scripts/run-checker-arm) -> LLM judge -> post-run gate check (checker arm) -> copy
artifacts -> manifest.yaml -> secret scan -> commit and push the run folder.

Outcomes: scored | timeout | crash are final (never rerun, decision 0019). void (usage limit or
login failure, decision 0018) renames the folder to *_voidN and the slot is run again.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "03-study-b"
CONFIG = EXP / "config.yaml"
SCHEDULE = EXP / "schedule.yaml"
RUNS = EXP / "runs"
CB = Path(os.environ.get("CB", ROOT / "external" / "collider-bench"))
TOKEN_FILE = Path(
    os.environ.get("TL_TOKEN_FILE", Path.home() / ".config" / "trust-layer" / "claude-oauth-token")
)
FINAL = ("scored", "timeout", "crash")
MAX_VOIDS = 3
SECRET_PATTERNS = re.compile(
    r"sk-ant-|Bearer [A-Za-z0-9]|refresh_token\"\s*:|access_token\"\s*:|CLAUDE_CODE_OAUTH_TOKEN=\S"
)
VOID_TEXT = re.compile(
    r"usage limit|rate limit|limit reached|401|unauthori[sz]ed|authentication|invalid api key|"
    r"oauth token|please run /login",
    re.IGNORECASE,
)


class StudyBError(RuntimeError):
    """A precondition failed; nothing was launched."""


@dataclass(frozen=True)
class Slot:
    id: str
    model: str
    task: str
    arm: str
    rep: int
    pilot: bool

    def folder_name(self) -> str:
        short = self.task.split("_sim-")[0] + "-" + self.task.split("_sim-")[1]
        model = self.model.removeprefix("claude-")
        return f"{self.id}_{short}_{model}_{self.arm}_{self.rep}"


# ── schedule ────────────────────────────────────────────────────────────────


def make_schedule(cfg: dict[str, Any], seed: int) -> list[Slot]:
    """The fixed run order: the pilot, then blocks of (rep, model), shuffled within each block.

    Pilot = one baseline run of the main model per task (decision 0019). Blocking by rep keeps
    both arms and both models spread evenly over the weeks, so drift (usage, machine) hits all
    cells alike. 3 tasks x 2 arms x 2 models x 3 reps = 36 slots.
    """
    tasks: list[str] = cfg["tasks"]
    main, extra = cfg["models"]["main"], cfg["models"]["extra_arm"]
    arms: list[str] = cfg["arms"]
    rng = random.Random(seed)
    cells = [(main, t, "baseline", 1, True) for t in tasks]
    for rep in range(1, cfg["n_runs"] + 1):
        for model in (main, extra):
            block = [
                (model, t, a, rep, False)
                for t in tasks
                for a in arms
                if (model, t, a, rep, True) not in cells
            ]
            rng.shuffle(block)
            cells.extend(block)
    return [Slot(f"S{i:02d}", *cell) for i, cell in enumerate(cells, start=1)]


def load_schedule() -> list[Slot]:
    data = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    return [Slot(**s) for s in data["slots"]]


# ── outcome and timing, read from the harness run directory ────────────────


def read_events(session: Path) -> list[dict[str, Any]]:
    """Parse a stream-json transcript (one JSON object per line), skipping broken lines."""
    if not session.is_file():
        return []
    opener = gzip.open if session.suffix == ".gz" else open
    events = []
    with opener(session, "rt", encoding="utf-8") as fh:  # type: ignore[operator]
        for line in fh:
            try:
                events.append(json.loads(line))
            except ValueError:
                continue
    return events


def classify(events: list[dict[str, Any]], launch_log: str, has_score: bool) -> str:
    """Return the run outcome: void | timeout | crash | scored (decisions 0018, 0019).

    void: a usage-limit or login failure (infrastructure; rerun). timeout: the harness walltime
    watchdog fired. crash: no score for another reason. scored: everything else.
    """
    rejected = any(
        e.get("type") == "rate_limit_event"
        and (e.get("rate_limit_info") or {}).get("status") == "rejected"
        for e in events
    )
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    error_text = str(result.get("result", "")) if result and result.get("is_error") else ""
    no_start = not any(e.get("type") == "system" and e.get("subtype") == "init" for e in events)
    if rejected or VOID_TEXT.search(error_text) or (no_start and VOID_TEXT.search(launch_log)):
        return "void"
    if re.search(r"task walltime .* exceeded", launch_log):
        return "timeout"
    return "scored" if has_score else "crash"


def _ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def checker_time(
    events: list[dict[str, Any]], bounce_events: list[dict[str, Any]]
) -> dict[str, Any]:
    """Time the checker added to a run (decision 0019, rule 4).

    Sums the wall time of every `record-quantity` tool call (tool_use -> its tool_result), and
    adds the time from the first bounce to the end of the run (the agent's extra work after the
    gate sent it back).
    """
    calls: dict[str, float] = {}
    seconds = 0.0
    last_ts = None
    for e in events:
        ts = e.get("timestamp")
        if ts:
            last_ts = _ts(ts)
        content = (e.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use" and "record-quantity" in json.dumps(c.get("input")):
                if ts:
                    calls[c["id"]] = _ts(ts)
            elif c.get("type") == "tool_result" and c.get("tool_use_id") in calls and ts:
                seconds += _ts(ts) - calls[c["tool_use_id"]]
    bounces = [b for b in bounce_events if b.get("event") == "bounce" and b.get("time")]
    after_bounce = 0.0
    if bounces and last_ts is not None:
        after_bounce = max(0.0, last_ts - _ts(bounces[0]["time"]))
    return {
        "record_quantity_calls": len(calls),
        "record_quantity_seconds": round(seconds, 1),
        "after_first_bounce_seconds": round(after_bounce, 1),
        "checker_seconds": round(seconds + after_bounce, 1),
    }


def find_secrets(folder: Path, token: str) -> list[str]:
    """Files in `folder` that contain the token itself or a secret-looking string."""
    hits = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        text = gzip.decompress(raw) if path.suffix == ".gz" else raw
        body = text.decode("utf-8", errors="replace")
        if (token and token in body) or SECRET_PATTERNS.search(body):
            hits.append(str(path.relative_to(folder)))
    return hits


# ── one run ─────────────────────────────────────────────────────────────────


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _token() -> str:
    if not TOKEN_FILE.is_file():
        raise StudyBError(
            f"no login token at {TOKEN_FILE}; create it with `claude setup-token` (runner task R5)"
        )
    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not token:
        raise StudyBError(f"{TOKEN_FILE} is empty")
    return token


def preflight(cfg: dict[str, Any], frozen: bool = True) -> dict[str, str]:
    """Check the setup before any run and return the pins for the manifest.

    frozen=True (measured runs) also requires the tag and no code change since it.
    """
    cb_head = _git("-C", str(CB), "rev-parse", "HEAD")
    if cb_head != cfg["collider_bench_commit"]:
        raise StudyBError(
            f"submodule at {cb_head[:7]}, config pins {cfg['collider_bench_commit'][:7]}"
        )
    if not (CB / "agents" / "simple_ledger" / "run.py").is_file():
        raise StudyBError(
            "agents/simple_ledger missing in the submodule; git submodule update --init"
        )
    tag = cfg["tag"]
    if not frozen:
        tag = ""
    elif (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
            cwd=ROOT,
            capture_output=True,
        ).returncode
        != 0
    ):
        raise StudyBError(f"tag {tag} missing; git fetch --tags")
    changed = tag and _git(
        "diff",
        "--name-only",
        tag,
        "HEAD",
        "--",
        "src",
        "integration",
        "scripts",
        ".gitmodules",
        "experiments/03-study-b/config.yaml",
        "experiments/03-study-b/schedule.yaml",
    )
    if changed or _git("status", "--porcelain", "--", "src", "integration", "scripts"):
        raise StudyBError(f"code differs from tag {tag}; Study B code is frozen:\n{changed}")
    image = f"ghcr.io/dfaroughy/lhc-bench@{cfg['container_digest']}"
    if subprocess.run(["podman", "image", "exists", image]).returncode != 0:
        raise StudyBError(f"image missing: podman pull {image}")
    return {
        "trust_layer_commit": _git("rev-parse", "HEAD"),
        "tag": tag,
        "collider_bench_commit": cb_head,
        "container_digest": cfg["container_digest"],
    }


def usage_probe(env: dict[str, str], cfg: dict[str, Any]) -> dict[str, float]:
    """Ask Claude for one word and read the subscription's usage from its rate_limit_event.

    Raises StudyBError if the login fails (so no run is wasted on a bad token). Returns {} if
    Claude answered but reported no usage windows.
    """
    cmd = ["claude", "-p", "Reply with OK.", "--model", cfg["models"]["extra_arm"]]
    cmd += ["--output-format", "stream-json", "--verbose"]
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("study_b: usage probe timed out; going ahead without usage data", flush=True)
        return {}
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    if result is None or result.get("is_error"):
        reason = (result or {}).get("result") or proc.stderr[-300:]
        raise StudyBError(f"usage probe failed (check the token): {reason}")
    use: dict[str, float] = {}
    for e in events:
        for name, w in ((e.get("rate_limit_info") or {}).get("unifiedWindows") or {}).items():
            use[name] = max(use.get(name, 0.0), float(w.get("utilization") or 0.0))
    if not use:
        print("study_b: no usage windows reported; going ahead", flush=True)
    return use


def wait_for_usage(env: dict[str, str], cfg: dict[str, Any]) -> None:
    """Start a run only when the 5-hour and 7-day windows have room (decision 0018)."""
    limits = cfg["usage_limits"]
    while True:
        use = usage_probe(env, cfg)
        busy = {k: v for k, v in use.items() if v >= limits.get(k, 1.0)}
        if not busy:
            return
        print(f"study_b: usage {busy} at or above {limits}; waiting 30 min", flush=True)
        time.sleep(1800)


def harness_config(slot: Slot, cfg: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "task": slot.task,
        "runner": "claude",
        "auth": "token",
        "model": slot.model,
        "effort": cfg["effort"],
        "sandbox": "podman",
        "compute": "local",
    }
    if slot.arm == "baseline":
        out = {"agent": "simple", **out}
    return out


def _harness_run_dir(launch_log: str) -> Path | None:
    m = re.search(r"Setting up workspace: (\S+)", launch_log)
    return CB / "runs" / m.group(1) if m else None


def _copy_artifacts(run_dir: Path, dest: Path) -> None:
    ws = run_dir / "workspace"
    pairs = [
        (run_dir / "run_info.json", "run_info.json"),
        (run_dir / "eval" / "score.json", "score.json"),
        (run_dir / "eval" / "judge_scores.json", "judge_scores.json"),
        (run_dir / "eval" / "judge_trajectory.md", "judge_trajectory.md"),
        (ws / "report.md", "agent-report.md"),
        (ws / "analysis.py", "analysis.py"),
    ]
    pairs += [(p, p.name) for p in sorted(ws.glob("*.yaml")) if p.name != "datasets.yaml"]
    for src, name in pairs:
        if src.is_file():
            shutil.copy2(src, dest / name)
    session = ws / "session.jsonl"
    if session.is_file():
        with session.open("rb") as fh, gzip.open(dest / "session.jsonl.gz", "wb") as gz:
            shutil.copyfileobj(fh, gz)


def _run_logged(cmd: list[str], env: dict[str, str], log: Path) -> int:
    with log.open("w", encoding="utf-8") as fh:
        return subprocess.run(
            cmd, cwd=ROOT, env=env, stdout=fh, stderr=subprocess.STDOUT
        ).returncode


def run_slot(
    slot: Slot,
    cfg: dict[str, Any],
    *,
    probe: bool = True,
    push: bool = True,
    dest: Path | None = None,
    frozen: bool = True,
) -> str:
    """Run one slot end to end and return its outcome.

    dest/frozen are for the R5 smoke test only: a test folder, and no tag requirement.
    """
    pins = preflight(cfg, frozen)
    token = _token()
    env = {**os.environ, "CLAUDE_CODE_OAUTH_TOKEN": token}
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
        env.pop(name, None)
    if probe:
        wait_for_usage(env, cfg)

    dest = dest or RUNS / slot.folder_name()
    if dest.exists():
        raise StudyBError(f"{dest} exists; rename or remove it first")
    dest.mkdir(parents=True)
    hcfg = dest / "harness-config.yaml"
    hcfg.write_text(yaml.safe_dump(harness_config(slot, cfg), sort_keys=False), encoding="utf-8")

    started = datetime.now(UTC)
    launcher = (
        ["bash", str(CB / "scripts" / "run-agent"), "--config", str(hcfg)]
        if slot.arm == "baseline"
        else ["bash", str(ROOT / "scripts" / "run-checker-arm"), "--config", str(hcfg)]
    )
    print(
        f"study_b: {slot.id} {slot.model} {slot.task} {slot.arm} rep {slot.rep}: launching",
        flush=True,
    )
    exit_code = _run_logged(launcher, env, dest / "launch.log")
    launch_log = (dest / "launch.log").read_text(encoding="utf-8", errors="replace")
    run_dir = _harness_run_dir(launch_log)

    gate: dict[str, Any] = {}
    if run_dir and run_dir.is_dir():
        _run_logged(
            ["bash", str(CB / "scripts" / "launch_eval.sh"), str(run_dir), "--judge"],
            env,
            dest / "eval.log",
        )
        if slot.arm == "checker":
            sys.path.insert(0, str(ROOT / "scripts"))
            import postrun_check

            gate = postrun_check.check(run_dir, CB / "agents" / "simple_ledger")
            if gate.get("bounce_log"):
                shutil.copy2(gate["bounce_log"], dest / "gate-bounces.jsonl")
        _copy_artifacts(run_dir, dest)

    events = read_events(dest / "session.jsonl.gz")
    outcome = classify(events, launch_log, (dest / "score.json").is_file())
    manifest = build_manifest(
        slot, cfg, pins, dest, events, gate, outcome, exit_code, started, run_dir
    )
    (dest / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (dest / "labels.yaml").write_text("schema_version: 1\nlabels: []\n", encoding="utf-8")

    if outcome == "void":
        n = len(list(RUNS.glob(f"{slot.folder_name()}_void*"))) + 1
        dest = dest.rename(dest.with_name(f"{dest.name}_void{n}"))

    hits = find_secrets(dest, token)
    if hits:
        raise StudyBError(f"possible secret in {dest.name}: {hits}; not committed, stop and report")
    _git("add", str(dest.relative_to(ROOT)))
    _git(
        "commit",
        "-m",
        f"Study B {slot.id}: {slot.task} {slot.model} {slot.arm} rep {slot.rep} -> {outcome}",
    )
    if push:
        _git("pull", "--rebase", "-q")
        _git("push", "-q")
    print(f"study_b: {slot.id}: {outcome} ({dest.name})", flush=True)
    return outcome


def build_manifest(
    slot: Slot,
    cfg: dict[str, Any],
    pins: dict[str, str],
    dest: Path,
    events: list[dict[str, Any]],
    gate: dict[str, Any],
    outcome: str,
    exit_code: int,
    started: datetime,
    run_dir: Path | None,
) -> dict[str, Any]:
    """The run's manifest.yaml: every pin, the outcome, usage, score, and gate summary."""
    info: dict[str, Any] = {}
    if (dest / "run_info.json").is_file():
        info = json.loads((dest / "run_info.json").read_text(encoding="utf-8"))
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    judge: dict[str, Any] = {}
    if (dest / "judge_scores.json").is_file():
        raw = json.loads((dest / "judge_scores.json").read_text(encoding="utf-8"))
        judge = {k: v for k, v in raw.items() if not isinstance(v, (dict, list))}
    bounce_events = []
    if (dest / "gate-bounces.jsonl").is_file():
        bounce_events = [
            json.loads(x)
            for x in (dest / "gate-bounces.jsonl").read_text(encoding="utf-8").splitlines()
            if x
        ]
    wall = info.get("duration_wall_s")
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment": dest.parent.parent.name,
        "slot": asdict(slot),
        "task": slot.task,
        "arm": slot.arm,
        "model_requested": slot.model,
        "model_snapshot": init.get("model"),
        "claude_code_version": init.get("claude_code_version"),
        "auth": "token",
        "api_key_source": init.get("apiKeySource"),
        "mcp_servers": init.get("mcp_servers"),
        **pins,
        "machine": cfg["hardware"],
        "cores": os.cpu_count(),
        "walltime_limit": cfg["walltime"],
        "started_at": started.isoformat(timespec="seconds"),
        "harness_run_dir": str(run_dir.relative_to(CB)) if run_dir else None,
        "outcome": outcome,
        "exit_code": exit_code,
        "wall_clock_hours": round(wall / 3600, 3) if wall else None,
        "usage": info.get("usage"),
        "score": info.get("final_score"),
        "judge": judge or None,
        "n_gen": None,
        "notes": "",
    }
    if slot.arm == "checker":
        manifest["gate"] = {k: v for k, v in gate.items() if k != "bounce_log"} or None
        manifest["checker_time"] = checker_time(events, bounce_events)
    return manifest


# ── commands ────────────────────────────────────────────────────────────────


def slot_state(slot: Slot) -> tuple[str, int]:
    """(outcome or 'pending', number of void attempts) for a slot, from its run folders."""
    voids = len(list(RUNS.glob(f"{slot.folder_name()}_void*")))
    manifest = RUNS / slot.folder_name() / "manifest.yaml"
    if manifest.is_file():
        return str(yaml.safe_load(manifest.read_text(encoding="utf-8")).get("outcome")), voids
    return "pending", voids


def cmd_status(slots: list[Slot]) -> int:
    for s in slots:
        state, voids = slot_state(s)
        extra = f" ({voids} void)" if voids else ""
        pilot = " pilot" if s.pilot else ""
        print(f"{s.id} {s.model:18} {s.task:26} {s.arm:8} rep {s.rep}{pilot}: {state}{extra}")
    return 0


def cmd_next(
    slots: list[Slot], cfg: dict[str, Any], pilot_only: bool, count: int | None, probe: bool
) -> int:
    done = 0
    for s in slots:
        if pilot_only and not s.pilot:
            break
        state, voids = slot_state(s)
        while state not in FINAL:
            if voids >= MAX_VOIDS:
                print(f"study_b: {s.id} voided {voids} times; stop and report", file=sys.stderr)
                return 1
            state = run_slot(s, cfg, probe=probe)
            voids = slot_state(s)[1]
            done += state in FINAL
            if count is not None and done >= count:
                return 0
    print("study_b: nothing left" + (" in the pilot" if pilot_only else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    sub.add_parser("status")
    sub.add_parser("smoke")
    n = sub.add_parser("next")
    n.add_argument("--pilot-only", action="store_true")
    n.add_argument("--count", type=int)
    n.add_argument("--no-probe", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("slot")
    r.add_argument("--no-probe", action="store_true")
    args = p.parse_args(argv)

    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    try:
        if args.cmd == "plan":
            slots = make_schedule(cfg, cfg["schedule_seed"])
            SCHEDULE.write_text(
                "# Fixed Study B run order (scripts/study_b.py plan). Never edit by hand.\n"
                + yaml.safe_dump(
                    {"seed": cfg["schedule_seed"], "slots": [asdict(s) for s in slots]},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            print(f"wrote {len(slots)} slots to {SCHEDULE.relative_to(ROOT)}")
            return 0
        if args.cmd == "smoke":
            slot = Slot("T01", cfg["models"]["extra_arm"], cfg["tasks"][0], "checker", 1, False)
            stamp = datetime.now().strftime("%Y%m%d-%H%M")
            dest = ROOT / "experiments" / "04-gate-test" / "runs" / f"{stamp}_study-b-smoke"
            run_slot(slot, cfg, dest=dest, frozen=False)
            return 0
        slots = load_schedule()
        if args.cmd == "status":
            return cmd_status(slots)
        if args.cmd == "next":
            return cmd_next(slots, cfg, args.pilot_only, args.count, not args.no_probe)
        slot = next((s for s in slots if s.id == args.slot), None)
        if slot is None:
            print(f"study_b: no slot {args.slot}", file=sys.stderr)
            return 2
        run_slot(slot, cfg, probe=not args.no_probe)
        return 0
    except StudyBError as exc:
        print(f"study_b: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
