# Runner tasks (Israr's machine)

The work queue for the runner: the Linux laptop that runs Collider-Bench. Ammad pulls the repo there and tells the runner's Claude session: **"Read `docs/runner-tasks.md` and do the open tasks."** Everything a task needs is written here; no instructions come in chat.

## How to work this queue (runner session, read first)

1. `cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer`, then `git checkout main && git pull --ff-only`. Stop and report if the pull fails.
2. Do the tasks marked **open**, in order. Skip **done** ones. Don't start a task whose "Needs" isn't met.
3. **Commit only under `experiments/*/runs/`** (CLAUDE.md, two-machine rule). Never commit code, docs, `.claude_home/`, `workspace/sims`, `workspace/data` or credentials. Never commit changes inside `external/collider-bench/`.
4. Each task ends with a `report.md` in its run folder (what ran, the numbers, anything odd, 5–10 lines), committed and pushed. The Windows session reads that report and marks the task done here. The runner never edits this file.
5. Before committing any transcript or log, scan it for secrets: `sk-ant`, `Bearer`, `oauth`, `refresh_token`, `access_token`, `api_key`, `password`. On a real secret, stop and report; don't commit.
6. If a step fails, write what failed into `report.md`, commit that, and stop. Don't improvise fixes to our code on this machine.

Paths used below: `CB=external/collider-bench`. A harness run folder is `$CB/runs/<runner>_<model>/<task>_<agent-id>/` (written `<RUN>`).

---

## R1 · Container test of the gate (M4 step 7) · **open: rerun**

- **Attempt 1 (2026-11-26, `2144354`):** ok 1–2 passed, but ok 3 failed. The cause was a bug in the test script, not the gate: `fill()` broke the template's `- {value: x}` rows, and the gate correctly rejected the file as invalid YAML. Fixed in the commit that adds this line. Rerun all of R1 in a new run folder; keep the first one.
- **Needs:** this commit or later; Podman; the image `ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3…` already pulled (it is, from the smoke run).
- **Cost:** part A free; part B a few cents (Haiku, OAuth).
- **Steps:**
  1. `python3 scripts/build_agent_folder.py`. It prints `built …/build/agent/simple_ledger`.
  2. Make the run folder: `mkdir -p experiments/04-gate-test/runs/$(date +%Y%m%d-%H%M)_container-test` (call it `$D`).
  3. Part A: `bash scripts/gate_container_test.sh 2>&1 | tee $D/container-test.txt`. Expected last line before the cleanup note: `CONTAINER TEST PASSED`.
  4. Part B, once: `bash scripts/gate_container_test.sh --claude-hook 2>&1 | tee $D/claude-hook-test.txt`. Expected: `ok 6: Claude Code fired the project Stop hook`. It uses the host's `claude` (logged in with OAuth) and `python3`. Before it, apply the smoke run's isolation: `export ENABLE_CLAUDEAI_MCP_SERVERS=false`.
  5. Copy `build/agent/simple_ledger/runtime/BUILD-INFO.yaml` into `$D/`.
  6. Write `$D/report.md`: pass/fail of ok 1–6, the Python version printed, anything odd. If ok 6 failed, include the last 40 lines of the `claude.out` file the script names.
  7. Commit `$D` ("Add M4 container gate test results") and push.

## R2 · One real checker-arm run (M4 step 8) · **open**

- **Needs:** R1 passed, including ok 6. If ok 6 failed, stop: the gate can't reach the agent this way, and the Windows side must change the design first.
- **Cost:** about $1 API-equivalent (Haiku 4.5), on the subscription.
- **Steps:**
  1. Rebuild and place the agent folder in the runner's Collider-Bench checkout. This is a temporary dirty submodule; never commit it:
     `python3 scripts/build_agent_folder.py && rm -rf $CB/agents/simple_ledger && cp -r build/agent/simple_ledger $CB/agents/`
  2. Isolation as in the smoke run: remove user-scope MCP servers for the run, and `export ENABLE_CLAUDEAI_MCP_SERVERS=false`. Restore them afterwards. (Decision 0010's dedicated user is still pending.)
  3. Run from `$CB`: `scripts/run-agent --config ../../experiments/04-gate-test/harness-config.yaml`. Note the run dir it prints (`<RUN>`).
  4. Post-run check from the repo root: `python3 scripts/postrun_check.py <RUN> $D` with `$D=experiments/04-gate-test/runs/<YYYYMMDD-HHMM>_sus-16-034_checker_1`. It copies `gate-bounces.jsonl` into `$D` and prints `bounces`, `gate_final_event`, `tampered` and `gate_error`.
  5. Copy into `$D`:
     - `<RUN>/workspace/session.jsonl` gzipped as `session.jsonl.gz`;
     - `<RUN>/workspace/ledger.yaml` (if it exists);
     - `<RUN>/workspace/results/*.yaml`;
     - `<RUN>/workspace/report.md` as `agent-report.md`;
     - `<RUN>/eval/score.json`;
     - `<RUN>/run_info.json`;
     - `experiments/04-gate-test/harness-config.yaml`.
  6. Write `$D/manifest.yaml`. Start from `python3 scripts/new_run.py 04-gate-test sus-16-034_sim-TChiWZ checker` (or copy the smoke run's manifest) and fill in every pin, with `bounces` from step 4.
  7. Write `$D/report.md`: score, cost, wall-clock, the postrun-check fields, and whether the gate fired. If it did, quote the first gate message from the transcript (`Stop hook feedback`).
  8. Clean up: `rm -rf $CB/agents/simple_ledger` (submodule clean again) and restore the MCP settings.
  9. Secret scan (rule 5), commit `$D` ("Add M4 checker-arm test run"), push.

---

## Done

(none yet)
