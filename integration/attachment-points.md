# Attachment points

Mapped in the smoke run on 2026-11-18. Sources: the run record in `experiments/00-smoke-run/runs/20261118-0109_sus-16-046_baseline_1/` (`attachment-points-observed.md`), checked against the Collider-Bench code at the pinned commit `2986d8b`. Checker development starts from this map.

In this file, `<RUN>` stands for `external/collider-bench/runs/<runner>_<model>/<task>_<agent-id>/`.

## 1. Where the ledger lives

- **Agent workspace:** `<RUN>/workspace/`.
  - It is bind-mounted read-write at the same absolute path inside the container.
  - It is the agent's working directory.
  - It holds `agent_context/`, `prompt.txt`, `papers/`, `results/<template>.yaml`, `object_efficiencies/`, `bin/` and `tools/`.
- **PATH is fixed.** It is set in `agent_runtime/sandbox.py`: the `/opt/sim` dirs, `/opt/node-global/bin`, `/opt/conda/envs/lhc_analysis/bin`, then system dirs. `workspace/bin` is *not* on PATH; the agent calls tools as `bin/<tool>`.
- **How `record-quantity` reaches the agent:** through an agent folder.
  - Each script in `agents/<name>/runtime/bin/` is symlinked into `workspace/bin/` (`agent_runtime/workspace.py`, `build_workspace`).
  - `agents/<name>/runtime/` is mounted read-only (`agent_runtime/launch.py:321-323`).
  - So a `simple-ledger` agent is a copy of `simple` plus `bin/record-quantity` plus a paragraph in its `AGENTS.md`. The agent then gets `bin/record-quantity` with no image or PATH change.
  - The baseline arm keeps upstream `simple`.
  - Where the folder lives (fork vs run-time symlink) is decision [0008](../docs/decisions/0008-ledger-agent-folder.md).
- **Ledger file:** anywhere under `<RUN>/workspace/`. That path is the same inside and outside the container, so both the agent and the gate can read it.
- **Python in the image:** `pyyaml` 6.0.3 is present; **`pint` is missing**. See decision [0009](../docs/decisions/0009-pint-in-container.md).

## 2. Where the gate fires

- **Hook config:** the harness builds a fake `$HOME` at `<RUN>/.claude_home/`. It copies the host user's `~/.claude.json`, `~/.claude/.credentials.json` and `~/.claude/settings.json` into it (`agent_runtime/vendors.py:224-227`). So a Stop hook in the host user's `~/.claude/settings.json` reaches the agent.
- **Coupling problem:** this ties the subject's settings to whatever the host user has. On the runner, that leaked an MCP server and the claude.ai connectors into the subject agent. They were disabled by hand for the smoke run. See decision [0010](../docs/decisions/0010-subject-isolation.md).
- **Does a Stop hook fire?** **Yes.** Tested with the same image and binary, a throwaway `$HOME` and Haiku 4.5, for $0.03.
- **Does the rejection reach the agent?** **Yes.**
  - Exit code 2 plus stderr arrive as a user turn: `Stop hook feedback: [<hook path>]: <message>`.
  - The agent acted on it, and the second stop was allowed.
  - Gate messages must give **absolute paths**: the agent wrote the requested file next to the hook script, not in its own working directory.
- **Where hook scripts can live:** only on a mounted path, the fake home or an agent folder's `runtime/`. The rest of this repo is not mounted.
- **Not covered yet:**
  - **Tampering:** the agent runs with `--dangerously-skip-permissions` and can write to its fake home, so it could remove the hook. Write the bounce log outside the workspace, and check the settings file after each run.
  - **Extra tools:** the harness blocks only `ScheduleWakeup` (`vendors.py:217`). Newer CLI tools (RemoteTrigger, CronCreate, PushNotification, SendMessage, Workflow) are available to the agent. Whether settings deny rules still apply under `--dangerously-skip-permissions` is untested.

## 3. Where run artifacts land

- **Transcript:** `<RUN>/workspace/session.jsonl` (`launch.py:162`). It is 1.2 MB for 107 turns. Collider-Bench's CLAUDE.md says `*.stream.jsonl`, which is out of date. A second copy is in `<RUN>/.claude_home/.claude/projects/`.
- **Submitted results YAML:** `<RUN>/workspace/results/<template>.yaml`, filled in place.
- **Evaluator output:** `<RUN>/eval/score.json` and `<RUN>/eval/plots/`.
- **Run metadata:** cost and tokens in `<RUN>/run_info.json`.
- **Disk:** about 1.4 GB per run at N_gen = 10k. Nearly all of it is `workspace/sims` and `workspace/data`, which are never committed.
- **Secrets:** `<RUN>/.claude_home/` holds a copy of the OAuth credentials. It never leaves the runner.

## 4. What `bin/run-analysis` activates

- **Environment:** conda env `lhc_analysis` at `/opt/conda/envs/lhc_analysis` (Python 3.11). It is already first on PATH in the image.
- **What the script does:**
  - sources `agent_runtime/shell/agent_env.sh`;
  - sets `PYTHONPATH=<CB root>`;
  - runs `agent_runtime/preflight.py:check_analysis`;
  - then runs `timeout 14400 python analysis.py` under a `flock`.
- **In the smoke run:** the agent used it 7 times and never ran `python analysis.py` directly.
- **How our checks run:**
  - The Stop hook runs inside the container as the agent's user.
  - It calls `/opt/conda/envs/lhc_analysis/bin/python`, with `trustlayer` importable from a read-only mount.
  - The natural mount is the `simple-ledger` agent folder's `runtime/`, which is already mounted.
