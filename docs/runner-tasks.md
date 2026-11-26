# Runner tasks (Israr's machine)

The work queue for the runner: the Linux laptop that runs Collider-Bench. Ammad pulls the repo there and tells the runner's Claude session: **"Read `docs/runner-tasks.md` and do the open tasks."** Everything a task needs is written here; no instructions come in chat.

## How to work this queue (runner session, read first)

1. `cd /home/israr/Documents/Ammad-Particle-Physics/trust-layer`, then `git checkout main && git pull --ff-only`. Stop and report if the pull fails.
2. Do the tasks marked **open**, in order. Skip **done** ones. Don't start a task whose "Needs" isn't met.
3. **Commit only under `experiments/*/runs/`** (CLAUDE.md, two-machine rule). Never commit code, docs, `.claude_home/`, `workspace/sims`, `workspace/data` or credentials. Never commit changes inside `external/collider-bench/`.
4. Each task ends with a `report.md` in its run folder (what ran, the numbers, anything odd, 5–10 lines), committed and pushed. The Windows session reads that report and marks the task done here. The runner never edits this file.
5. Before committing any transcript or log, scan it for secrets: `sk-ant`, `Bearer`, `oauth`, `refresh_token`, `access_token`, `api_key`, `password`. On a real secret, stop and report; don't commit.
6. If a step fails, write what failed into `report.md`, commit that, and stop. Don't improvise fixes to our code on this machine.

**Study B update (27 Nov, from the person at the runner):** Study B now runs entirely on this machine, so the runner session may edit docs (this file included) and fix setup problems, then document them and carry on. **Code stays frozen at `study-b-v1` until Study B is done.** A code bug is written up for the Windows session and never patched here, so every run uses the same setup (fairness). Later milestones go back to the Windows machine.

Machine specs: [`runner-machine.md`](runner-machine.md).

Paths used below: `CB=external/collider-bench`. A harness run folder is `$CB/runs/<runner>_<model>/<task>_<agent-id>/` (written `<RUN>`).

---

### Study B, end to end (decisions 0005, 0007, 0018, 0019, 0020)

**Start here:** Ammad's guide is [`study-b-start.md`](study-b-start.md). These tasks don't wait for the Windows side: each one has its own go/no-go rule, written before any run. Do them in order.

Everything runs as user `israr`, from the repo root. One script does each run: `scripts/study_b.py`. It checks the setup, waits until the Max plan's usage has room, launches the run, runs the judge and the gate check, files the results in a run folder, scans that folder for secrets, and commits and pushes it. **Don't run Study B by hand, and don't edit code here.** If the script stops with an error, write what it printed into a `report.md` (where the task says), commit, and stop.

**Keep the laptop awake:** plugged in, lid open, no suspend. Every long command below is wrapped in `systemd-inhibit` so the laptop doesn't sleep mid-run.

**The login token is a secret.** It lives in `~/.config/trust-layer/claude-oauth-token`. Never `cat`, print, copy or commit it. Check only that it exists, with `test -s`.

### R5 · Token login and one test run through `study_b.py`: **open**

**Needs:** step 1 done by a person (Ammad or Israr, with Israr's OK). It is a 2-minute browser login to **Israr's Max account**; the steps are in [`study-b-start.md`](study-b-start.md). If `~/.config/trust-layer/claude-oauth-token` is missing, ask the person to do that step, then wait.

1. Update: `git checkout main && git pull --ff-only`. R2's hand copy is in the way, so: `rm -rf $CB/agents/simple_ledger && git submodule sync && git submodule update --init`. Then `git -C $CB log --oneline -1` must show `8c81028`.
2. `test -s ~/.config/trust-layer/claude-oauth-token && echo token present` (don't print the file).
3. Launch the test run detached (Haiku 4.5, checker arm, TChiWZ, about 10 min, $0 on the subscription):
   `systemd-run --user --unit tl-smoke --same-dir --setenv=PATH="$PWD/external/collider-bench/.venv/bin:$PATH" systemd-inhibit --what=sleep:idle --why="Study B smoke" /usr/bin/python3 scripts/study_b.py smoke`
4. While it runs, keep this session busy with normal work: read files, run `git status`, follow `journalctl --user -u tl-smoke -f`. That is exactly the case that broke the shared login before.
5. When the unit ends, the script has committed and pushed `experiments/04-gate-test/runs/<stamp>_study-b-smoke/`. Read its `manifest.yaml` and check:
   - `outcome` is not `void`;
   - `mcp_servers: []`;
   - `gate:` has `tampered: false` and `gate_error: false`;
   - `checker_time` is filled;
   - `judge` has a `provenance_status`;
   - `score` is filled (or, for `timeout`/`crash`, `launch.log` shows why).
6. Check that Israr's own login still works: `claude -p "Reply OK" --model claude-haiku-4-5`.
7. Write `report.md` in that folder (5–10 lines: each check above, wall-clock, anything odd), then commit and push.
8. **Go/no-go.**
   - **Pass** (all checks in 5 and 6 hold): tag the code and go straight on to R6:
     `git tag -a study-b-v1 -m "Study B frozen setup (R5 passed)" && git push origin study-b-v1`.
   - **Fail:** stop. Say in the report what failed. Don't tag.

### R6 · Study B pilot, 3 runs: **open once R5 passes** (the tag `study-b-v1` exists)

1. `python3 scripts/study_b.py status`: S01–S03 are the pilot (Sonnet 4.6, no checker, one per task).
2. `systemd-run --user --unit tl-pilot --same-dir --setenv=PATH="$PWD/external/collider-bench/.venv/bin:$PATH" systemd-inhibit --what=sleep:idle --why="Study B pilot" /usr/bin/python3 scripts/study_b.py next --pilot-only`. Each run takes 0.5–2.5 h (up to 10 h) and commits itself.
3. When the unit ends, write `experiments/03-study-b/runs/R6-pilot-report.md`: for each slot, its outcome, wall-clock hours, Δ_norm and judge status, from its `manifest.yaml`. Then commit and push.
4. **Go/no-go (decision 0019's pilot rule):**
   - **Go** to R7 if all 3 runs are `scored` and each took under 8 h.
   - **Stop** if any run is `timeout` or `crash`, or took 8 h or more. Say why in the report. Ammad takes it to the Windows session: a crash may be a setup problem, and many long runs would change the time limit.

### R7 · Study B, the remaining 33 runs: **open once R6 says go**

1. `git pull --ff-only`, then `python3 scripts/study_b.py status`.
2. `systemd-run --user --unit tl-study-b --same-dir --setenv=PATH="$PWD/external/collider-bench/.venv/bin:$PATH" systemd-inhibit --what=sleep:idle --why="Study B" /usr/bin/python3 scripts/study_b.py next`. This runs S04–S36 in the fixed order of `schedule.yaml`, one at a time, about 1–3 weeks in all. Each run commits itself.
3. Check it now and then with `python3 scripts/study_b.py status` and `journalctl --user -u tl-study-b -n 50`. **Never start a second copy while one runs** (`systemctl --user is-active tl-study-b`).
4. If it stops early, look at the last lines of the journal and act:
   - **A run voided 3 times** (usage limit or login): wait for the usage to reset (5 h, or the weekly reset), then start step 2 again. It resumes where it stopped.
   - **"usage probe failed (check the token)":** the key may have expired or been revoked. Ask the person to redo step 1 of [`study-b-start.md`](study-b-start.md), then start step 2 again.
   - **Laptop rebooted mid-run:** that run's folder has no `manifest.yaml`. Rename it by adding `_void<N>` (the next free N), write `interrupted by reboot` into a `note.md` inside it, commit it, then start step 2 again.
   - **"possible secret":** stop and report. Commit nothing from that folder.
   - **Anything else:** write `experiments/03-study-b/runs/R7-report.md` with the error, commit, and stop.
5. When `status` shows every slot final (scored, timeout or crash), write `experiments/03-study-b/runs/R7-report.md`: counts per outcome per arm and model, plus total wall-clock. Commit and push.

### R8 · Label every run and build the results: **open once the first Study B run is committed** (do it while R7 runs)

1. For each final run folder `experiments/03-study-b/runs/S??_*` (not `*_void*`) whose `labels.yaml` has no `read: full`: use the `label-run` skill (`.claude/skills/label-run/`). Read the whole transcript; label every mistake with a sub-gap code. Commit each `labels.yaml` as you finish it, committing only that file: `git commit -m "Label Study B <slot>" -- <path>`. Then `git pull --rebase --autostash && git push`, because the run script pushes too.
   - The hand ledgers in `tasks/<task>/ledger.yaml` are the reference. Never copy them into a run folder or anywhere the agent under test can see.
   - Label without looking at the other arm's runs of the same task first, so one arm's reading doesn't colour the other's.
2. After each batch of labels, refresh the table: `PYTHONPATH=src python3 -m trustlayer.report study-b`. Commit `experiments/03-study-b/results/` (generated files only; never edit them by hand).
3. **When R7 is complete and every run is labelled:**
   - build the table once more;
   - write `experiments/03-study-b/runs/STUDY-B-DONE.md`: 5–10 plain lines with the headline numbers from `results/study-b.md` (per model: pass rate and Gap-1 errors, without vs with the checker), timeouts and voids per arm, and anything odd;
   - append one line to `lab-log.md` (date · what ran · what we learned · next step);
   - commit and push. **Study B is done.**

---

## Done

- **R4 · Prospino LO for Study A: done** (`c765e58`, folder `experiments/02-study-a/runs/20261127-0032_prospino-lo`), $0. Stop 800: LO 15.9 / NLO 27.2 fb; wino 550: LO 23.09 / NLO 27.55 fb. Both NLO values within 9% of the published NLO+NLL.
- **R3 · Container test of the 0017 Prospino check: passed** (`3976e9b`, folder `20261126-0145_container-test-0017`), ok 1–5 and 7, $0.
- **R2 · One real checker-arm run (M4 step 8): ran** on attempt 2 (`aa8db45`, folder `20261126-0125_sus-16-034_checker_1`). Haiku 4.5, $1.13, 0 bounces, gate passed, not tampered. Attempt 1 (`59477a5`) never launched (agent-name allow-list; fixed by `scripts/run-checker-arm`). Review: `experiments/04-gate-test/results/r2-review.md`.
- **R1 · Container test of the gate (M4 step 7): passed** on attempt 2 (`da69956`, folder `20261126-0119_container-test`), ok 1–6. Ok 6 confirms that Claude Code in `-p` mode fires a Stop hook from the workspace's `.claude/settings.json`. Attempt 1 (`2144354`) failed on a bug in the test script, fixed in `f713503`.
