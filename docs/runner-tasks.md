# Runner tasks (Israr's machine)

The work queue for the runner: the Linux laptop that runs Collider-Bench. Ammad pulls the repo there and tells the runner's Claude session: **"Read `docs/runner-tasks.md` and do the open tasks."** Everything a task needs is written here; no instructions come in chat.

## How to work this queue (runner session, read first)

1. `cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer`, then `git checkout main && git pull --ff-only`. Stop and report if the pull fails.
2. Do the tasks marked **open**, in order. Skip **done** ones. Don't start a task whose "Needs" isn't met.
3. **Commit only under `experiments/*/runs/`** (CLAUDE.md, two-machine rule). Never commit code, docs, `.claude_home/`, `workspace/sims`, `workspace/data` or credentials. Never commit changes inside `external/collider-bench/`.
4. Each task ends with a `report.md` in its run folder (what ran, the numbers, anything odd, 5–10 lines), committed and pushed. The Windows session reads that report and marks the task done here. The runner never edits this file.
5. Before committing any transcript or log, scan it for secrets: `sk-ant`, `Bearer`, `oauth`, `refresh_token`, `access_token`, `api_key`, `password`. On a real secret, stop and report; don't commit.
6. If a step fails, write what failed into `report.md`, commit that, and stop. Don't improvise fixes to our code on this machine.

Machine specs: [`runner-machine.md`](runner-machine.md).

Paths used below: `CB=external/collider-bench`. A harness run folder is `$CB/runs/<runner>_<model>/<task>_<agent-id>/` (written `<RUN>`).

---

(no open tasks)

---

## Done

- **R4 · Prospino LO for Study A: done** (`c765e58`, folder `experiments/02-study-a/runs/20261127-0032_prospino-lo`), $0. Stop 800: LO 15.9 / NLO 27.2 fb; wino 550: LO 23.09 / NLO 27.55 fb. Both NLO values within 9% of the published NLO+NLL.
- **R3 · Container test of the 0017 Prospino check: passed** (`3976e9b`, folder `20261126-0145_container-test-0017`), ok 1–5 and 7, $0.
- **R2 · One real checker-arm run (M4 step 8): ran** on attempt 2 (`aa8db45`, folder `20261126-0125_sus-16-034_checker_1`). Haiku 4.5, $1.13, 0 bounces, gate passed, not tampered. Attempt 1 (`59477a5`) never launched (agent-name allow-list; fixed by `scripts/run-checker-arm`). Review: `experiments/04-gate-test/results/r2-review.md`.
- **R1 · Container test of the gate (M4 step 7): passed** on attempt 2 (`da69956`, folder `20261126-0119_container-test`), ok 1–6. Ok 6 confirms that Claude Code in `-p` mode fires a Stop hook from the workspace's `.claude/settings.json`. Attempt 1 (`2144354`) failed on a bug in the test script, fixed in `f713503`.
