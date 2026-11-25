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

### R4 · open · Prospino LO cross sections for two Study A tasks ($0, no API)

- **Why:** Study A's "LO σ used" injections need the leading-order σ for two tasks. Right now they use a stand-in (NLO / 1.25), marked † in `experiments/02-study-a/results/study-a.md`. Prospino's own LO value replaces it.
- **Needs:** the Collider-Bench image already pulled (same digest as `scripts/gate_container_test.sh`). No API key, no agent.
- **Run folder:** `experiments/02-study-a/runs/<YYYYMMDD-HHMM>_prospino-lo/`.

Steps:
1. Read `$CB/ColliderBench/tools/CLI/PROSPINO.md` (or `bin/prospino --doc`) for the process codes, SLHA fields and `ipart` options.
2. Inside the image (`podman run --rm --network=none` with `$CB` mounted at the same path, `REPO_ROOT=$CB`, working directory a scratch folder under `/tmp`), run `$CB/ColliderBench/bin/prospino run --sqrts 13000 --order NLO` for:
   - **(a) stop pair, `tb`:** m(stop_1) = 800 GeV; stop_2, sbottoms, the other squarks and the gluino all decoupled (e.g. 5000 GeV); neutralino_1 = 400 GeV.
   - **(b) wino chargino–neutralino, `nn`:** chargino_1 and neutralino_2 both 550 GeV and pure wino, neutralino_1 = 200 GeV (bino), squarks decoupled. Compute **both** chargino_1⁺ neutralino_2 and chargino_1⁻ neutralino_2, and add them.
3. Copy into the run folder: each SLHA file you used, each `prospino.dat`, and the JSON each run printed. Don't copy the whole scratch folder.
4. `report.md`: for (a) and (b), the LO and NLO values in fb (for (b), give each charge and the sum), the K factor (NLO/LO), and how long each run took.
5. **Sanity check (write the result in the report):** Prospino's NLO should be within about 15% of the published NLO+NLL values, 28.33 fb for (a) and 30.17 fb for (b). If it's further off, say so, and say which SLHA setting you suspect. Don't retry more than twice.
6. Commit only the run folder and push.

---

## Done

- **R3 · Container test of the 0017 Prospino check: passed** (`3976e9b`, folder `20261126-0145_container-test-0017`), ok 1–5 and 7, $0.
- **R2 · One real checker-arm run (M4 step 8): ran** on attempt 2 (`aa8db45`, folder `20261126-0125_sus-16-034_checker_1`). Haiku 4.5, $1.13, 0 bounces, gate passed, not tampered. Attempt 1 (`59477a5`) never launched (agent-name allow-list; fixed by `scripts/run-checker-arm`). Review: `experiments/04-gate-test/results/r2-review.md`.
- **R1 · Container test of the gate (M4 step 7): passed** on attempt 2 (`da69956`, folder `20261126-0119_container-test`), ok 1–6. Ok 6 confirms that Claude Code in `-p` mode fires a Stop hook from the workspace's `.claude/settings.json`. Attempt 1 (`2144354`) failed on a bug in the test script, fixed in `f713503`.
