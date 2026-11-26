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

### Study B, end to end (decisions 0005, 0007, 0018, 0019, 0020)

Everything runs as user `israr`, from the repo root. One script does each run: `scripts/study_b.py`. It checks the setup, waits until the Max plan's usage has room, launches the run, runs the judge and the gate check, files the results in a run folder, scans that folder for secrets, and commits and pushes it. **Don't run Study B by hand, and don't edit code here.** If the script stops with an error, write what it printed into a `report.md` (where the task says), commit, and stop.

**Keep the laptop awake:** plugged in, lid open, no suspend. Every long command below is wrapped in `systemd-inhibit` so the laptop doesn't sleep mid-run.

**The login token is a secret.** It lives in `~/.config/trust-layer/claude-oauth-token`. Never `cat`, print, copy or commit it. Check only that it exists, with `test -s`.

### R5 · Token login and one test run through `study_b.py`: **open**

**Needs:** step 1 done by a person (Israr, or Ammad with Israr's OK). It is a 2-minute browser login to **Israr's Max account**.

**Step 1 (person, in a terminal on the laptop, as `israr`):**
```bash
mkdir -p ~/.config/trust-layer && chmod 700 ~/.config/trust-layer
claude setup-token            # opens a browser: sign in with Israr's Max account, Authorize. It prints a long token.
nano ~/.config/trust-layer/claude-oauth-token     # paste the token, Ctrl+O, Enter, Ctrl+X
chmod 600 ~/.config/trust-layer/claude-oauth-token
```

**Step 2 (runner session):**
1. Update: `git checkout main && git pull --ff-only`. R2's hand copy is in the way, so: `rm -rf $CB/agents/simple_ledger && git submodule sync && git submodule update --init`. Then `git -C $CB log --oneline -1` must show `8c81028`.
2. `test -s ~/.config/trust-layer/claude-oauth-token && echo token present` (don't print the file).
3. Launch the test run detached (Haiku 4.5, checker arm, TChiWZ, about 10 min, $0 on the subscription):
   `systemd-run --user --unit tl-smoke --same-dir --setenv=PATH="$PATH" systemd-inhibit --what=sleep:idle --why="Study B smoke" python3 scripts/study_b.py smoke`
4. While it runs, keep this runner session busy with normal work: read files, run `git status`, check `journalctl --user -u tl-smoke -f`. That is exactly the case that broke the shared login before.
5. When the unit ends, the script has committed and pushed `experiments/04-gate-test/runs/<stamp>_study-b-smoke/`. Read its `manifest.yaml` and check:
   - `outcome: scored` (or `timeout`/`crash` with a reason in `launch.log`), **not** `void`;
   - `mcp_servers: []`;
   - `gate:` has `tampered: false` and `gate_error: false`;
   - `checker_time` is filled;
   - `judge_scores.json` exists.
6. Check that Israr's own login still works: `claude -p "Reply OK" --model claude-haiku-4-5`.
7. Write `report.md` in that folder (5–10 lines: the checks above, wall-clock, anything odd), then commit and push.

**Pass:** not void, `mcp_servers: []`, gate not tampered, judge ran, and Israr's own login still works.

### R6 · Study B pilot, 3 runs: **waiting** (Windows tags `study-b-v1` after reviewing R5 and marks this open)

1. `git pull --ff-only && git fetch --tags && git submodule update --init`.
2. `python3 scripts/study_b.py status`: S01–S03 are the pilot (Sonnet 4.6, no checker, one per task).
3. `systemd-run --user --unit tl-pilot --same-dir --setenv=PATH="$PATH" systemd-inhibit --what=sleep:idle --why="Study B pilot" python3 scripts/study_b.py next --pilot-only`. Each run takes 0.5–2.5 h (up to 10 h); each commits itself.
4. When the unit ends, write `experiments/03-study-b/runs/R6-pilot-report.md`: for each slot, its outcome, wall-clock hours and score, from its `manifest.yaml`. Then commit, push, and **stop**. Windows reviews the pilot before R7.

### R7 · Study B, the remaining 33 runs: **waiting** (Windows marks this open after the pilot review)

1. `git pull --ff-only && git submodule update --init`, then `python3 scripts/study_b.py status`.
2. `systemd-run --user --unit tl-study-b --same-dir --setenv=PATH="$PATH" systemd-inhibit --what=sleep:idle --why="Study B" python3 scripts/study_b.py next`. This runs S04–S36 in the fixed order of `schedule.yaml`, one at a time, about 1–3 weeks in all. Each run commits itself.
3. Check it now and then with `python3 scripts/study_b.py status` and `journalctl --user -u tl-study-b -n 50`. **Don't** start a second copy while it runs.
4. If it stops early, look at the last lines of the journal and act:
   - **A run voided 3 times** (usage limit or login): wait for the usage to reset, then start step 2 again. It resumes where it stopped.
   - **Laptop rebooted mid-run:** that run's folder has no `manifest.yaml`. Rename it by adding `_void<N>` (the next free N) and write `interrupted by reboot` into a `note.md` inside it. Commit it, then start step 2 again.
   - **"possible secret"**: stop and report. Commit nothing from that folder.
   - **Anything else:** write `experiments/03-study-b/runs/R7-report.md` with the error, commit, and stop.
5. When `status` shows every slot final (scored, timeout or crash), write `experiments/03-study-b/runs/R7-report.md`: counts per outcome per arm and model, plus total wall-clock. Commit and push.

---

## Done

- **R4 · Prospino LO for Study A: done** (`c765e58`, folder `experiments/02-study-a/runs/20261127-0032_prospino-lo`), $0. Stop 800: LO 15.9 / NLO 27.2 fb; wino 550: LO 23.09 / NLO 27.55 fb. Both NLO values within 9% of the published NLO+NLL.
- **R3 · Container test of the 0017 Prospino check: passed** (`3976e9b`, folder `20261126-0145_container-test-0017`), ok 1–5 and 7, $0.
- **R2 · One real checker-arm run (M4 step 8): ran** on attempt 2 (`aa8db45`, folder `20261126-0125_sus-16-034_checker_1`). Haiku 4.5, $1.13, 0 bounces, gate passed, not tampered. Attempt 1 (`59477a5`) never launched (agent-name allow-list; fixed by `scripts/run-checker-arm`). Review: `experiments/04-gate-test/results/r2-review.md`.
- **R1 · Container test of the gate (M4 step 7): passed** on attempt 2 (`da69956`, folder `20261126-0119_container-test`), ok 1–6. Ok 6 confirms that Claude Code in `-p` mode fires a Stop hook from the workspace's `.claude/settings.json`. Attempt 1 (`2144354`) failed on a bug in the test script, fixed in `f713503`.
